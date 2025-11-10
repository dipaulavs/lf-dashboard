# 🤖 Configuração Innoitune - Formato TEXTO

## ⚠️ IMPORTANTE
O Innoitune tem dificuldade com JSON. Use os endpoints com `?formato=texto` para receber texto simples.

---

## 1️⃣ LISTAR IMÓVEIS (FORMATO TEXTO)

**URL:**
```
https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/imoveis?formato=texto
```

**Method:** GET

**Headers:**
```
Authorization: Bearer dev-token-12345
```

**Resposta Exemplo:**
```
IMÓVEIS DISPONÍVEIS (2 encontrados):

ID: 1
Título: Chácara 1000m² Itatiaiuçu
Tipo: Chacara
Cidade: Itatiaiuçu
Área: 1000m²
Preço: R$ 65.000.00
Status: Disponivel
--------------------------------------------------

ID: 2
Título: Casa 3 Quartos Betim
Tipo: Casa
Cidade: Betim
Área: 150m²
Preço: R$ 200.000.00
Status: Disponivel
--------------------------------------------------
```

---

## 2️⃣ FAQ DO IMÓVEL (FORMATO TEXTO)

**URL:**
```
https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/imoveis/1/faq?formato=texto
```
*Troque `1` pelo ID do imóvel*

**Method:** GET

**Headers:**
```
Authorization: Bearer dev-token-12345
```

**Resposta Exemplo:**
```
FAQ - Chácara 1000m² Itatiaiuçu
ID: 1
==================================================

Chácara maravilhosa com 1000m², localizada em Itatiaiuçu.

Características:
- Água disponível
- Energia elétrica
- Documentação em dia
- Acesso asfaltado

Condições de Pagamento:
- Entrada de 30%
- Saldo em até 12x
```

---

## 3️⃣ FOTOS DO IMÓVEL (FORMATO TEXTO)

**URL:**
```
https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/imoveis/1/fotos?formato=texto
```
*Troque `1` pelo ID do imóvel*

**Method:** GET

**Headers:**
```
Authorization: Bearer dev-token-12345
```

**Resposta Exemplo:**
```
FOTOS - Chácara 1000m² Itatiaiuçu
ID: 1
==================================================

FOTOS (2 disponíveis):
1. https://via.placeholder.com/800x600.png?text=Foto1
2. https://via.placeholder.com/800x600.png?text=Foto2

VÍDEO TOUR:
https://youtube.com/watch?v=exemplo
```

---

## 🔧 Como Configurar no Innoitune

### **Ação 1: Listar Imóveis**
1. Criar nova ação HTTP Request
2. Nome: "Listar Imóveis"
3. Method: GET
4. URL: `https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/imoveis?formato=texto`
5. Headers: `Authorization: Bearer dev-token-12345`
6. Salvar

### **Ação 2: Buscar FAQ**
1. Criar nova ação HTTP Request
2. Nome: "Buscar FAQ Imóvel"
3. Method: GET
4. URL: `https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/imoveis/{id}/faq?formato=texto`
5. Headers: `Authorization: Bearer dev-token-12345`
6. Substituir `{id}` dinamicamente pelo ID do imóvel
7. Salvar

### **Ação 3: Buscar Fotos**
1. Criar nova ação HTTP Request
2. Nome: "Buscar Fotos Imóvel"
3. Method: GET
4. URL: `https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/imoveis/{id}/fotos?formato=texto`
5. Headers: `Authorization: Bearer dev-token-12345`
6. Substituir `{id}` dinamicamente pelo ID do imóvel
7. Salvar

---

## 📋 Testando com Curl

```bash
# 1. Listar imóveis (texto)
curl -H "Authorization: Bearer dev-token-12345" \
  "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/imoveis?formato=texto"

# 2. FAQ do imóvel 1 (texto)
curl -H "Authorization: Bearer dev-token-12345" \
  "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/imoveis/1/faq?formato=texto"

# 3. Fotos do imóvel 1 (texto)
curl -H "Authorization: Bearer dev-token-12345" \
  "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/imoveis/1/fotos?formato=texto"
```

---

## 🎯 Fluxo de Conversa

```
👤 Cliente: "Quero ver imóveis disponíveis"
    ↓
🤖 Innoitune: Chama GET /api/imoveis?formato=texto
    ↓
🤖 Innoitune: Recebe texto simples com lista de imóveis
    ↓
🤖 Innoitune: "Temos 2 imóveis disponíveis:
              1. Chácara 1000m² em Itatiaiuçu - R$ 65.000
              2. Casa 3 Quartos em Betim - R$ 200.000"
    ↓
👤 Cliente: "Me fala mais sobre a chácara"
    ↓
🤖 Innoitune: Chama GET /api/imoveis/1/faq?formato=texto
    ↓
🤖 Innoitune: Recebe FAQ completo em texto
    ↓
🤖 Innoitune: Envia FAQ para o cliente
    ↓
👤 Cliente: "Manda fotos"
    ↓
🤖 Innoitune: Chama GET /api/imoveis/1/fotos?formato=texto
    ↓
🤖 Innoitune: Recebe lista de URLs em texto
    ↓
🤖 Innoitune: Extrai URLs e envia fotos
```

---

## ✅ Vantagens do Formato Texto

- ✅ Mais fácil de processar para agentes IA
- ✅ Sem problemas de parsing JSON
- ✅ Resposta legível e estruturada
- ✅ Funciona com qualquer ferramenta HTTP Request

---

## 📌 Copiar e Colar

**Endpoint 1:**
```
https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/imoveis?formato=texto
```

**Endpoint 2:**
```
https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/imoveis/1/faq?formato=texto
```

**Endpoint 3:**
```
https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/imoveis/1/fotos?formato=texto
```

**Header (para todos):**
```
Authorization: Bearer dev-token-12345
```
