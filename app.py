#!/usr/bin/env python3
"""
Dashboard de Imóveis + API REST
Integração com Innoitune Agent via HTTP Request
"""

from flask import Flask, request, jsonify, send_from_directory, make_response, session, redirect, url_for, render_template_string
from flask_cors import CORS
from functools import wraps
import json
import os
import time
import secrets
from datetime import datetime, timezone, timedelta
from database import LeadsDatabase
from auth import init_oauth, login_required, admin_required, UserModel
from decorators import protect_endpoint

# Fuso horário de Brasília (UTC-3)
BRASILIA_TZ = timezone(timedelta(hours=-3))

def now_brasilia():
    """Retorna datetime atual no horário de Brasília (sem timezone para evitar conversão no frontend)"""
    # Retorna datetime "naive" no horário de Brasília (sem info de timezone)
    return datetime.now(BRASILIA_TZ).replace(tzinfo=None)

app = Flask(__name__)
CORS(app)

# Configurar secret key para sessões
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

# Configurações de sessão segura
app.config.update(
    SESSION_COOKIE_SECURE=True if os.getenv('FLASK_ENV') == 'production' else False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=86400  # 24 horas
)

# Inicializar OAuth Google
google_oauth = init_oauth(app)

# Inicializar banco de leads
db_leads = LeadsDatabase()

# Inicializar modelo de usuários
user_model = UserModel(db_leads)

# Configurações
API_KEY = os.getenv('API_KEY', 'dev-token-12345')
DATA_DIR = 'data'
INDICE_FILE = os.path.join(DATA_DIR, 'INDICE.json')
IMOVEIS_DIR = os.path.join(DATA_DIR, 'imoveis')

# Garantir que diretórios existem
os.makedirs(IMOVEIS_DIR, exist_ok=True)

# ==================== ROTAS DE AUTENTICAÇÃO OAUTH ====================

@app.route('/login')
def login():
    """Página de login - Se já logado, redireciona para dashboard"""
    # Se já está logado, vai direto para dashboard
    if 'user' in session:
        return redirect('/')

    # Mostra página de login
    return send_from_directory('static', 'login.html')


@app.route('/auth/google')
def auth_google():
    """Inicia fluxo OAuth com Google"""
    # Sempre usar HTTPS em produção
    redirect_uri = 'https://lfimoveis.loop9.com.br/authorize'
    return google_oauth.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
    """Callback do OAuth Google"""
    try:
        # Troca código por token
        token = google_oauth.authorize_access_token()

        # Pega informações do usuário
        user_info = token.get('userinfo')

        if not user_info:
            return jsonify({'error': 'Falha ao obter informações do usuário'}), 400

        # Salva usuário no banco
        resultado = user_model.criar_ou_atualizar(user_info, token)

        if not resultado['success']:
            return jsonify({'error': resultado['error']}), 500

        # Salva na sessão
        session.permanent = True
        session['user'] = {
            'id': resultado['user_id'],
            'google_id': user_info['sub'],
            'email': user_info['email'],
            'name': user_info.get('name', ''),
            'picture': user_info.get('picture', ''),
            'approved': resultado.get('approved', False),
            'is_admin': resultado.get('is_admin', False)
        }

        # Redireciona para dashboard (decorator vai verificar aprovação)
        return redirect('/')

    except Exception as e:
        return jsonify({'error': f'Erro na autenticação: {str(e)}'}), 500


@app.route('/logout')
def logout():
    """Faz logout do usuário"""
    session.pop('user', None)
    return redirect('/login')


@app.route('/api/user')
def api_user():
    """Retorna dados do usuário logado (sem @login_required para aguardando aprovação)"""
    if 'user' not in session:
        return jsonify({'success': False, 'error': 'Não autenticado'}), 401

    return jsonify({
        'success': True,
        'user': session.get('user')
    })


@app.route('/aguardando-aprovacao')
def aguardando_aprovacao():
    """Página de espera para usuários não aprovados"""
    # Se não está logado, redireciona para login
    if 'user' not in session:
        return redirect('/login')

    # Se está aprovado, redireciona para dashboard
    if session['user'].get('approved'):
        return redirect('/')

    # Mostra página de espera
    return send_from_directory('static', 'aguardando-aprovacao.html')


# ==================== AUTENTICAÇÃO API ====================

def require_api_key(f):
    """Decorator para validar API Key"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'success': False, 'error': 'API Key não fornecida'}), 401

        try:
            token = auth_header.split('Bearer ')[1]
            if token != API_KEY:
                return jsonify({'success': False, 'error': 'API Key inválida'}), 401
        except:
            return jsonify({'success': False, 'error': 'Formato de Authorization inválido'}), 401

        return f(*args, **kwargs)
    return decorated_function

# ==================== HELPERS ====================

def ler_indice():
    """Lê o arquivo INDICE.json"""
    if not os.path.exists(INDICE_FILE):
        return {
            'versao': '1.0',
            'total_imoveis': 0,
            'imoveis': []
        }

    with open(INDICE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_indice(dados):
    """Salva o arquivo INDICE.json"""
    with open(INDICE_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def gerar_slug(titulo):
    """Gera slug a partir do título"""
    import re
    slug = titulo.lower()
    slug = re.sub(r'[áàãâä]', 'a', slug)
    slug = re.sub(r'[éèêë]', 'e', slug)
    slug = re.sub(r'[íìîï]', 'i', slug)
    slug = re.sub(r'[óòõôö]', 'o', slug)
    slug = re.sub(r'[úùûü]', 'u', slug)
    slug = re.sub(r'[ç]', 'c', slug)
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug

def proximo_id():
    """Retorna o próximo ID disponível"""
    indice = ler_indice()
    if not indice['imoveis']:
        return 1
    return max(imovel['id'] for imovel in indice['imoveis']) + 1

# ==================== ROTAS FRONTEND ====================

@app.route('/')
@login_required
def index():
    """Servir dashboard HTML com cache busting (requer autenticação)"""
    # Ler HTML
    with open('static/index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # Injetar timestamp dinâmico nos scripts
    timestamp = str(int(time.time()))
    html = html.replace('agenda.js?v=1762739999', f'agenda.js?v={timestamp}')
    html = html.replace('leads_v2.js?v=1762738405', f'leads_v2.js?v={timestamp}')

    # Retornar com headers anti-cache
    response = make_response(html)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/static/<path:path>')
def static_files(path):
    """Servir arquivos estáticos"""
    return send_from_directory('static', path)

# ==================== API ENDPOINTS ====================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check (sem autenticação)"""
    return jsonify({
        'success': True,
        'status': 'online',
        'timestamp': now_brasilia().isoformat()
    })

# ==================== ENDPOINTS TEXTO PURO (para Innoitune) ====================

@app.route('/api/texto/imoveis', methods=['GET'])
@require_api_key
def listar_imoveis_texto():
    """Lista imóveis em formato JSON estruturado"""
    indice = ler_indice()

    # Filtros opcionais
    cidade = request.args.get('cidade')
    tipo = request.args.get('tipo')
    status_filter = request.args.get('status', 'disponivel')

    imoveis = indice['imoveis']

    # Aplicar filtros
    if cidade:
        imoveis = [i for i in imoveis if i.get('cidade', '').lower() == cidade.lower()]
    if tipo:
        imoveis = [i for i in imoveis if i.get('tipo', '').lower() == tipo.lower()]
    if status_filter:
        imoveis = [i for i in imoveis if i.get('status', 'disponivel').lower() == status_filter.lower()]

    # Retornar JSON estruturado
    resultado = {
        'total': len(imoveis),
        'imoveis': []
    }

    for imovel in imoveis:
        item = {
            'id': imovel['id'],
            'titulo': imovel['titulo'],
            'tipo': imovel['tipo'],
            'cidade': imovel['cidade'],
            'area_m2': imovel.get('area_m2'),
            'preco': imovel.get('preco_total_min'),
            'status': imovel['status']
        }
        resultado['imoveis'].append(item)

    return jsonify(resultado)

@app.route('/api/texto/faq', methods=['GET'])
@require_api_key
def buscar_faq_por_parametro():
    """Busca FAQ usando ID como parâmetro (para IA preencher automaticamente)"""
    imovel_id = request.args.get('id')

    if not imovel_id:
        return "Parametro 'id' obrigatorio. Exemplo: /api/texto/faq?id=1", 400, {'Content-Type': 'text/plain; charset=utf-8'}

    try:
        imovel_id = int(imovel_id)
    except:
        return "Parametro 'id' deve ser um numero.", 400, {'Content-Type': 'text/plain; charset=utf-8'}

    indice = ler_indice()

    imovel = next((i for i in indice['imoveis'] if i['id'] == imovel_id), None)

    if not imovel:
        return "Imovel nao encontrado.", 404, {'Content-Type': 'text/plain; charset=utf-8'}

    # Ler arquivo FAQ.txt
    faq_path = os.path.join(IMOVEIS_DIR, imovel['slug'], 'FAQ.txt')

    if not os.path.exists(faq_path):
        faq_content = 'FAQ nao disponivel'
    else:
        with open(faq_path, 'r', encoding='utf-8') as f:
            faq_content = f.read()

    # Ler arquivo links.json para pegar fotos
    links_path = os.path.join(IMOVEIS_DIR, imovel['slug'], 'links.json')

    if not os.path.exists(links_path):
        links_data = {'fotos': [], 'video_tour': None, 'planta_baixa': None}
    else:
        with open(links_path, 'r', encoding='utf-8') as f:
            links_data = json.load(f)

    fotos = links_data.get('fotos', [])
    video_tour = links_data.get('video_tour')
    planta_baixa = links_data.get('planta_baixa')

    # Montar resposta JSON estruturada
    resultado = {
        'id': imovel_id,
        'titulo': imovel['titulo'],
        'tipo': imovel['tipo'],
        'cidade': imovel['cidade'],
        'area_m2': imovel.get('area_m2'),
        'preco': imovel.get('preco_total_min'),
        'status': imovel['status'],
        'informacoes': faq_content,
        'fotos': fotos,
        'video_tour': video_tour,
        'planta_baixa': planta_baixa
    }

    return jsonify(resultado)

@app.route('/api/texto/imoveis/<int:imovel_id>/faq', methods=['GET'])
@require_api_key
def buscar_faq_texto(imovel_id):
    """Busca FAQ completo (informações + fotos) em formato texto puro - URL antiga mantida"""
    indice = ler_indice()

    imovel = next((i for i in indice['imoveis'] if i['id'] == imovel_id), None)

    if not imovel:
        return "Imovel nao encontrado.", 404, {'Content-Type': 'text/plain; charset=utf-8'}

    # Ler arquivo FAQ.txt
    faq_path = os.path.join(IMOVEIS_DIR, imovel['slug'], 'FAQ.txt')

    if not os.path.exists(faq_path):
        faq_content = 'FAQ nao disponivel'
    else:
        with open(faq_path, 'r', encoding='utf-8') as f:
            faq_content = f.read()

    # Ler arquivo links.json para pegar fotos
    links_path = os.path.join(IMOVEIS_DIR, imovel['slug'], 'links.json')

    if not os.path.exists(links_path):
        links_data = {'fotos': [], 'video_tour': None, 'planta_baixa': None}
    else:
        with open(links_path, 'r', encoding='utf-8') as f:
            links_data = json.load(f)

    fotos = links_data.get('fotos', [])
    video_tour = links_data.get('video_tour')
    planta_baixa = links_data.get('planta_baixa')

    # Montar resposta completa
    texto = f"FAQ - {imovel['titulo']}\n"
    texto += f"ID: {imovel_id}\n"
    texto += "=" * 50 + "\n\n"
    texto += faq_content
    texto += "\n\n" + "=" * 50 + "\n"
    texto += "LINKS E FOTOS\n"
    texto += "=" * 50 + "\n\n"

    if fotos:
        texto += f"FOTOS ({len(fotos)} disponiveis):\n"
        for i, url in enumerate(fotos, 1):
            texto += f"{i}. {url}\n"
    else:
        texto += "Nenhuma foto disponivel.\n"

    if video_tour:
        texto += f"\nVIDEO TOUR:\n{video_tour}\n"

    if planta_baixa:
        texto += f"\nPLANTA BAIXA:\n{planta_baixa}\n"

    return texto, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/api/texto/imoveis/<int:imovel_id>/fotos', methods=['GET'])
@require_api_key
def buscar_fotos_texto(imovel_id):
    """Busca URLs de fotos em formato texto puro"""
    indice = ler_indice()

    imovel = next((i for i in indice['imoveis'] if i['id'] == imovel_id), None)

    if not imovel:
        return "Imovel nao encontrado.", 404, {'Content-Type': 'text/plain; charset=utf-8'}

    # Ler arquivo links.json
    links_path = os.path.join(IMOVEIS_DIR, imovel['slug'], 'links.json')

    if not os.path.exists(links_path):
        links_data = {'fotos': [], 'video_tour': None, 'planta_baixa': None}
    else:
        with open(links_path, 'r', encoding='utf-8') as f:
            links_data = json.load(f)

    fotos = links_data.get('fotos', [])
    video_tour = links_data.get('video_tour')
    planta_baixa = links_data.get('planta_baixa')

    texto = f"FOTOS - {imovel['titulo']}\n"
    texto += f"ID: {imovel_id}\n"
    texto += "=" * 50 + "\n\n"

    if fotos:
        texto += f"FOTOS ({len(fotos)} disponiveis):\n"
        for i, url in enumerate(fotos, 1):
            texto += f"{i}. {url}\n"
    else:
        texto += "Nenhuma foto disponivel.\n"

    if video_tour:
        texto += f"\nVIDEO TOUR:\n{video_tour}\n"

    if planta_baixa:
        texto += f"\nPLANTA BAIXA:\n{planta_baixa}\n"

    return texto, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/api/imoveis', methods=['GET'])
@require_api_key
def listar_imoveis():
    """Lista todos os imóveis"""
    indice = ler_indice()

    # Filtros opcionais
    cidade = request.args.get('cidade')
    tipo = request.args.get('tipo')
    status = request.args.get('status', 'disponivel')
    formato = request.args.get('formato', 'json')  # json ou texto

    imoveis = indice['imoveis']

    # Aplicar filtros
    if cidade:
        imoveis = [i for i in imoveis if i.get('cidade', '').lower() == cidade.lower()]
    if tipo:
        imoveis = [i for i in imoveis if i.get('tipo', '').lower() == tipo.lower()]
    if status:
        imoveis = [i for i in imoveis if i.get('status', 'disponivel').lower() == status.lower()]

    # Retornar em formato texto para agentes IA
    if formato == 'texto':
        if not imoveis:
            return "Nenhum imóvel encontrado.", 200, {'Content-Type': 'text/plain; charset=utf-8'}

        texto = f"IMÓVEIS DISPONÍVEIS ({len(imoveis)} encontrados):\n\n"
        for imovel in imoveis:
            texto += f"ID: {imovel['id']}\n"
            texto += f"Título: {imovel['titulo']}\n"
            texto += f"Tipo: {imovel['tipo'].capitalize()}\n"
            texto += f"Cidade: {imovel['cidade']}\n"
            if imovel.get('area_m2'):
                texto += f"Área: {imovel['area_m2']}m²\n"
            if imovel.get('preco_total_min'):
                preco = f"R$ {imovel['preco_total_min']:,.2f}".replace(',', '.')
                texto += f"Preço: {preco}\n"
            texto += f"Status: {imovel['status'].capitalize()}\n"
            texto += "-" * 50 + "\n\n"

        return texto, 200, {'Content-Type': 'text/plain; charset=utf-8'}

    # Retorno JSON padrão
    return jsonify({
        'success': True,
        'total': len(imoveis),
        'imoveis': imoveis if imoveis else [],
        'mensagem': 'Nenhum imóvel encontrado' if not imoveis else f'{len(imoveis)} imóveis encontrados'
    })

@app.route('/api/imoveis/<int:imovel_id>', methods=['GET'])
@require_api_key
def buscar_imovel(imovel_id):
    """Busca um imóvel por ID"""
    indice = ler_indice()

    imovel = next((i for i in indice['imoveis'] if i['id'] == imovel_id), None)

    if not imovel:
        return jsonify({'success': False, 'error': 'Imóvel não encontrado'}), 404

    return jsonify({
        'success': True,
        'imovel': imovel
    })

@app.route('/api/imoveis/<int:imovel_id>/faq', methods=['GET'])
@require_api_key
def buscar_faq(imovel_id):
    """Busca FAQ de um imóvel"""
    indice = ler_indice()
    formato = request.args.get('formato', 'json')

    imovel = next((i for i in indice['imoveis'] if i['id'] == imovel_id), None)

    if not imovel:
        if formato == 'texto':
            return "Imóvel não encontrado.", 404, {'Content-Type': 'text/plain; charset=utf-8'}
        return jsonify({'success': False, 'error': 'Imóvel não encontrado'}), 404

    # Ler arquivo FAQ.txt
    faq_path = os.path.join(IMOVEIS_DIR, imovel['slug'], 'FAQ.txt')

    if not os.path.exists(faq_path):
        faq_content = 'FAQ não disponível'
    else:
        with open(faq_path, 'r', encoding='utf-8') as f:
            faq_content = f.read()

    # Retornar em formato texto
    if formato == 'texto':
        texto = f"FAQ - {imovel['titulo']}\n"
        texto += f"ID: {imovel_id}\n"
        texto += "=" * 50 + "\n\n"
        texto += faq_content
        return texto, 200, {'Content-Type': 'text/plain; charset=utf-8'}

    # Retorno JSON padrão
    return jsonify({
        'success': True,
        'imovel_id': imovel_id,
        'slug': imovel['slug'],
        'faq': faq_content
    })

@app.route('/api/imoveis/<int:imovel_id>/fotos', methods=['GET'])
@require_api_key
def buscar_fotos(imovel_id):
    """Busca URLs das fotos de um imóvel"""
    indice = ler_indice()
    formato = request.args.get('formato', 'json')

    imovel = next((i for i in indice['imoveis'] if i['id'] == imovel_id), None)

    if not imovel:
        if formato == 'texto':
            return "Imóvel não encontrado.", 404, {'Content-Type': 'text/plain; charset=utf-8'}
        return jsonify({'success': False, 'error': 'Imóvel não encontrado'}), 404

    # Ler arquivo links.json
    links_path = os.path.join(IMOVEIS_DIR, imovel['slug'], 'links.json')

    if not os.path.exists(links_path):
        links_data = {'fotos': [], 'video_tour': None, 'planta_baixa': None}
    else:
        with open(links_path, 'r', encoding='utf-8') as f:
            links_data = json.load(f)

    fotos = links_data.get('fotos', [])
    video_tour = links_data.get('video_tour')
    planta_baixa = links_data.get('planta_baixa')

    # Retornar em formato texto
    if formato == 'texto':
        texto = f"FOTOS - {imovel['titulo']}\n"
        texto += f"ID: {imovel_id}\n"
        texto += "=" * 50 + "\n\n"

        if fotos:
            texto += f"FOTOS ({len(fotos)} disponíveis):\n"
            for i, url in enumerate(fotos, 1):
                texto += f"{i}. {url}\n"
        else:
            texto += "Nenhuma foto disponível.\n"

        if video_tour:
            texto += f"\nVÍDEO TOUR:\n{video_tour}\n"

        if planta_baixa:
            texto += f"\nPLANTA BAIXA:\n{planta_baixa}\n"

        return texto, 200, {'Content-Type': 'text/plain; charset=utf-8'}

    # Retorno JSON padrão
    return jsonify({
        'success': True,
        'imovel_id': imovel_id,
        'slug': imovel['slug'],
        'fotos': fotos,
        'video_tour': video_tour,
        'planta_baixa': planta_baixa
    })

@app.route('/api/imoveis', methods=['POST'])
def criar_imovel():
    """Cria um novo imóvel (sem autenticação para o dashboard)"""
    dados = request.json

    # Validações
    if not dados.get('titulo'):
        return jsonify({'success': False, 'error': 'Título é obrigatório'}), 400

    indice = ler_indice()

    # Gerar slug
    slug_base = dados.get('slug') or gerar_slug(dados['titulo'])
    slug = f"{slug_base}-{proximo_id():03d}"

    # Criar novo imóvel
    novo_imovel = {
        'id': proximo_id(),
        'slug': slug,
        'tipo': dados.get('tipo', 'casa'),
        'titulo': dados['titulo'],
        'cidade': dados.get('cidade', ''),
        'area_m2': dados.get('area_m2', 0),
        'preco_total_min': dados.get('preco_total_min', 0),
        'status': dados.get('status', 'disponivel'),
        'criado_em': now_brasilia().isoformat()
    }

    # Adicionar ao índice
    indice['imoveis'].append(novo_imovel)
    indice['total_imoveis'] = len(indice['imoveis'])
    salvar_indice(indice)

    # Criar pasta do imóvel
    imovel_dir = os.path.join(IMOVEIS_DIR, slug)
    os.makedirs(imovel_dir, exist_ok=True)

    # Salvar FAQ
    faq_path = os.path.join(imovel_dir, 'FAQ.txt')
    with open(faq_path, 'w', encoding='utf-8') as f:
        f.write(dados.get('faq', f"FAQ do imóvel {dados['titulo']}\n\nEm construção..."))

    # Salvar links
    links_path = os.path.join(imovel_dir, 'links.json')
    links_data = {
        'fotos': dados.get('fotos', []),
        'video_tour': dados.get('video_tour'),
        'planta_baixa': dados.get('planta_baixa')
    }
    with open(links_path, 'w', encoding='utf-8') as f:
        json.dump(links_data, f, ensure_ascii=False, indent=2)

    return jsonify({
        'success': True,
        'imovel_id': novo_imovel['id'],
        'slug': slug,
        'message': 'Imóvel criado com sucesso'
    }), 201

@app.route('/api/imoveis/<int:imovel_id>', methods=['PUT'])
def atualizar_imovel(imovel_id):
    """Atualiza um imóvel existente"""
    dados = request.json
    indice = ler_indice()

    imovel = next((i for i in indice['imoveis'] if i['id'] == imovel_id), None)

    if not imovel:
        return jsonify({'success': False, 'error': 'Imóvel não encontrado'}), 404

    # Atualizar campos do índice
    campos_atualizaveis = ['tipo', 'titulo', 'cidade', 'area_m2', 'preco_total_min', 'status']
    for campo in campos_atualizaveis:
        if campo in dados:
            imovel[campo] = dados[campo]

    imovel['atualizado_em'] = now_brasilia().isoformat()
    salvar_indice(indice)

    # Atualizar FAQ se fornecido
    if 'faq' in dados:
        faq_path = os.path.join(IMOVEIS_DIR, imovel['slug'], 'FAQ.txt')
        with open(faq_path, 'w', encoding='utf-8') as f:
            f.write(dados['faq'])

    # Atualizar links se fornecidos
    if any(k in dados for k in ['fotos', 'video_tour', 'planta_baixa']):
        links_path = os.path.join(IMOVEIS_DIR, imovel['slug'], 'links.json')

        # Ler links existentes
        if os.path.exists(links_path):
            with open(links_path, 'r', encoding='utf-8') as f:
                links_data = json.load(f)
        else:
            links_data = {}

        # Atualizar campos
        if 'fotos' in dados:
            links_data['fotos'] = dados['fotos']
        if 'video_tour' in dados:
            links_data['video_tour'] = dados['video_tour']
        if 'planta_baixa' in dados:
            links_data['planta_baixa'] = dados['planta_baixa']

        # Salvar
        with open(links_path, 'w', encoding='utf-8') as f:
            json.dump(links_data, f, ensure_ascii=False, indent=2)

    return jsonify({
        'success': True,
        'imovel_id': imovel_id,
        'message': 'Imóvel atualizado com sucesso'
    })

@app.route('/api/imoveis/<int:imovel_id>', methods=['DELETE'])
def deletar_imovel(imovel_id):
    """Deleta um imóvel"""
    indice = ler_indice()

    imovel = next((i for i in indice['imoveis'] if i['id'] == imovel_id), None)

    if not imovel:
        return jsonify({'success': False, 'error': 'Imóvel não encontrado'}), 404

    # Remover do índice
    indice['imoveis'] = [i for i in indice['imoveis'] if i['id'] != imovel_id]
    indice['total_imoveis'] = len(indice['imoveis'])
    salvar_indice(indice)

    # Opcionalmente, deletar pasta (comentado por segurança)
    # import shutil
    # imovel_dir = os.path.join(IMOVEIS_DIR, imovel['slug'])
    # if os.path.exists(imovel_dir):
    #     shutil.rmtree(imovel_dir)

    return jsonify({
        'success': True,
        'message': 'Imóvel deletado com sucesso'
    })

# ==================== ENDPOINTS DE LEADS ====================

@app.route('/api/leads/score', methods=['GET'])
@require_api_key
@protect_endpoint(
    max_requests=10,  # 10 req/s por IP
    window_seconds=1,
    dedup_window=5,  # Bloqueia duplicatas em 5s
    dedup_params=['whatsapp', 'score']  # Considera whatsapp+score para dedup
)
def atualizar_score():
    """
    ENDPOINT 1: Atualizar apenas o SCORE do lead

    Uso: /api/leads/score?whatsapp=5531999887766&nome=João Silva&imovel_id=4&score=45

    Query params:
        - whatsapp: Número WhatsApp (obrigatório)
        - nome: Nome do lead (obrigatório)
        - imovel_id: ID do imóvel (obrigatório)
        - score: Score do lead 0-100 (obrigatório)

    Protection:
        - Rate limit: 10 req/s por IP
        - Deduplication: 5s window (whatsapp+score)
        - Retry on lock: 3 tentativas com backoff exponencial
    """
    whatsapp = request.args.get('whatsapp')
    nome = request.args.get('nome')
    imovel_id = request.args.get('imovel_id')
    score = request.args.get('score')

    # Validações com orientações para o agente
    if not whatsapp or not nome or not imovel_id or not score:
        dados_faltantes = []
        acoes_sugeridas = []

        if not nome:
            dados_faltantes.append('nome')
            acoes_sugeridas.append('Pergunte: "Qual é o seu nome completo?"')

        if not imovel_id:
            dados_faltantes.append('imovel_id')
            acoes_sugeridas.append('Use a ferramenta "buscar imoveis" para listar os imóveis disponíveis e identifique qual imóvel o cliente tem interesse')

        if not score:
            dados_faltantes.append('score')

        return jsonify({
            'success': False,
            'error': 'Dados insuficientes para atualizar score',
            'dados_faltantes': dados_faltantes,
            'instrucao_agente': 'Você precisa coletar mais informações do cliente antes de atualizar o score',
            'acoes_necessarias': acoes_sugeridas,
            'proximo_passo': 'Após coletar nome e identificar o imóvel de interesse, chame novamente esta ferramenta com todos os parâmetros'
        }), 200

    # Validar score
    try:
        score = int(score)
        if score < 0 or score > 100:
            raise ValueError("Score deve estar entre 0 e 100")
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Score inválido: {str(e)}'
        }), 400

    # Validar imovel_id
    try:
        imovel_id = int(imovel_id)
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'imovel_id deve ser um número'
        }), 400

    # Limpar whatsapp
    whatsapp = str(whatsapp).replace('+', '').replace(' ', '').replace('-', '')

    # Buscar lead existente
    lead_existente = db_leads.buscar_lead(whatsapp)

    # Registrar/atualizar mantendo outros dados
    resultado = db_leads.registrar_lead(
        whatsapp=whatsapp,
        nome=nome,
        imovel_id=imovel_id,
        score=score,
        agendou_visita=lead_existente.get('agendou_visita', False) if lead_existente else False
    )

    return jsonify(resultado), 200

@app.route('/api/leads/imovel', methods=['GET'])
@require_api_key
@protect_endpoint(
    max_requests=10,  # 10 req/s por IP
    window_seconds=1,
    dedup_window=5,  # Bloqueia duplicatas em 5s
    dedup_params=['whatsapp', 'imovel_id']  # Considera whatsapp+imovel_id para dedup
)
def definir_imovel():
    """
    ENDPOINT 2: Definir qual IMÓVEL o lead tem interesse

    Uso: /api/leads/imovel?whatsapp=5531999887766&nome=João Silva&imovel_id=1

    Query params:
        - whatsapp: Número WhatsApp (obrigatório)
        - nome: Nome do lead (obrigatório)
        - imovel_id: ID do imóvel (obrigatório)

    Protection:
        - Rate limit: 10 req/s por IP
        - Deduplication: 5s window (whatsapp+imovel_id)
        - Retry on lock: 3 tentativas com backoff exponencial
    """
    whatsapp = request.args.get('whatsapp')
    nome = request.args.get('nome')
    imovel_id = request.args.get('imovel_id')

    # Validações com orientações para o agente
    if not whatsapp or not nome or not imovel_id:
        dados_faltantes = []
        acoes_sugeridas = []

        if not nome:
            dados_faltantes.append('nome')
            acoes_sugeridas.append('Pergunte ao cliente: "Qual é o seu nome completo?"')

        if not imovel_id:
            dados_faltantes.append('imovel_id')
            acoes_sugeridas.append('Use a ferramenta "buscar imoveis" (sara imoveis ou lcj) para listar os imóveis disponíveis e identifique qual imóvel o cliente mencionou ou demonstrou interesse')

        return jsonify({
            'success': False,
            'error': 'Dados insuficientes para registrar interesse no imóvel',
            'dados_faltantes': dados_faltantes,
            'instrucao_agente': 'Você precisa coletar o nome do cliente e identificar em qual imóvel ele está interessado',
            'acoes_necessarias': acoes_sugeridas,
            'proximo_passo': 'Após coletar nome e identificar o ID do imóvel, chame novamente esta ferramenta'
        }), 200

    try:
        imovel_id = int(imovel_id)
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'imovel_id deve ser um número'
        }), 400

    # Limpar whatsapp
    whatsapp = str(whatsapp).replace('+', '').replace(' ', '').replace('-', '')

    # Buscar lead existente
    lead_existente = db_leads.buscar_lead(whatsapp)

    # Registrar/atualizar mantendo outros dados
    resultado = db_leads.registrar_lead(
        whatsapp=whatsapp,
        nome=nome,
        imovel_id=imovel_id,
        score=lead_existente.get('score', 0) if lead_existente else 0,
        agendou_visita=lead_existente.get('agendou_visita', False) if lead_existente else False
    )

    return jsonify(resultado), 200

@app.route('/api/leads/agendar', methods=['GET'])
@require_api_key
def marcar_agendamento():
    """
    ENDPOINT 3: Marcar que lead AGENDOU VISITA

    Uso: /api/leads/agendar?whatsapp=5531999887766&nome=João Silva&agendou=true

    Query params:
        - whatsapp: Número WhatsApp (obrigatório)
        - nome: Nome do lead (obrigatório)
        - agendou: true/false (obrigatório)
    """
    whatsapp = request.args.get('whatsapp')
    nome = request.args.get('nome')
    agendou = request.args.get('agendou', 'false').lower() == 'true'

    # Validações
    if not whatsapp or not nome:
        return jsonify({
            'success': False,
            'error': 'Parâmetros obrigatórios: whatsapp, nome, agendou'
        }), 400

    # Limpar whatsapp
    whatsapp = str(whatsapp).replace('+', '').replace(' ', '').replace('-', '')

    # Buscar lead existente
    lead_existente = db_leads.buscar_lead(whatsapp)

    # Registrar/atualizar mantendo outros dados
    resultado = db_leads.registrar_lead(
        whatsapp=whatsapp,
        nome=nome,
        imovel_id=lead_existente.get('imovel_id') if lead_existente else None,
        score=lead_existente.get('score', 0) if lead_existente else 0,
        agendou_visita=agendou
    )

    return jsonify(resultado), 200

@app.route('/api/leads/tag', methods=['GET'])
@require_api_key
def taguear_lead_get():
    """
    ENDPOINT COMPLETO (LEGADO): Atualizar tudo de uma vez

    Uso: /api/leads/tag?whatsapp=5531999887766&nome=João Silva&imovel_id=1&score=45&agendou_visita=true

    Query params:
        - whatsapp: Número WhatsApp (obrigatório)
        - nome: Nome do lead (obrigatório)
        - imovel_id: ID do imóvel de interesse (opcional)
        - score: Score do lead 0-100 (obrigatório)
        - agendou_visita: true/false (opcional, padrão: false)

    Exemplo completo:
    /api/leads/tag?whatsapp=5531999887766&nome=João%20Silva&imovel_id=1&score=45&agendou_visita=true
    """
    # Extrair parâmetros
    whatsapp = request.args.get('whatsapp')
    nome = request.args.get('nome')
    score = request.args.get('score')
    imovel_id = request.args.get('imovel_id')
    agendou_visita = request.args.get('agendou_visita', 'false').lower() == 'true'

    # Validações
    if not whatsapp:
        return jsonify({
            'success': False,
            'error': 'Parâmetro "whatsapp" é obrigatório'
        }), 400

    if not nome:
        return jsonify({
            'success': False,
            'error': 'Parâmetro "nome" é obrigatório'
        }), 400

    if not score:
        return jsonify({
            'success': False,
            'error': 'Parâmetro "score" é obrigatório'
        }), 400

    try:
        score = int(score)
        if score < 0 or score > 100:
            raise ValueError("Score deve estar entre 0 e 100")
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Score inválido: {str(e)}'
        }), 400

    # Converter imovel_id se fornecido
    if imovel_id:
        try:
            imovel_id = int(imovel_id)
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'imovel_id deve ser um número'
            }), 400

    # Limpar whatsapp (remover + e espaços)
    whatsapp = str(whatsapp).replace('+', '').replace(' ', '').replace('-', '')

    # Registrar no banco
    resultado = db_leads.registrar_lead(
        whatsapp=whatsapp,
        nome=nome,
        imovel_id=imovel_id,
        score=score,
        agendou_visita=agendou_visita
    )

    if not resultado['success']:
        return jsonify(resultado), 400

    return jsonify(resultado), 201 if resultado['acao'] == 'created' else 200

@app.route('/api/leads/registrar', methods=['POST'])
@require_api_key
def registrar_lead():
    """
    Registra ou atualiza lead (usado pelo agente IA via ferramenta)

    Body JSON:
    {
        "whatsapp": "5531999887766",
        "nome": "João Silva",
        "imovel_id": 1,
        "score": 45,
        "agendou_visita": true
    }
    """
    dados = request.json

    # Validações
    campos_obrigatorios = ['whatsapp', 'nome', 'score']
    for campo in campos_obrigatorios:
        if campo not in dados:
            return jsonify({
                'success': False,
                'error': f'Campo "{campo}" é obrigatório'
            }), 400

    # Limpar whatsapp (remover + e espaços)
    whatsapp = str(dados['whatsapp']).replace('+', '').replace(' ', '').replace('-', '')

    # Registrar no banco
    resultado = db_leads.registrar_lead(
        whatsapp=whatsapp,
        nome=dados['nome'],
        imovel_id=dados.get('imovel_id'),
        score=dados['score'],
        agendou_visita=dados.get('agendou_visita', False)
    )

    if not resultado['success']:
        return jsonify(resultado), 400

    return jsonify(resultado), 201 if resultado['acao'] == 'created' else 200

@app.route('/api/leads', methods=['GET'])
@require_api_key
def listar_leads():
    """
    Lista leads com filtros opcionais

    Query params:
        - score_min: Score mínimo (ex: 31)
        - score_max: Score máximo (ex: 60)
        - imovel_id: Filtrar por imóvel
        - agendou_visita: true/false
    """
    filtros = {}

    # Extrair filtros dos query params
    if request.args.get('score_min'):
        filtros['score_min'] = int(request.args.get('score_min'))
    if request.args.get('score_max'):
        filtros['score_max'] = int(request.args.get('score_max'))
    if request.args.get('imovel_id'):
        filtros['imovel_id'] = int(request.args.get('imovel_id'))
    if request.args.get('agendou_visita'):
        filtros['agendou_visita'] = request.args.get('agendou_visita').lower() == 'true'

    leads = db_leads.listar_leads(filtros)

    return jsonify({
        'success': True,
        'total': len(leads),
        'filtros_aplicados': filtros,
        'leads': leads
    })

@app.route('/api/leads/<whatsapp>', methods=['GET'])
@require_api_key
def buscar_lead(whatsapp):
    """Busca lead específico com histórico de score"""
    whatsapp = whatsapp.replace('+', '').replace(' ', '').replace('-', '')

    lead = db_leads.buscar_lead(whatsapp)

    if not lead:
        return jsonify({
            'success': False,
            'error': 'Lead não encontrado'
        }), 404

    # Adicionar histórico
    historico = db_leads.obter_historico(whatsapp)

    return jsonify({
        'success': True,
        'lead': lead,
        'historico': historico
    })

@app.route('/api/leads/<whatsapp>', methods=['DELETE'])
@require_api_key
def deletar_lead_route(whatsapp):
    """Deleta um lead"""
    whatsapp = whatsapp.replace('+', '').replace(' ', '').replace('-', '')
    resultado = db_leads.deletar_lead(whatsapp)

    if not resultado['success']:
        return jsonify(resultado), 404

    return jsonify(resultado)

@app.route('/api/leads/export', methods=['GET'])
@require_api_key
def exportar_leads():
    """
    Exporta leads em formato CSV

    Query params: mesmos de /api/leads
    """
    filtros = {}

    if request.args.get('score_min'):
        filtros['score_min'] = int(request.args.get('score_min'))
    if request.args.get('score_max'):
        filtros['score_max'] = int(request.args.get('score_max'))
    if request.args.get('imovel_id'):
        filtros['imovel_id'] = int(request.args.get('imovel_id'))
    if request.args.get('agendou_visita'):
        filtros['agendou_visita'] = request.args.get('agendou_visita').lower() == 'true'

    leads = db_leads.listar_leads(filtros)

    # Gerar CSV
    csv = "Nome,WhatsApp,Score,Imóvel ID,Agendou Visita,Criado Em\n"
    for lead in leads:
        csv += f"{lead['nome']},{lead['whatsapp']},{lead['score']},"
        csv += f"{lead.get('imovel_id', '')},{lead['agendou_visita']},{lead['criado_em']}\n"

    return csv, 200, {
        'Content-Type': 'text/csv; charset=utf-8',
        'Content-Disposition': f'attachment; filename=leads_{now_brasilia().strftime("%Y%m%d")}.csv'
    }

@app.route('/api/estatisticas', methods=['GET'])
@require_api_key
def estatisticas():
    """Retorna estatísticas agregadas para gráficos"""
    stats = db_leads.obter_estatisticas()

    return jsonify({
        'success': True,
        'estatisticas': stats
    })

# ==================== ENDPOINTS DE AGENDA ====================

@app.route('/api/agenda/agendamentos', methods=['GET'])
def listar_agendamentos():
    """Lista agendamentos com filtros opcionais"""
    filtros = {}

    if request.args.get('status'):
        filtros['status'] = request.args.get('status')
    if request.args.get('data_inicio'):
        filtros['data_inicio'] = request.args.get('data_inicio')
    if request.args.get('data_fim'):
        filtros['data_fim'] = request.args.get('data_fim')
    if request.args.get('imovel_id'):
        filtros['imovel_id'] = int(request.args.get('imovel_id'))

    agendamentos = db_leads.listar_agendamentos(filtros)

    return jsonify({
        'success': True,
        'total': len(agendamentos),
        'agendamentos': agendamentos
    })

@app.route('/api/agenda/agendamentos', methods=['POST'])
def criar_agendamento():
    """Cria novo agendamento"""
    dados = request.json

    # Validações
    campos_obrigatorios = ['nome_cliente', 'whatsapp', 'imovel_id', 'data_visita', 'hora_visita']
    for campo in campos_obrigatorios:
        if campo not in dados:
            return jsonify({
                'success': False,
                'error': f'Campo "{campo}" é obrigatório'
            }), 400

    resultado = db_leads.criar_agendamento(
        nome_cliente=dados['nome_cliente'],
        whatsapp=dados['whatsapp'],
        imovel_id=dados['imovel_id'],
        data_visita=dados['data_visita'],
        hora_visita=dados['hora_visita'],
        observacoes=dados.get('observacoes'),
        status=dados.get('status', 'agendado')
    )

    if not resultado['success']:
        return jsonify(resultado), 400

    return jsonify(resultado), 201

@app.route('/api/agenda/agendamentos/<int:agendamento_id>', methods=['PUT'])
def atualizar_agendamento_route(agendamento_id):
    """Atualiza agendamento existente"""
    dados = request.json
    resultado = db_leads.atualizar_agendamento(agendamento_id, dados)

    if not resultado['success']:
        return jsonify(resultado), 400

    return jsonify(resultado)

@app.route('/api/agenda/agendamentos/<int:agendamento_id>', methods=['DELETE'])
def deletar_agendamento_route(agendamento_id):
    """Deleta agendamento"""
    resultado = db_leads.deletar_agendamento(agendamento_id)

    if not resultado['success']:
        return jsonify(resultado), 404

    return jsonify(resultado)

@app.route('/api/agenda/estatisticas', methods=['GET'])
def estatisticas_agenda():
    """Retorna estatísticas da agenda"""
    stats = db_leads.obter_estatisticas_agenda()

    return jsonify({
        'success': True,
        'estatisticas': stats
    })

@app.route('/api/agenda/observacoes', methods=['GET'])
def obter_observacoes():
    """Obtém observações da agenda"""
    observacoes = db_leads.obter_configuracao('agenda_observacoes')

    return jsonify({
        'success': True,
        'observacoes': observacoes or ''
    })

@app.route('/api/agenda/observacoes', methods=['POST'])
def salvar_observacoes():
    """Salva observações da agenda"""
    dados = request.json

    if 'observacoes' not in dados:
        return jsonify({
            'success': False,
            'error': 'Campo "observacoes" é obrigatório'
        }), 400

    resultado = db_leads.salvar_configuracao('agenda_observacoes', dados['observacoes'])

    return jsonify(resultado)

# ==================== ENDPOINTS ADMIN ====================

@app.route('/api/admin/usuarios', methods=['GET'])
@admin_required
def listar_todos_usuarios():
    """Lista todos os usuários (somente admin)"""
    usuarios = user_model.listar_todos()

    return jsonify({
        'success': True,
        'usuarios': usuarios
    })


@app.route('/api/admin/usuarios/pendentes', methods=['GET'])
@admin_required
def listar_usuarios_pendentes():
    """Lista usuários aguardando aprovação (somente admin)"""
    usuarios = user_model.listar_pendentes()

    return jsonify({
        'success': True,
        'usuarios': usuarios
    })


@app.route('/api/admin/usuarios/<int:user_id>/aprovar', methods=['POST'])
@admin_required
def aprovar_usuario(user_id):
    """Aprova um usuário (somente admin)"""
    resultado = user_model.aprovar_usuario(user_id)

    if not resultado['success']:
        return jsonify(resultado), 404

    return jsonify(resultado)


@app.route('/api/admin/usuarios/<int:user_id>/revogar', methods=['POST'])
@admin_required
def revogar_usuario(user_id):
    """Revoga aprovação de um usuário (somente admin)"""
    resultado = user_model.revogar_usuario(user_id)

    if not resultado['success']:
        return jsonify(resultado), 404

    return jsonify(resultado)

# ==================== ENDPOINTS PARA AGENTE IA ====================

@app.route('/api/agente/consultar-agenda', methods=['GET'])
@require_api_key
def consultar_agenda_agente():
    """
    ENDPOINT 1 (AGENTE IA): Consultar agenda disponível

    Uso: GET /api/agente/consultar-agenda?data=2025-01-15

    Query params:
        - data: Data para consultar (YYYY-MM-DD) - opcional (padrão: hoje)
        - dias: Quantos dias à frente consultar (padrão: 7)

    Retorna: Lista de horários agendados + observações/regras
    """
    from datetime import datetime, timedelta

    # Parâmetros
    data_param = request.args.get('data')
    dias = int(request.args.get('dias', 7))

    # Data inicial
    if data_param:
        try:
            data_inicio = datetime.strptime(data_param, '%Y-%m-%d').date()
        except:
            return jsonify({
                'success': False,
                'error': 'Formato de data inválido. Use YYYY-MM-DD'
            }), 400
    else:
        data_inicio = now_brasilia().date()

    # Data final
    data_fim = data_inicio + timedelta(days=dias)

    # Buscar agendamentos no período
    filtros = {
        'data_inicio': data_inicio.isoformat(),
        'data_fim': data_fim.isoformat()
    }

    agendamentos = db_leads.listar_agendamentos(filtros)

    # Buscar observações/regras
    observacoes = db_leads.obter_configuracao('agenda_observacoes') or 'Nenhuma regra configurada'

    # Organizar por data
    agenda_por_data = {}
    for agendamento in agendamentos:
        data = agendamento['data_visita']
        if data not in agenda_por_data:
            agenda_por_data[data] = []

        agenda_por_data[data].append({
            'hora': agendamento['hora_visita'],
            'cliente': agendamento['nome_cliente'],
            'imovel_id': agendamento['imovel_id'],
            'status': agendamento['status']
        })

    # Resposta formatada para IA
    return jsonify({
        'success': True,
        'periodo': {
            'inicio': data_inicio.isoformat(),
            'fim': data_fim.isoformat(),
            'dias': dias
        },
        'regras_agendamento': observacoes,
        'total_agendamentos': len(agendamentos),
        'agenda': agenda_por_data,
        'mensagem': f'Agenda consultada de {data_inicio.strftime("%d/%m/%Y")} até {data_fim.strftime("%d/%m/%Y")}'
    })

@app.route('/api/agente/agendar-visita', methods=['POST'])
@require_api_key
def agendar_visita_agente():
    """
    ENDPOINT 2 (AGENTE IA): Agendar visita automaticamente

    Body JSON:
    {
        "nome_cliente": "João Silva",
        "whatsapp": "5531999887766",
        "imovel_id": 1,
        "data_visita": "2025-01-15",
        "hora_visita": "14:00",
        "observacoes": "Cliente preferiu horário da tarde"
    }

    Retorna: Confirmação do agendamento
    """
    dados = request.json

    # Validações
    campos_obrigatorios = ['nome_cliente', 'whatsapp', 'imovel_id', 'data_visita', 'hora_visita']
    for campo in campos_obrigatorios:
        if campo not in dados:
            return jsonify({
                'success': False,
                'error': f'Campo "{campo}" é obrigatório'
            }), 400

    # Limpar whatsapp
    whatsapp = str(dados['whatsapp']).replace('+', '').replace(' ', '').replace('-', '')

    # Criar agendamento (sem validar imóvel)
    resultado = db_leads.criar_agendamento(
        nome_cliente=dados['nome_cliente'],
        whatsapp=whatsapp,
        imovel_id=dados['imovel_id'],
        data_visita=dados['data_visita'],
        hora_visita=dados['hora_visita'],
        observacoes=dados.get('observacoes'),
        status='agendado'
    )

    if not resultado['success']:
        return jsonify(resultado), 400

    # Atualizar lead (marcar agendou_visita=True)
    db_leads.registrar_lead(
        whatsapp=whatsapp,
        nome=dados['nome_cliente'],
        imovel_id=dados['imovel_id'],
        score=90,  # Score alto pois agendou visita
        agendou_visita=True
    )

    # Resposta formatada
    from datetime import datetime
    data_obj = datetime.strptime(dados['data_visita'], '%Y-%m-%d')
    data_formatada = data_obj.strftime('%d/%m/%Y')

    return jsonify({
        'success': True,
        'agendamento_id': resultado['agendamento_id'],
        'mensagem': f'Visita agendada com sucesso para {data_formatada} às {dados["hora_visita"]}',
        'detalhes': {
            'cliente': dados['nome_cliente'],
            'whatsapp': whatsapp,
            'imovel_id': dados['imovel_id'],
            'data': data_formatada,
            'hora': dados['hora_visita']
        }
    }), 201

# ==================== RUN ====================

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5555))
    print("🚀 Dashboard de Imóveis - API REST")
    print(f"📁 Dados em: {os.path.abspath(DATA_DIR)}")
    print(f"🔑 API Key: {API_KEY}")
    print(f"🌐 Porta: {port}")
    print("=" * 60)
    app.run(host='0.0.0.0', port=port, debug=True)
