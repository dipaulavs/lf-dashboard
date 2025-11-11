# Exemplos Práticos de Uso dos Decorators

Guia rápido para aplicar proteções em outros endpoints.

---

## 1. Endpoint de Escrita Simples

**Cenário:** Atualizar score de lead (já implementado)

```python
@app.route('/api/leads/score', methods=['GET'])
@require_api_key
@protect_endpoint(
    max_requests=10,
    window_seconds=1,
    dedup_window=5,
    dedup_params=['whatsapp', 'score']
)
def atualizar_score():
    whatsapp = request.args.get('whatsapp')
    score = request.args.get('score')

    # Protegido contra:
    # - Burst > 10 req/s → 429
    # - Mesma requisição em 5s → 409
    # - Database locked → 503 (retry automático)

    resultado = db_leads.registrar_lead(...)
    return jsonify(resultado)
```

**Resultado:** n8n pode enviar 50 req/s, apenas 10 processadas/s, resto bloqueado.

---

## 2. Endpoint de Criação (POST)

**Cenário:** Criar agendamento de visita

```python
@app.route('/api/agendamentos', methods=['POST'])
@require_api_key
@protect_endpoint(
    max_requests=5,  # Mais restritivo (escrita custosa)
    window_seconds=1,
    dedup_window=10,  # Janela maior (agendamentos são raros)
    dedup_params=['whatsapp', 'data_visita', 'hora_visita']
)
def criar_agendamento():
    data = request.get_json()

    # dedup_params garante que mesmo cliente não agende
    # mesma visita múltiplas vezes em 10s

    resultado = db_leads.criar_agendamento(
        nome_cliente=data['nome'],
        whatsapp=data['whatsapp'],
        data_visita=data['data'],
        hora_visita=data['hora']
    )

    return jsonify(resultado)
```

**Dedup params explicados:**
- `whatsapp + data_visita + hora_visita` = identificador único
- Se n8n enviar 5x a mesma requisição, apenas 1 processa
- Outras retornam 409 Conflict

---

## 3. Endpoint de Leitura (GET)

**Cenário:** Listar leads (sem escrita)

```python
@app.route('/api/leads', methods=['GET'])
@require_api_key
@rate_limit(max_requests=50, window_seconds=1)  # Apenas rate limit
def listar_leads():
    # Leitura = sem risco de database locked
    # Não precisa de deduplicação nem retry
    # Apenas rate limit para prevenir abuso

    filtros = {}
    if request.args.get('score_min'):
        filtros['score_min'] = int(request.args.get('score_min'))

    leads = db_leads.listar_leads(filtros)
    return jsonify({"leads": leads})
```

**Quando usar apenas `@rate_limit`:**
- Endpoints de leitura (GET)
- Operações idempotentes
- Sem risco de database locking

---

## 4. Proteção Personalizada

**Cenário:** Endpoint crítico que precisa controle fino

```python
from decorators import rate_limit, deduplicate, retry_on_lock

@app.route('/api/leads/delete', methods=['DELETE'])
@require_api_key
@rate_limit(max_requests=2, window_seconds=10)  # Muito restritivo
@deduplicate(window_seconds=30, check_params=['whatsapp'])  # Janela longa
@retry_on_lock(max_retries=5)  # Mais tentativas
def deletar_lead():
    whatsapp = request.args.get('whatsapp')

    # Proteções:
    # - Apenas 2 deleções a cada 10s por IP
    # - Não pode deletar mesmo lead 2x em 30s
    # - 5 tentativas de retry se DB travar

    resultado = db_leads.deletar_lead(whatsapp)
    return jsonify(resultado)
```

**Aplicar decorators em ordem:**
1. `@rate_limit` (primeiro a verificar)
2. `@deduplicate` (verifica depois do rate limit)
3. `@retry_on_lock` (executa por último, captura erros)

---

## 5. Endpoint sem Deduplicação

**Cenário:** Cada requisição é única (não faz sentido dedup)

```python
@app.route('/api/analytics/track', methods=['POST'])
@require_api_key
@rate_limit(max_requests=100, window_seconds=1)
@retry_on_lock()
def track_evento():
    data = request.get_json()

    # Analytics = cada evento é único
    # Mesmo payload repetido = eventos diferentes
    # Logo: SEM deduplicação

    db.registrar_evento(
        evento=data['evento'],
        timestamp=datetime.now()
    )

    return jsonify({"success": True})
```

---

## 6. Proteção por API Key (ao invés de IP)

**Cenário:** Múltiplas instâncias n8n na mesma rede

```python
from decorators import RateLimiter

# Criar limiter customizado
api_key_limiter = RateLimiter(max_requests=20, window_seconds=1)

@app.route('/api/leads/bulk', methods=['POST'])
@require_api_key
def bulk_import():
    # Identificar por API key ao invés de IP
    api_key = request.headers.get('X-API-Key', 'unknown')

    # Verificar rate limit por API key
    allowed, reason = api_key_limiter.is_allowed(api_key)

    if not allowed:
        return jsonify({
            "success": False,
            "error": "Too many requests",
            "retry_after": 1
        }), 429

    # Processar bulk import
    leads = request.get_json()['leads']

    for lead in leads:
        db_leads.registrar_lead(**lead)

    return jsonify({"success": True, "imported": len(leads)})
```

**Vantagem:** Limites por cliente (API key) ao invés de IP compartilhado.

---

## 7. Desabilitar Proteções em Dev

**Cenário:** Desenvolvimento local sem rate limiting

```python
import os

# Em app.py (topo do arquivo)
ENABLE_RATE_LIMIT = os.getenv('ENABLE_RATE_LIMIT', 'true').lower() == 'true'

# Decorator condicional
def optional_rate_limit(*args, **kwargs):
    def decorator(func):
        if ENABLE_RATE_LIMIT:
            return protect_endpoint(*args, **kwargs)(func)
        else:
            return func
    return decorator

# Uso
@app.route('/api/leads/score')
@require_api_key
@optional_rate_limit(max_requests=10, dedup_params=['whatsapp', 'score'])
def atualizar_score():
    pass
```

**Controle via env:**
```bash
# Produção
export ENABLE_RATE_LIMIT=true

# Desenvolvimento
export ENABLE_RATE_LIMIT=false
```

---

## 8. Logging e Monitoramento

**Cenário:** Rastrear bloqueios para ajustar limites

```python
import logging

logger = logging.getLogger(__name__)

@app.route('/api/leads/score')
@require_api_key
@protect_endpoint(max_requests=10, dedup_params=['whatsapp', 'score'])
def atualizar_score():
    # decorators.py já loga automaticamente:
    # WARNING: Rate limit exceeded for 192.168.1.100
    # INFO: Duplicate request detected

    whatsapp = request.args.get('whatsapp')

    # Log adicional para métricas
    logger.info(f"Processing score update for {whatsapp}")

    resultado = db_leads.registrar_lead(...)

    return jsonify(resultado)
```

**Logs gerados automaticamente:**
```
WARNING: Rate limit exceeded for 172.16.0.5 on /api/leads/score
INFO: Duplicate request detected: /api/leads/score params={'whatsapp': '123', 'score': 45} hash=a1b2c3d4
ERROR: Database locked after 3 retries on /api/leads/score: database is locked
```

---

## 9. Resposta Customizada para Erros

**Cenário:** Retornar mensagem específica para cada erro

```python
@app.route('/api/leads/score')
@require_api_key
def atualizar_score():
    # Aplicar proteções manualmente para controle fino
    from rate_limiter import rate_limiter

    client_ip = request.remote_addr
    request_data = {
        'whatsapp': request.args.get('whatsapp'),
        'score': request.args.get('score')
    }

    # Verificar rate limit
    allowed, reason = rate_limiter.check_request(client_ip, request_data)

    if not allowed:
        if reason == "rate_limit":
            return jsonify({
                "success": False,
                "error": "Você está enviando requisições muito rápido.",
                "message": "Aguarde 1 segundo e tente novamente.",
                "retry_after": 1
            }), 429

        elif reason == "duplicate":
            return jsonify({
                "success": False,
                "error": "Requisição duplicada detectada.",
                "message": "Essa atualização já foi processada recentemente.",
                "window_seconds": 5
            }), 409

    # Processar normalmente
    resultado = db_leads.registrar_lead(...)
    return jsonify(resultado)
```

---

## 10. Combinação Avançada

**Cenário:** Endpoint com múltiplas regras

```python
from functools import wraps

def advanced_protection(func):
    """Proteção customizada com múltiplas regras"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Regra 1: Horário comercial (9h-18h)
        hora_atual = datetime.now().hour
        if hora_atual < 9 or hora_atual >= 18:
            return jsonify({
                "success": False,
                "error": "Endpoint disponível apenas em horário comercial (9h-18h)"
            }), 403

        # Regra 2: Rate limit por API key
        api_key = request.headers.get('X-API-Key', 'unknown')
        allowed, reason = rate_limiter.is_allowed(api_key)

        if not allowed:
            return jsonify({
                "success": False,
                "error": "Too many requests"
            }), 429

        # Regra 3: Validar payload
        if request.method == 'POST':
            data = request.get_json()
            if not data or 'whatsapp' not in data:
                return jsonify({
                    "success": False,
                    "error": "Payload inválido"
                }), 400

        # Todas regras passaram
        return func(*args, **kwargs)

    return wrapper

@app.route('/api/leads/premium', methods=['POST'])
@require_api_key
@advanced_protection
def endpoint_premium():
    # Protegido por:
    # - Horário comercial
    # - Rate limit
    # - Validação de payload
    # - Autenticação (require_api_key)

    data = request.get_json()
    resultado = db_leads.registrar_lead(**data)
    return jsonify(resultado)
```

---

## Resumo de Uso

| Endpoint | Proteções | Rate Limit | Dedup | Retry |
|----------|-----------|------------|-------|-------|
| Escrita crítica | `@protect_endpoint()` | ✅ 10/s | ✅ 5s | ✅ 3x |
| Escrita normal | `@protect_endpoint()` | ✅ 20/s | ✅ 5s | ✅ 3x |
| Leitura | `@rate_limit()` | ✅ 50/s | ❌ | ❌ |
| Deleção | Custom | ✅ 2/10s | ✅ 30s | ✅ 5x |
| Analytics | `@rate_limit()` + `@retry_on_lock()` | ✅ 100/s | ❌ | ✅ 3x |

---

**Próximos passos:**
1. Aplicar proteções nos outros endpoints de leads
2. Testar com carga real do n8n
3. Ajustar limites conforme métricas
4. Considerar migrar para PostgreSQL se > 100 req/s
