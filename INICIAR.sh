#!/bin/bash

echo "🚀 Iniciando Dashboard de Imóveis + Ngrok"
echo "=========================================="

# Diretório do projeto
cd "$(dirname "$0")"

# Verificar se venv existe
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar venv
source venv/bin/activate

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -q -r requirements.txt

# Matar processos anteriores
echo "🧹 Limpando processos anteriores..."
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "ngrok" 2>/dev/null || true

# Iniciar Flask em background
echo "🌐 Iniciando Flask API na porta 5555..."
export FLASK_APP=app.py
export API_KEY=dev-token-12345
export FLASK_PORT=5555
python3 app.py > flask.log 2>&1 &
FLASK_PID=$!

echo "⏳ Aguardando Flask iniciar..."
sleep 3

# Verificar se Flask está rodando
if ! ps -p $FLASK_PID > /dev/null; then
    echo "❌ Erro ao iniciar Flask!"
    cat flask.log
    exit 1
fi

# Iniciar ngrok
echo "🌍 Iniciando ngrok..."
ngrok http 5555 > /dev/null &
NGROK_PID=$!

echo "⏳ Aguardando ngrok iniciar..."
sleep 3

# Pegar URL pública do ngrok
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"https://[^"]*' | grep -o 'https://[^"]*' | head -1)

if [ -z "$NGROK_URL" ]; then
    echo "❌ Erro ao obter URL do ngrok!"
    kill $FLASK_PID $NGROK_PID 2>/dev/null
    exit 1
fi

echo ""
echo "✅ Dashboard rodando com sucesso!"
echo "=========================================="
echo "📊 Dashboard Web: $NGROK_URL"
echo "🔌 API REST: $NGROK_URL/api/imoveis"
echo "🔑 API Key: dev-token-12345"
echo ""
echo "📝 Endpoints disponíveis:"
echo "  GET  $NGROK_URL/api/imoveis"
echo "  GET  $NGROK_URL/api/imoveis/{id}"
echo "  GET  $NGROK_URL/api/imoveis/{id}/faq"
echo "  GET  $NGROK_URL/api/imoveis/{id}/fotos"
echo "  POST $NGROK_URL/api/imoveis"
echo "  PUT  $NGROK_URL/api/imoveis/{id}"
echo "  DELETE $NGROK_URL/api/imoveis/{id}"
echo ""
echo "🤖 Configuração Innoitune:"
echo "  URL: $NGROK_URL/api/imoveis"
echo "  Header: Authorization: Bearer dev-token-12345"
echo ""
echo "=========================================="
echo "📋 Logs em tempo real:"
echo ""

# Seguir logs
tail -f flask.log
