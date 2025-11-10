"""
Decoradores de autenticação
"""
from functools import wraps
from flask import session, redirect, url_for, jsonify, request

def login_required(f):
    """
    Decorator para proteger rotas que requerem autenticação E aprovação

    Usage:
        @app.route('/dashboard')
        @login_required
        def dashboard():
            return render_template('dashboard.html')
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verifica se usuário está na sessão
        if 'user' not in session:
            # Se for requisição API, retorna JSON
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Não autenticado'}), 401

            # Se for página web, redireciona para login
            return redirect(url_for('login'))

        # Verifica se usuário foi aprovado
        user = session['user']
        if not user.get('approved'):
            # Se for API, retorna erro
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Usuário aguardando aprovação do administrador'}), 403

            # Se for web, redireciona para página de espera
            return redirect(url_for('aguardando_aprovacao'))

        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """
    Decorator para rotas que requerem permissão de admin

    Usage:
        @app.route('/admin')
        @admin_required
        def admin_panel():
            return render_template('admin.html')
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            # Se for API, retorna JSON
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Não autenticado'}), 401
            return redirect(url_for('login'))

        # Verifica se usuário é admin
        user = session['user']
        if not user.get('is_admin'):
            # Se for API, retorna JSON
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Permissão negada - apenas administradores'}), 403
            return redirect(url_for('index'))

        return f(*args, **kwargs)

    return decorated_function
