# Sistema de Score/Tags para Leads

Sistema completo de pontuação e tags para leads de imóveis, integrado ao Dashboard via HTTP Request.

## Arquitetura

```
Cliente WhatsApp
    ↓
Evolution API
    ↓
Agente IA (Innoitune)
    ├─ Processa conversa
    ├─ Calcula score (0-100)
    ├─ Detecta agendamento
    └─ USA FERRAMENTA: registrar_lead()
    ↓
Dashboard API
    ├─ SQLite (persistência)
    ├─ Gráficos (Chart.js)
    └─ Exportação CSV
```

## Sistema de Pontuação (0-100)

### Ações que aumentam o score:

| Ação | Pontos | Descrição |
|------|--------|-----------|
| Primeira mensagem | +5 | Cliente iniciou contato |
| Perguntou preço | +10 | Interesse em valor |
| Pediu fotos/vídeos | +10 | Quer conhecer melhor |
| Perguntou financiamento | +15 | Pensando em compra |
| Perguntou endereço exato | +20 | Perto de visitar |
| **Marcou visita** | +30 | **Ação mais valiosa** |
| Voltou depois de 24h | +10 | Lead engajado |

### Tags automáticas por score:

- **0-30**: Lead Frio ❄️
- **31-60**: Lead Morno 🌡️
- **61-100**: Lead Quente 🔥

## API Endpoints

### 1. Taguear Lead via URL (GET) - NOVO! ⚡

**Perfeito para automações** - Todos os campos são query parameters individuais!

```
GET /api/leads/tag?whatsapp=5531999887766&nome=João Silva&imovel_id=1&score=45&agendou_visita=true
Authorization: Bearer dev-token-12345
```

**Parâmetros (todos individuais):**
- `whatsapp` - Número WhatsApp (obrigatório) - Ex: 5531999887766
- `nome` - Nome do lead (obrigatório) - Ex: João Silva
- `imovel_id` - ID do imóvel (opcional) - Ex: 1
- `score` - Score 0-100 (obrigatório) - Ex: 45
- `agendou_visita` - true/false (opcional, padrão: false) - Ex: true

**Exemplos de uso:**

```bash
# Lead novo com interesse inicial (score baixo)
curl "https://dashboard-imoveis.loop9.com.br/api/leads/tag?whatsapp=5531999887766&nome=João%20Silva&score=15" \
  -H "Authorization: Bearer dev-token-12345"

# Lead perguntou preço (aumentar score)
curl "https://dashboard-imoveis.loop9.com.br/api/leads/tag?whatsapp=5531999887766&nome=João%20Silva&imovel_id=1&score=25" \
  -H "Authorization: Bearer dev-token-12345"

# Lead agendou visita (score alto + flag)
curl "https://dashboard-imoveis.loop9.com.br/api/leads/tag?whatsapp=5531999887766&nome=João%20Silva&imovel_id=1&score=55&agendou_visita=true" \
  -H "Authorization: Bearer dev-token-12345"

# Teste local (desenvolvimento)
curl "http://localhost:5555/api/leads/tag?whatsapp=5531999887766&nome=Teste&score=30" \
  -H "Authorization: Bearer dev-token-12345"
```

**Resposta:**
```json
{
  "success": true,
  "lead_id": 123,
  "acao": "created",  // ou "updated"
  "score": 45
}
```

**Uso em automações (Make, Zapier, n8n):**
```
URL: https://dashboard-imoveis.loop9.com.br/api/leads/tag
Método: GET
Headers:
  - Authorization: Bearer dev-token-12345
Query Params:
  - whatsapp: {{contact.phone}}
  - nome: {{contact.name}}
  - imovel_id: {{message.imovel_id}}
  - score: {{calculated_score}}
  - agendou_visita: {{has_scheduled}}
```

### 2. Registrar/Atualizar Lead via POST (método original)

```bash
POST /api/leads/registrar
Authorization: Bearer dev-token-12345
Content-Type: application/json

{
  "whatsapp": "5531999887766",
  "nome": "João Silva",
  "imovel_id": 1,
  "score": 45,
  "agendou_visita": true
}
```

**Resposta:**
```json
{
  "success": true,
  "lead_id": 123,
  "acao": "created",  // ou "updated"
  "score": 45
}
```

### 3. Listar Leads (com filtros)

```bash
GET /api/leads?score_min=31&score_max=60&agendou_visita=true
Authorization: Bearer dev-token-12345
```

**Parâmetros:**
- `score_min`: Score mínimo (0-100)
- `score_max`: Score máximo (0-100)
- `imovel_id`: Filtrar por imóvel
- `agendou_visita`: true/false

**Resposta:**
```json
{
  "success": true,
  "total": 15,
  "filtros_aplicados": {
    "score_min": 31,
    "score_max": 60
  },
  "leads": [
    {
      "id": 1,
      "whatsapp": "5531999887766",
      "nome": "João Silva",
      "imovel_id": 1,
      "score": 45,
      "agendou_visita": true,
      "criado_em": "2025-11-09T10:30:00",
      "atualizado_em": "2025-11-09T15:45:00"
    }
  ]
}
```

### 4. Buscar Lead Específico

```bash
GET /api/leads/5531999887766
Authorization: Bearer dev-token-12345
```

**Resposta:**
```json
{
  "success": true,
  "lead": {
    "id": 1,
    "whatsapp": "5531999887766",
    "nome": "João Silva",
    "score": 45,
    "imovel_id": 1,
    "agendou_visita": true
  },
  "historico": [
    {
      "id": 1,
      "score_anterior": 15,
      "score_novo": 45,
      "motivo": "Score atualizado de 15 para 45",
      "timestamp": "2025-11-09T15:45:00"
    }
  ]
}
```

### 5. Estatísticas (para gráficos)

```bash
GET /api/estatisticas
Authorization: Bearer dev-token-12345
```

**Resposta:**
```json
{
  "success": true,
  "estatisticas": {
    "total_leads": 75,
    "distribuicao": {
      "frios": 12,
      "mornos": 25,
      "quentes": 38
    },
    "por_imovel": [
      { "imovel_id": 1, "count": 30 },
      { "imovel_id": 2, "count": 20 }
    ],
    "agendamentos": {
      "total_agendamentos": 15,
      "taxa_agendamento": 20.0
    },
    "score_medio": 52.5
  }
}
```

### 6. Exportar CSV

```bash
GET /api/leads/export?score_min=61&agendou_visita=true
Authorization: Bearer dev-token-12345
```

**Retorna arquivo CSV:**
```
Nome,WhatsApp,Score,Imóvel ID,Agendou Visita,Criado Em
João Silva,5531999887766,75,1,True,2025-11-09T10:30:00
Maria Souza,5531888776655,85,1,True,2025-11-09T11:15:00
```

## Ferramenta para Agente IA

### Instalação

```bash
cd ferramentas
pip install requests
```

### Uso no código do agente

```python
from ferramentas.registrar_lead import registrar_lead

# Exemplo 1: Cliente perguntou sobre imóvel
resultado = registrar_lead(
    whatsapp="5531999887766",
    nome="João Silva",
    imovel_id=1,
    score=15,
    agendou_visita=False
)

# Exemplo 2: Cliente perguntou preço
resultado = registrar_lead(
    whatsapp="5531999887766",
    nome="João Silva",
    imovel_id=1,
    score=25,  # +10 pontos
    agendou_visita=False
)

# Exemplo 3: Cliente marcou visita
resultado = registrar_lead(
    whatsapp="5531999887766",
    nome="João Silva",
    imovel_id=1,
    score=55,  # +30 pontos
    agendou_visita=True
)

print(resultado)
# {'success': True, 'lead_id': 123, 'acao': 'updated', 'score': 55}
```

### Configuração via variáveis de ambiente

```bash
export DASHBOARD_URL="https://dashboard-imoveis.loop9.com.br"
export DASHBOARD_API_KEY="seu-token-aqui"
```

## Dashboard Frontend

### Aba "Leads"

#### Filtros disponíveis:
1. **Score**: Todos / Frios (0-30) / Mornos (31-60) / Quentes (61-100)
2. **Imóvel**: Dropdown com todos os imóveis cadastrados
3. **Agendamento**: Todos / Agendou visita / Não agendou

#### Gráficos:
1. **Pizza**: Distribuição por score (frio/morno/quente)
2. **Barras**: Leads por imóvel

#### Tabela:
- Nome
- WhatsApp (formatado: 55 31 99988-7766)
- Score (com badge colorido)
- Imóvel de interesse
- Agendou visita? ✅/❌
- Última atualização

#### Ações:
- **Exportar CSV**: Baixa arquivo com leads filtrados
- Click em linha: Ver histórico completo (futuro)

## Casos de Uso

### 1. Enviar campanha para leads quentes

```bash
# Filtrar no dashboard:
- Score: Leads Quentes (61-100)
- Agendou visita: Sim

# Exportar CSV → obter números WhatsApp
# Usar em campanha de remarketing
```

### 2. Priorizar atendimento

```bash
# Consultar API:
GET /api/leads?score_min=61&agendou_visita=true

# Resultado: Leads prontos para fechar negócio
# Atendente prioriza esses contatos
```

### 3. Analisar imóvel mais popular

```bash
# Ver gráfico "Leads por Imóvel"
# Identificar: Chácara Itatiaiuçu tem 45 leads
# Ação: Criar campanha focada nesse imóvel
```

### 4. Taxa de conversão

```bash
# Estatísticas mostram:
- Total de leads: 100
- Agendamentos: 25
- Taxa: 25%

# Métrica para acompanhar performance
```

## Estrutura do Banco de Dados

### Tabela: `leads`

```sql
CREATE TABLE leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    whatsapp TEXT UNIQUE NOT NULL,
    nome TEXT NOT NULL,
    imovel_id INTEGER,
    score INTEGER CHECK(score >= 0 AND score <= 100) DEFAULT 0,
    agendou_visita BOOLEAN DEFAULT 0,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Tabela: `score_historico`

```sql
CREATE TABLE score_historico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    whatsapp TEXT NOT NULL,
    score_anterior INTEGER,
    score_novo INTEGER,
    motivo TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (whatsapp) REFERENCES leads(whatsapp)
);
```

## Testes

### Testar ferramenta

```bash
cd ferramentas
python3 registrar_lead.py

# Testes automáticos:
# 1. Criar novo lead
# 2. Atualizar score
# 3. Marcar visita
```

### Testar endpoint diretamente

```bash
curl -X POST http://localhost:5555/api/leads/registrar \
  -H "Authorization: Bearer dev-token-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "whatsapp": "5531999887766",
    "nome": "Teste Cliente",
    "imovel_id": 1,
    "score": 35,
    "agendou_visita": false
  }'
```

## Deploy

### Desenvolvimento (local)

```bash
cd dashboard-imoveis
python3 app.py
# Acessa: http://localhost:5555
```

### Produção (SWARM)

```bash
cd SWARM
./deploy.sh dashboard-imoveis
# Acessa: https://dashboard-imoveis.loop9.com.br
```

## Próximos Passos

- [ ] Notificações automáticas para leads quentes
- [ ] Integração com CRM (envio automático)
- [ ] Relatórios semanais via email
- [ ] Dashboard público para clientes visualizarem score
- [ ] IA para calcular score automaticamente baseado em NLP

## Suporte

Dúvidas sobre integração: consulte `ferramentas/registrar_lead.py` (código comentado)
