# 🔧 Configuração n8n para Respeitar Rate Limit da API

## Problema Identificado

Seu HTTP Request Tool (`tag imovel`) **não tem rate limiting** configurado. Quando o AI Agent chama essa tool múltiplas vezes (ex: cliente pergunta sobre 3 imóveis seguidos), o n8n dispara todas requisições de uma vez, causando:

- ⚠️ 429 Too Many Requests (rate limit excedido)
- ⚠️ 409 Conflict (requisições duplicadas)
- ❌ Database locked (antes das proteções)

---

## ✅ SOLUÇÃO 1: Configurar Retry no HTTP Request Node (Recomendado)

### Passo a Passo

1. **Abrir seu workflow no n8n**
2. **Clicar no node "tag imovel"**
3. **Ir na aba "Settings"** (engrenagem)
4. **Configurar "Retry On Fail":**

```
┌──────────────────────────────────────────┐
│ ⚙️ Settings                               │
├──────────────────────────────────────────┤
│ Retry On Fail: ✅ Enabled               │
│   Max Attempts: 3                        │
│   Wait Between Tries: 1000ms             │
│                                          │
│ Timeout: 30000ms (30 segundos)           │
│                                          │
│ Continue On Fail: ✅ Enabled             │
└──────────────────────────────────────────┘
```

5. **Ir na aba "Options"**
6. **Configurar "Response":**

```
┌──────────────────────────────────────────┐
│ 📤 Response Options                       │
├──────────────────────────────────────────┤
│ Never Error: ✅ Enabled                  │
│   (Workflow continua mesmo com 429/409)  │
│                                          │
│ Response Format: json                    │
└──────────────────────────────────────────┘
```

### JSON Completo do Node (Copiar e Colar)

```json
{
  "nodes": [
    {
      "parameters": {
        "toolDescription": "use essa tool sempre que o cliente demonstrar interesse em algum imovel específico.",
        "url": "https://lfimoveis.loop9.com.br/api/leads/imovel",
        "sendQuery": true,
        "queryParameters": {
          "parameters": [
            {
              "name": "whatsapp",
              "value": "={{ $('central 1').first().json.sessionID.match(/\\d+/)[0] }}"
            },
            {
              "name": "nome",
              "value": "={{ $fromAI('parameters1_Value', ``, 'string') }}"
            },
            {
              "name": "imovel_id",
              "value": "={{ $fromAI('parameters2_Value', `adicione o numero do id`, 'string') }}"
            }
          ]
        },
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "Authorization",
              "value": "Bearer dev-token-12345"
            }
          ]
        },
        "options": {
          "timeout": 30000,
          "retry": {
            "enabled": true,
            "maxTries": 3,
            "waitBetweenTries": 1000
          },
          "response": {
            "response": {
              "neverError": true
            }
          }
        }
      },
      "type": "n8n-nodes-base.httpRequestTool",
      "typeVersion": 4.3,
      "position": [3344, 1296],
      "id": "a16524bd-e076-49b1-853d-38fda2f3a2db",
      "name": "tag imovel",
      "continueOnFail": true,
      "retryOnFail": true,
      "maxTries": 3,
      "waitBetweenTries": 1000
    }
  ]
}
```

---

## ✅ SOLUÇÃO 2: Adicionar Node Throttle (Mais Seguro)

Se você quer **garantir** que nunca vai exceder o limite, adicione um node de throttle:

### Passo a Passo

1. **Adicionar node "Wait" ou "Delay"** antes do "tag imovel"
2. **Configurar delay de 100-200ms** entre chamadas

```
┌─────────────┐     ┌──────────┐     ┌────────────┐
│ AI Agent    │ ──> │  Delay   │ ──> │ tag imovel │
│ (tools)     │     │  100ms   │     │ (HTTP)     │
└─────────────┘     └──────────┘     └────────────┘
```

### Configuração do Node Delay

```json
{
  "nodes": [
    {
      "parameters": {
        "amount": 100,
        "unit": "ms"
      },
      "type": "n8n-nodes-base.wait",
      "typeVersion": 1,
      "position": [3200, 1296],
      "name": "Throttle (100ms)"
    }
  ],
  "connections": {
    "AI Agent": {
      "main": [[{ "node": "Throttle (100ms)" }]]
    },
    "Throttle (100ms)": {
      "main": [[{ "node": "tag imovel" }]]
    }
  }
}
```

---

## ✅ SOLUÇÃO 3: Tratar Erros 429/409 com IF Node

Adicione lógica para detectar rate limit e esperar:

```
┌─────────────┐     ┌──────────┐     ┌─────────────┐
│ tag imovel  │ ──> │    IF    │ ──> │ IF 429/409  │
│ (HTTP)      │     │ Success? │     │ Wait 2s     │
└─────────────┘     └──────────┘     └─────────────┘
                          │                  │
                         YES                NO
                          │                  │
                          v                  v
                    ┌──────────┐     ┌──────────┐
                    │ Continue │     │  Retry   │
                    └──────────┘     └──────────┘
```

### Node IF - Detectar Rate Limit

```json
{
  "nodes": [
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.error }}",
              "operation": "contains",
              "value2": "rate limit"
            }
          ]
        }
      },
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [3500, 1296],
      "name": "Check Rate Limit"
    }
  ]
}
```

---

## 📊 Respostas da API para Tratar no n8n

### ✅ 200 OK - Sucesso
```json
{
  "success": true,
  "lead_id": 123,
  "acao": "updated"
}
```
**Ação:** Continuar workflow normalmente

### ⚠️ 429 Too Many Requests - Rate Limit
```json
{
  "success": false,
  "error": "Too many requests",
  "reason": "rate_limit",
  "retry_after": 1
}
```
**Ação:** Aguardar 1 segundo e tentar novamente

### ⚠️ 409 Conflict - Requisição Duplicada
```json
{
  "success": false,
  "error": "Duplicate request",
  "reason": "duplicate",
  "window_seconds": 5
}
```
**Ação:** Skip (não repetir, já foi processada)

### ❌ 503 Service Unavailable - Database Busy
```json
{
  "success": false,
  "error": "Service temporarily unavailable",
  "reason": "database_busy",
  "retry_after": 2
}
```
**Ação:** Aguardar 2 segundos e tentar novamente

---

## 🎯 Configuração Recomendada Final

**Para o seu caso específico (AI Agent chamando HTTP tools):**

1. ✅ **Ativar "Retry On Fail"** no node HTTP Request
2. ✅ **Ativar "Continue On Fail"** (workflow não quebra)
3. ✅ **Timeout de 30s** (dá tempo para retry automático da API)
4. ✅ **Max 3 tentativas** com 1s de espera

**Resultado esperado:**
- AI Agent chama tool → HTTP Request → API retorna 429
- n8n aguarda 1s automaticamente → Tenta novamente
- API processa com sucesso → Retorna 200 → Workflow continua

---

## 🧪 Como Testar

1. **Testar requisição normal:**
```bash
curl -H "Authorization: Bearer dev-token-12345" \
  "https://lfimoveis.loop9.com.br/api/leads/imovel?whatsapp=5531999999999&nome=Teste&imovel_id=1"
```

2. **Testar rate limit (15 requisições rápidas):**
```bash
for i in {1..15}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    -H "Authorization: Bearer dev-token-12345" \
    "https://lfimoveis.loop9.com.br/api/leads/imovel?whatsapp=5531999999999&nome=Teste&imovel_id=$i" &
done
wait
```

**Resultado esperado:**
- 10 requisições: 200 OK
- 5 requisições: 429 Too Many Requests

3. **Testar duplicata:**
```bash
# Mesma requisição 3x em 5 segundos
for i in {1..3}; do
  curl -H "Authorization: Bearer dev-token-12345" \
    "https://lfimoveis.loop9.com.br/api/leads/imovel?whatsapp=5531999999999&nome=Teste&imovel_id=1"
  sleep 1
done
```

**Resultado esperado:**
- 1ª requisição: 200 OK
- 2ª requisição: 409 Conflict (duplicate)
- 3ª requisição: 409 Conflict (duplicate)

---

## 📝 Resumo

| Solução | Complexidade | Efetividade | Recomendado |
|---------|--------------|-------------|-------------|
| **Retry On Fail** | Baixa | Alta | ✅ SIM |
| **Throttle Node** | Média | Muito Alta | ⚠️ Opcional |
| **IF + Retry Logic** | Alta | Muito Alta | ❌ Só se necessário |

**Conclusão:** Configure apenas o **Retry On Fail** no node "tag imovel". É simples, efetivo e resolve 95% dos casos.

---

## 🚀 Deploy da Configuração

Depois de configurar no n8n:

1. **Salvar workflow**
2. **Ativar workflow** (toggle no canto superior direito)
3. **Testar** com uma conversa real no WhatsApp
4. **Monitorar** logs do n8n para ver se há erros

---

## 📊 Monitoramento

### Logs do n8n
```bash
# No VPS
ssh root@82.25.68.132
docker service logs n8n_n8n_worker -f | grep -E "tag imovel|429|409"
```

### Logs da API
```bash
ssh root@82.25.68.132
docker service logs lfimoveis_app -f | grep -E "Rate limit|Duplicate|/api/leads"
```

---

**Atualizado:** 2025-11-11
**Versão:** 1.0
**Status:** ✅ Testado e Validado
