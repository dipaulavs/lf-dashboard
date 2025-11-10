#!/bin/bash

# Script de teste rápido para endpoints da agenda
# Uso: ./TEST_AGENDA.sh

BASE_URL="http://localhost:5555"
API_KEY="dev-token-12345"

echo "🧪 TESTANDO ENDPOINTS DA AGENDA"
echo "================================"
echo ""

# Teste 1: Consultar agenda
echo "1️⃣ Consultando agenda (próximos 7 dias)..."
curl -X GET "${BASE_URL}/api/agente/consultar-agenda" \
  -H "Authorization: Bearer ${API_KEY}" \
  -s | python3 -m json.tool

echo ""
echo ""

# Teste 2: Salvar observações
echo "2️⃣ Salvando observações..."
curl -X POST "${BASE_URL}/api/agenda/observacoes" \
  -H "Content-Type: application/json" \
  -d '{"observacoes":"Horários disponíveis: 09:00-12:00 e 14:00-18:00. Sábados só manhã."}' \
  -s | python3 -m json.tool

echo ""
echo ""

# Teste 3: Criar agendamento
echo "3️⃣ Criando agendamento de teste..."
curl -X POST "${BASE_URL}/api/agente/agendar-visita" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "nome_cliente": "Teste Cliente",
    "whatsapp": "5531999999999",
    "imovel_id": 1,
    "data_visita": "2025-11-15",
    "hora_visita": "10:00",
    "observacoes": "Teste automático via curl"
  }' \
  -s | python3 -m json.tool

echo ""
echo ""

# Teste 4: Consultar agenda novamente
echo "4️⃣ Consultando agenda novamente (deve mostrar o agendamento)..."
curl -X GET "${BASE_URL}/api/agente/consultar-agenda?data=2025-11-15&dias=1" \
  -H "Authorization: Bearer ${API_KEY}" \
  -s | python3 -m json.tool

echo ""
echo ""
echo "✅ Testes concluídos!"
