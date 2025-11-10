#!/bin/bash

API_URL="https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev"
API_KEY="dev-token-12345"

echo "🧪 Testando API Dashboard de Imóveis"
echo "======================================"

echo ""
echo "1️⃣ Criando imóvel de teste..."
curl -s -X POST "$API_URL/api/imoveis" \
  -H "Content-Type: application/json" \
  -d '{"titulo":"Chácara 1000m² Itatiaiuçu","tipo":"chacara","cidade":"Itatiaiuçu","area_m2":1000,"preco_total_min":65000,"faq":"Chácara maravilhosa com 1000m², localizada em Itatiaiuçu.","fotos":["https://via.placeholder.com/800x600.png?text=Foto1","https://via.placeholder.com/800x600.png?text=Foto2"]}' | python3 -m json.tool

echo ""
echo "2️⃣ Listando imóveis..."
curl -s -H "Authorization: Bearer $API_KEY" "$API_URL/api/imoveis" | python3 -m json.tool

echo ""
echo "3️⃣ Buscando FAQ do imóvel 1..."
curl -s -H "Authorization: Bearer $API_KEY" "$API_URL/api/imoveis/1/faq" | python3 -m json.tool

echo ""
echo "4️⃣ Buscando fotos do imóvel 1..."
curl -s -H "Authorization: Bearer $API_KEY" "$API_URL/api/imoveis/1/fotos" | python3 -m json.tool

echo ""
echo "✅ Testes concluídos!"
