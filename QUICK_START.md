# Quick Start - Proteção contra Database Locking

Guia rápido de 2 minutos para ativar as proteções.

---

## Status Atual

```
✅ Implementado: 3 camadas de proteção
✅ Testado: 13/13 testes passando
✅ Endpoint protegido: /api/leads/score
🟡 Pendente: Reiniciar Flask app
```

---

## Como Ativar (3 comandos)

### 1. Verificar arquivos
```bash
cd "/Users/felipemdepaula/Desktop/ClaudeCode-Workspace/APPS E SITES/lfimoveis-dashboard"

# Verificar que arquivos existem
ls -lh database.py decorators.py rate_limiter.py

# Rodar testes
python3 test_rate_limiter_standalone.py
```

**Resultado esperado:** `13/13 testes passaram ✅`

---

### 2. Reiniciar Flask app

```bash
# Parar app atual (se rodando)
pkill -f "python.*app.py"

# Iniciar com proteções ativas
python3 app.py
```

**Ou via Docker:**
```bash
docker-compose restart
```

---

### 3. Testar endpoint protegido

```bash
# Teste básico (deve passar)
curl "http://localhost:5002/api/leads/score?whatsapp=5531999887766&nome=João&score=45" \
  -H "X-API-Key: seu-token"

# Teste de burst (10 passam, 5 bloqueadas)
for i in {1..15}; do
  curl -s "http://localhost:5002/api/leads/score?whatsapp=5531$i&nome=Lead$i&score=45" \
    -H "X-API-Key: seu-token" | jq -r '.error // "OK"'
done
```

**Resultado esperado:**
```
OK
OK
...
OK  (10x)
Too many requests  (5x)
```

---

## Proteções Ativas

### Camada 1: Rate Limiting
- Limite: 10 req/s por IP
- Resposta: 429 Too Many Requests

### Camada 2: Deduplicação
- Janela: 5 segundos
- Params: whatsapp + score
- Resposta: 409 Conflict

### Camada 3: SQLite Otimizado
- WAL mode: Leituras durante escritas
- Timeout: 30 segundos
- Retry: 3 tentativas com backoff
- Resposta: 503 Service Unavailable (se todas tentativas falharem)

---

## Verificar WAL Mode

```bash
cd data
sqlite3 dashboard.db "PRAGMA journal_mode;"
```

**Deve retornar:** `wal`

Se retornar `delete` ou `truncate`:
```bash
# Forçar WAL mode
sqlite3 dashboard.db "PRAGMA journal_mode=WAL;"
```

---

## Configurar n8n

### Opção 1: Retry automático (recomendado)

No HTTP Request node:
```
Settings:
  Retry on Fail: On
  Max Tries: 3
  Wait Between Tries: 1000ms

Options:
  Response:
    Continue on Fail: On

Error Handling:
  IF status code = 429 OR 409
    THEN: Skip and log
    ELSE: Retry
```

### Opção 2: Batch com delay

```
Split In Batches (10) → Wait (100ms) → HTTP Request
```

---

## Monitorar Logs

```bash
# Tail logs do Flask
tail -f app.log

# Ou se rodando em foreground
python3 app.py
```

**Logs esperados:**
```
WARNING: Rate limit exceeded for 192.168.1.100 on /api/leads/score
INFO: Duplicate request detected: /api/leads/score params={'whatsapp': '123'}
```

---

## Troubleshooting Rápido

### Ainda recebo database locked

**1. Verificar WAL mode:**
```bash
sqlite3 data/dashboard.db "PRAGMA journal_mode;"
```

**2. Verificar timeout:**
```bash
sqlite3 data/dashboard.db "PRAGMA busy_timeout;"
# Deve retornar: 30000
```

**3. Reiniciar Flask:**
```bash
pkill -f "python.*app.py"
python3 app.py
```

### Muitos 429 (rate limit)

**Solução 1:** Aumentar limite no código
```python
# Em app.py, linha 762
@protect_endpoint(
    max_requests=20,  # Aumentar de 10 para 20
    ...
)
```

**Solução 2:** Configurar batch no n8n
```
Split In Batches: 10 items
Wait: 100ms between batches
```

### n8n continua com erro

**Verificar:**
1. API key correta
2. URL correta (http://localhost:5002)
3. Parâmetros obrigatórios (whatsapp, nome, score)
4. Flask rodando

**Testar direto:**
```bash
curl -v "http://localhost:5002/api/leads/score?whatsapp=123&nome=Test&score=45" \
  -H "X-API-Key: seu-token"
```

---

## Aplicar em Outros Endpoints

### Endpoint de escrita
```python
@app.route('/api/leads/imovel', methods=['GET'])
@require_api_key
@protect_endpoint(
    max_requests=10,
    dedup_params=['whatsapp', 'imovel_id']
)
def definir_imovel():
    pass
```

### Endpoint de leitura
```python
@app.route('/api/leads', methods=['GET'])
@require_api_key
@rate_limit(max_requests=50, window_seconds=1)
def listar_leads():
    pass
```

---

## Documentação Completa

- **README_RATE_LIMITING.md** - Guia completo (9.3K)
- **IMPLEMENTACAO_COMPLETA.md** - Detalhes técnicos (13K)
- **EXEMPLOS_USO.md** - 10 exemplos práticos (10K)

---

## Comandos Úteis

```bash
# Rodar todos os testes
python3 test_rate_limiter_standalone.py

# Simular burst
python3 test_burst_simulation.py

# Verificar sintaxe
python3 -m py_compile database.py decorators.py

# Ver limites atuais
grep "max_requests" app.py decorators.py
```

---

## Resultados Esperados

### Antes
```
n8n → Burst 50 req/s
         ↓
❌ sqlite3.OperationalError: database is locked
```

### Depois
```
n8n → Burst 50 req/s
         ↓
✅ 10 req/s processadas
⚠️  40 req/s bloqueadas (429)
✅ 0 database locks
```

---

**Tudo certo?** Proteções ativas! ✅

**Problemas?** Consultar README_RATE_LIMITING.md ou logs do Flask.
