# 🌐 Dashboard Imóveis - Rodando com Ngrok

## URL Pública (Ngrok)
```
https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev
```

---

## 🔧 CURL para o Agente IA

### 1. Registrar Lead (copiar e colar)

```bash
curl -X POST https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/leads/registrar \
  -H "Authorization: Bearer dev-token-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "whatsapp": "5531999887766",
    "nome": "Nome do Cliente",
    "imovel_id": 1,
    "score": 45,
    "agendou_visita": false
  }'
```

### 2. Com variáveis (para o agente preencher)

```bash
curl -X POST https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/leads/registrar \
  -H "Authorization: Bearer dev-token-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "whatsapp": "{{NUMERO_WHATSAPP}}",
    "nome": "{{NOME_CLIENTE}}",
    "imovel_id": {{ID_IMOVEL}},
    "score": {{SCORE_CALCULADO}},
    "agendou_visita": {{AGENDOU_VISITA}}
  }'
```

---

## 📊 Exemplos por Situação

### Cliente perguntou sobre imóvel (primeira vez)
```bash
curl -X POST https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/leads/registrar \
  -H "Authorization: Bearer dev-token-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "whatsapp": "5531999887766",
    "nome": "João Silva",
    "imovel_id": 1,
    "score": 5,
    "agendou_visita": false
  }'
```

### Cliente perguntou preço
```bash
curl -X POST https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/leads/registrar \
  -H "Authorization: Bearer dev-token-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "whatsapp": "5531999887766",
    "nome": "João Silva",
    "imovel_id": 1,
    "score": 15,
    "agendou_visita": false
  }'
```

### Cliente marcou visita 🔥
```bash
curl -X POST https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/leads/registrar \
  -H "Authorization: Bearer dev-token-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "whatsapp": "5531999887766",
    "nome": "João Silva",
    "imovel_id": 1,
    "score": 55,
    "agendou_visita": true
  }'
```

---

## 🔍 Consultar Leads

### Listar todos
```bash
curl -H "Authorization: Bearer dev-token-12345" \
  https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/leads
```

### Listar leads quentes (score >= 61)
```bash
curl -H "Authorization: Bearer dev-token-12345" \
  "https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/leads?score_min=61"
```

### Buscar lead específico + histórico
```bash
curl -H "Authorization: Bearer dev-token-12345" \
  https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/leads/5531999887766
```

### Estatísticas
```bash
curl -H "Authorization: Bearer dev-token-12345" \
  https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/estatisticas
```

---

## 🎯 Configuração no Innoitune

**URL do Endpoint:**
```
https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev/api/leads/registrar
```

**Método:** POST

**Headers:**
```
Authorization: Bearer dev-token-12345
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "whatsapp": "{{whatsapp_number}}",
  "nome": "{{customer_name}}",
  "imovel_id": {{property_id}},
  "score": {{calculated_score}},
  "agendou_visita": {{scheduled_visit}}
}
```

---

## 📱 Acessar Dashboard Visual

```
https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev
```

Clique na aba "👥 Leads" para ver:
- Gráficos de distribuição
- Tabela de leads
- Filtros por score/imóvel/agendamento
- Exportação CSV

---

## 📋 Tabela de Pontuação

| Ação | Pontos | Score |
|------|--------|-------|
| Primeira mensagem | +5 | 5 |
| Perguntou preço | +10 | 15 |
| Pediu fotos | +10 | 25 |
| Perguntou financiamento | +15 | 40 |
| Perguntou endereço | +20 | 60 |
| **Marcou visita** | +30 | **90** |

---

## ⚙️ Processos Rodando

- **Flask:** http://localhost:5555
- **Ngrok:** https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev
- **Logs:** /tmp/dashboard-prod.log

### Para parar:
```bash
# Parar Flask
lsof -ti:5555 | xargs kill -9

# Parar Ngrok
pkill ngrok
```

---

## ✅ Testado e Funcionando

Sistema 100% operacional com:
- ✅ Backend Flask
- ✅ SQLite Database
- ✅ API REST (5 endpoints)
- ✅ Frontend com gráficos
- ✅ Ngrok tunnel ativo
- ✅ SSL automático (ngrok)

**Pronto para integrar com seu agente IA!** 🚀
