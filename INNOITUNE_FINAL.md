# 🤖 Configuração Final Innoitune - 2 Endpoints Apenas

## ✅ SOLUÇÃO SIMPLIFICADA

Apenas **2 endpoints** necessários:
1. **Listar imóveis disponíveis**
2. **FAQ completo** (informações + fotos + links)

---

## 1️⃣ LISTAR IMÓVEIS DISPONÍVEIS

**URL:**
```
https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/texto/imoveis
```

**Method:** GET

**Headers:**
```
Authorization: Bearer dev-token-12345
```

**Resposta:**
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

---

## 2️⃣ FAQ COMPLETO (Informações + Fotos)

### **NOVO FORMATO: ID como parâmetro separado**

**URL:**
```
https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/texto/faq?id={ID}
```

**Method:** GET

**Headers:**
```
Authorization: Bearer dev-token-12345
```

**Como usar:**
- A IA preenche o `{ID}` automaticamente
- O ID fica **separado da URL**, como parâmetro
- Exemplo: `?id=1` ou `?id=2`

**Resposta Completa:**
```
FAQ - Chácara 1000m² Itatiaiuçu
ID: 1
==================================================

Chácara maravilhosa com 1000m², localizada em Itatiaiuçu.

==================================================
LINKS E FOTOS
==================================================

FOTOS (2 disponiveis):
1. https://via.placeholder.com/800x600.png?text=Foto1
2. https://via.placeholder.com/800x600.png?text=Foto2
```

---

## 🔧 Configuração no Innoitune

### **Ação 1: Listar Imóveis**
```
Nome: Listar Imóveis
Method: GET
URL: https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/texto/imoveis
Headers: Authorization: Bearer dev-token-12345
```

### **Ação 2: FAQ Completo**
```
Nome: Buscar FAQ Imóvel
Method: GET
URL: https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/texto/faq
Parâmetro: id (preenchido pela IA)
Headers: Authorization: Bearer dev-token-12345
```

**Configurar campo dinâmico:**
- Criar variável `id` que a IA preenche
- URL final fica: `/api/texto/faq?id={valor_preenchido_pela_ia}`

---

## 🎯 Fluxo de Conversa

```
👤 Cliente: "Quais imóveis você tem?"
    ↓
🤖 Innoitune: GET /api/texto/imoveis
    ↓
🤖 Innoitune: "Temos 2 imóveis:
              1. Chácara em Itatiaiuçu - R$ 65.000
              2. Casa em Betim - R$ 500.000"
    ↓
👤 Cliente: "Me fala mais sobre a chácara"
    ↓
🤖 Innoitune: (IA identifica ID=1 da lista)
    ↓
🤖 Innoitune: GET /api/texto/faq?id=1
    ↓
🤖 Innoitune: Recebe FAQ completo + URLs das fotos
    ↓
🤖 Innoitune: Envia informações + fotos para o cliente
```

---

## 📋 Testando com Curl

### Listar imóveis:
```bash
curl -H "Authorization: Bearer dev-token-12345" \
  "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/texto/imoveis"
```

### FAQ do imóvel 1:
```bash
curl -H "Authorization: Bearer dev-token-12345" \
  "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/texto/faq?id=1"
```

### FAQ do imóvel 2:
```bash
curl -H "Authorization: Bearer dev-token-12345" \
  "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/texto/faq?id=2"
```

---

## ✅ Vantagens deste Formato

- ✅ Apenas 2 endpoints (simples)
- ✅ FAQ inclui TUDO (informações + fotos)
- ✅ ID separado da URL (fácil para IA preencher)
- ✅ Texto puro (sem erro de parsing JSON)
- ✅ Fotos dentro do FAQ (sem endpoint extra)

---

## 🔑 Informações de Acesso

**Base URL:** `https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev`

**API Key:** `dev-token-12345`

**Endpoints:**
1. `/api/texto/imoveis` (listar)
2. `/api/texto/faq?id={ID}` (FAQ completo)

**Header:** `Authorization: Bearer dev-token-12345`
