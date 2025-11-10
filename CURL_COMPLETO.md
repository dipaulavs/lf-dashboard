# 🔌 Todos os Curls - Dashboard de Imóveis

## 🎯 ENDPOINTS TEXTO PURO (Para Innoitune)

### 1️⃣ Listar Todos os Imóveis
```bash
curl -H "Authorization: Bearer dev-token-12345" \
  "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/texto/imoveis"
```

### 2️⃣ Filtrar Imóveis por Cidade
```bash
curl -H "Authorization: Bearer dev-token-12345" \
  "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/texto/imoveis?cidade=betim"
```

### 3️⃣ Filtrar Imóveis por Tipo
```bash
curl -H "Authorization: Bearer dev-token-12345" \
  "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/texto/imoveis?tipo=casa"
```

### 4️⃣ Buscar FAQ do Imóvel 1
```bash
curl -H "Authorization: Bearer dev-token-12345" \
  "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/texto/imoveis/1/faq"
```

### 5️⃣ Buscar FAQ do Imóvel 2
```bash
curl -H "Authorization: Bearer dev-token-12345" \
  "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/texto/imoveis/2/faq"
```

### 6️⃣ Buscar Fotos do Imóvel 1
```bash
curl -H "Authorization: Bearer dev-token-12345" \
  "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/texto/imoveis/1/fotos"
```

### 7️⃣ Buscar Fotos do Imóvel 2
```bash
curl -H "Authorization: Bearer dev-token-12345" \
  "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/texto/imoveis/2/fotos"
```

---

## 📋 ENDPOINTS JSON (Para outras integrações)

### 8️⃣ Listar Imóveis (JSON)
```bash
curl -H "Authorization: Bearer dev-token-12345" \
  "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/imoveis"
```

### 9️⃣ Buscar Imóvel Específico (JSON)
```bash
curl -H "Authorization: Bearer dev-token-12345" \
  "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/imoveis/1"
```

### 🔟 FAQ do Imóvel (JSON)
```bash
curl -H "Authorization: Bearer dev-token-12345" \
  "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/imoveis/1/faq"
```

### 1️⃣1️⃣ Fotos do Imóvel (JSON)
```bash
curl -H "Authorization: Bearer dev-token-12345" \
  "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/imoveis/1/fotos"
```

### 1️⃣2️⃣ Health Check (sem autenticação)
```bash
curl "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/health"
```

---

## ✏️ CRIAR/EDITAR/DELETAR (Dashboard)

### 1️⃣3️⃣ Criar Novo Imóvel
```bash
curl -X POST "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/imoveis" \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Apartamento 2 Quartos Contagem",
    "tipo": "apartamento",
    "cidade": "Contagem",
    "area_m2": 60,
    "preco_total_min": 180000,
    "faq": "Apartamento em ótimo estado, próximo ao metrô.",
    "fotos": [
      "https://exemplo.com/foto1.jpg",
      "https://exemplo.com/foto2.jpg"
    ]
  }'
```

### 1️⃣4️⃣ Atualizar Imóvel
```bash
curl -X PUT "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/imoveis/1" \
  -H "Content-Type: application/json" \
  -d '{
    "preco_total_min": 70000,
    "status": "reservado"
  }'
```

### 1️⃣5️⃣ Deletar Imóvel
```bash
curl -X DELETE "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/imoveis/1"
```

---

## 🤖 CONFIGURAÇÃO INNOITUNE (COPIAR E COLAR)

### Ação 1: Listar Imóveis
```
Method: GET
URL: https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/texto/imoveis
Headers:
  Authorization: Bearer dev-token-12345
```

### Ação 2: Buscar FAQ
```
Method: GET
URL: https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/texto/imoveis/{id}/faq
Headers:
  Authorization: Bearer dev-token-12345
```
**Nota:** Substitua `{id}` pelo ID dinâmico do imóvel (1, 2, 3, etc)

### Ação 3: Buscar Fotos
```
Method: GET
URL: https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/texto/imoveis/{id}/fotos
Headers:
  Authorization: Bearer dev-token-12345
```
**Nota:** Substitua `{id}` pelo ID dinâmico do imóvel (1, 2, 3, etc)

---

## 📝 EXEMPLOS DE RESPOSTAS

### Listar Imóveis (Texto)
```
IMOVEIS DISPONIVEIS (2 encontrados):

ID: 1
Titulo: Chácara 1000m² Itatiaiuçu
Tipo: Chacara
Cidade: Itatiaiuçu
Area: 1000m2
Preco: R$ 65.000,00
Status: Disponivel
--------------------------------------------------

ID: 2
Titulo: casa em betim
Tipo: Casa
Cidade: betim
Preco: R$ 500.000,00
Status: Disponivel
--------------------------------------------------
```

### FAQ (Texto)
```
FAQ - casa em betim
ID: 2
==================================================

tem agua encanada e foi de leilão
```

### Fotos (Texto)
```
FOTOS - Chácara 1000m² Itatiaiuçu
ID: 1
==================================================

FOTOS (2 disponiveis):
1. https://via.placeholder.com/800x600.png?text=Foto1
2. https://via.placeholder.com/800x600.png?text=Foto2
```

---

## 🔑 INFORMAÇÕES IMPORTANTES

**Base URL:** `https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev`

**API Key:** `dev-token-12345`

**Header padrão:**
```
Authorization: Bearer dev-token-12345
```

**Endpoints principais:**
- `/api/texto/imoveis` - Lista (texto)
- `/api/texto/imoveis/{id}/faq` - FAQ (texto)
- `/api/texto/imoveis/{id}/fotos` - Fotos (texto)

---

## 🎯 TESTAR TUDO DE UMA VEZ

```bash
#!/bin/bash

API_URL="https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev"
API_KEY="dev-token-12345"

echo "1. Listar imóveis (texto)"
curl -H "Authorization: Bearer $API_KEY" "$API_URL/api/texto/imoveis"
echo -e "\n\n"

echo "2. FAQ imóvel 1 (texto)"
curl -H "Authorization: Bearer $API_KEY" "$API_URL/api/texto/imoveis/1/faq"
echo -e "\n\n"

echo "3. Fotos imóvel 1 (texto)"
curl -H "Authorization: Bearer $API_KEY" "$API_URL/api/texto/imoveis/1/fotos"
echo -e "\n\n"

echo "4. FAQ imóvel 2 (texto)"
curl -H "Authorization: Bearer $API_KEY" "$API_URL/api/texto/imoveis/2/faq"
echo -e "\n\n"

echo "5. Fotos imóvel 2 (texto)"
curl -H "Authorization: Bearer $API_KEY" "$API_URL/api/texto/imoveis/2/fotos"
echo -e "\n\n"

echo "✅ Testes concluídos!"
```

---

## ⚠️ IMPORTANTE

- **URL muda** quando reiniciar ngrok (gera novo subdomínio)
- **Sempre incluir** header `Authorization: Bearer dev-token-12345`
- **Substituir {id}** pelo número real do imóvel
- **Formato texto** = `/api/texto/` (para Innoitune)
- **Formato JSON** = `/api/` (para outras integrações)
