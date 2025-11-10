# 🔌 Exemplos de Curl para Innoitune

Base URL: `https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev`
API Key: `dev-token-12345`

---

## 1️⃣ Listar Todos os Imóveis

```bash
curl -X GET \
  -H "Authorization: Bearer dev-token-12345" \
  "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/imoveis"
```

**Resposta:**
```json
{
  "success": true,
  "total": 2,
  "imoveis": [
    {
      "id": 1,
      "slug": "chacara-1000m-itatiaiucu-001",
      "titulo": "Chácara 1000m² Itatiaiuçu",
      "tipo": "chacara",
      "cidade": "Itatiaiuçu",
      "area_m2": 1000,
      "preco_total_min": 65000,
      "status": "disponivel"
    }
  ]
}
```

---

## 2️⃣ Filtrar Imóveis por Cidade

```bash
curl -X GET \
  -H "Authorization: Bearer dev-token-12345" \
  "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/imoveis?cidade=Betim"
```

---

## 3️⃣ Filtrar Imóveis por Tipo

```bash
curl -X GET \
  -H "Authorization: Bearer dev-token-12345" \
  "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/imoveis?tipo=casa"
```

---

## 4️⃣ Buscar Detalhes de um Imóvel Específico

```bash
curl -X GET \
  -H "Authorization: Bearer dev-token-12345" \
  "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/imoveis/1"
```

**Resposta:**
```json
{
  "success": true,
  "imovel": {
    "id": 1,
    "slug": "chacara-1000m-itatiaiucu-001",
    "titulo": "Chácara 1000m² Itatiaiuçu",
    "tipo": "chacara",
    "cidade": "Itatiaiuçu",
    "area_m2": 1000,
    "preco_total_min": 65000,
    "status": "disponivel"
  }
}
```

---

## 5️⃣ Buscar FAQ de um Imóvel

```bash
curl -X GET \
  -H "Authorization: Bearer dev-token-12345" \
  "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/imoveis/1/faq"
```

**Resposta:**
```json
{
  "success": true,
  "imovel_id": 1,
  "slug": "chacara-1000m-itatiaiucu-001",
  "faq": "Chácara maravilhosa com 1000m², localizada em Itatiaiuçu..."
}
```

---

## 6️⃣ Buscar Fotos de um Imóvel

```bash
curl -X GET \
  -H "Authorization: Bearer dev-token-12345" \
  "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/imoveis/1/fotos"
```

**Resposta:**
```json
{
  "success": true,
  "imovel_id": 1,
  "slug": "chacara-1000m-itatiaiucu-001",
  "fotos": [
    "https://via.placeholder.com/800x600.png?text=Foto1",
    "https://via.placeholder.com/800x600.png?text=Foto2"
  ],
  "video_tour": "https://youtube.com/watch?v=exemplo",
  "planta_baixa": null
}
```

---

## 7️⃣ Health Check (sem autenticação)

```bash
curl -X GET \
  "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/health"
```

**Resposta:**
```json
{
  "success": true,
  "status": "online",
  "timestamp": "2025-11-09T20:45:00.123456"
}
```

---

## 🎯 Para Copiar Direto no Innoitune

### **Ação 1: Listar Imóveis**
```
Method: GET
URL: https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/imoveis
Headers:
  Authorization: Bearer dev-token-12345
```

### **Ação 2: Buscar FAQ**
```
Method: GET
URL: https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/imoveis/{id}/faq
Headers:
  Authorization: Bearer dev-token-12345
```
*Substitua `{id}` pelo ID do imóvel (ex: 1, 2, 3)*

### **Ação 3: Buscar Fotos**
```
Method: GET
URL: https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/imoveis/{id}/fotos
Headers:
  Authorization: Bearer dev-token-12345
```
*Substitua `{id}` pelo ID do imóvel (ex: 1, 2, 3)*

---

## 📋 Testando com Curl

```bash
# Copie e cole no terminal para testar

# 1. Listar imóveis
curl -H "Authorization: Bearer dev-token-12345" \
  "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/imoveis"

# 2. FAQ do imóvel 1
curl -H "Authorization: Bearer dev-token-12345" \
  "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/imoveis/1/faq"

# 3. Fotos do imóvel 1
curl -H "Authorization: Bearer dev-token-12345" \
  "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/imoveis/1/fotos"
```

---

## ⚠️ Importante

- **Sempre incluir o header:** `Authorization: Bearer dev-token-12345`
- **Substituir `{id}`** pelo número real do imóvel (1, 2, 3, etc)
- **URL muda** quando reiniciar o ngrok (gera novo subdomínio)
