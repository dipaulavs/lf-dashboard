# 📅 API Agendamento - Endpoints para Agente IA

Dois endpoints simplificados para o agente IA gerenciar agendamentos de visitas.

---

## 🔍 1. Consultar Agenda Disponível

**Endpoint:** `GET /api/agente/consultar-agenda`
**Autenticação:** Bearer Token

### Parâmetros (Query String)

| Parâmetro | Tipo | Obrigatório | Padrão | Descrição |
|-----------|------|-------------|--------|-----------|
| `data` | string (YYYY-MM-DD) | ❌ | hoje | Data inicial para consulta |
| `dias` | integer | ❌ | 7 | Quantos dias à frente consultar |

### Exemplo 1: Consultar próximos 7 dias (padrão)

```bash
curl -X GET "http://localhost:5555/api/agente/consultar-agenda" \
  -H "Authorization: Bearer dev-token-12345"
```

### Exemplo 2: Consultar data específica + 14 dias

```bash
curl -X GET "http://localhost:5555/api/agente/consultar-agenda?data=2025-01-15&dias=14" \
  -H "Authorization: Bearer dev-token-12345"
```

### Resposta de Sucesso

```json
{
  "success": true,
  "periodo": {
    "inicio": "2025-01-10",
    "fim": "2025-01-17",
    "dias": 7
  },
  "regras_agendamento": "Horários disponíveis: 09:00-12:00 e 14:00-18:00. Sábados só pela manhã.",
  "total_agendamentos": 3,
  "agenda": {
    "2025-01-10": [
      {
        "hora": "10:00",
        "cliente": "João Silva",
        "imovel_id": 1,
        "status": "confirmado"
      }
    ],
    "2025-01-12": [
      {
        "hora": "14:00",
        "cliente": "Maria Santos",
        "imovel_id": 2,
        "status": "agendado"
      },
      {
        "hora": "16:00",
        "cliente": "Pedro Oliveira",
        "imovel_id": 1,
        "status": "agendado"
      }
    ]
  },
  "mensagem": "Agenda consultada de 10/01/2025 até 17/01/2025"
}
```

### Como Usar na IA

O agente deve:
1. Consultar a agenda ANTES de propor horários ao cliente
2. Ler as `regras_agendamento` para respeitar horários disponíveis
3. Verificar a `agenda` para evitar conflitos de horário
4. Propor horários livres baseado nas informações retornadas

---

## ✅ 2. Agendar Visita

**Endpoint:** `POST /api/agente/agendar-visita`
**Autenticação:** Bearer Token
**Content-Type:** application/json

### Body JSON

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `nome_cliente` | string | ✅ | Nome completo do cliente |
| `whatsapp` | string | ✅ | WhatsApp (com ou sem +55) |
| `imovel_id` | integer | ✅ | ID do imóvel consultado |
| `data_visita` | string (YYYY-MM-DD) | ✅ | Data da visita |
| `hora_visita` | string (HH:MM) | ✅ | Hora da visita (formato 24h) |
| `observacoes` | string | ❌ | Observações sobre o agendamento |

### Exemplo: Agendar visita

```bash
curl -X POST "http://localhost:5555/api/agente/agendar-visita" \
  -H "Authorization: Bearer dev-token-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "nome_cliente": "João Silva",
    "whatsapp": "5531999887766",
    "imovel_id": 1,
    "data_visita": "2025-01-15",
    "hora_visita": "14:00",
    "observacoes": "Cliente preferiu horário da tarde"
  }'
```

### Resposta de Sucesso (201 Created)

```json
{
  "success": true,
  "agendamento_id": 42,
  "mensagem": "Visita agendada com sucesso para 15/01/2025 às 14:00",
  "detalhes": {
    "cliente": "João Silva",
    "whatsapp": "5531999887766",
    "imovel": "Casa 3 quartos Betim",
    "data": "15/01/2025",
    "hora": "14:00"
  }
}
```

### Resposta de Erro (400 Bad Request)

```json
{
  "success": false,
  "error": "Campo \"data_visita\" é obrigatório"
}
```

### Resposta de Erro (404 Not Found)

```json
{
  "success": false,
  "error": "Imóvel ID 999 não encontrado"
}
```

### Efeitos Colaterais

Quando uma visita é agendada com sucesso:
1. ✅ Agendamento criado na tabela `agendamentos`
2. ✅ Lead atualizado/criado na tabela `leads`
3. ✅ Campo `agendou_visita` = `true`
4. ✅ Score atualizado para `90` (lead quente 🔥)

---

## 🤖 Fluxo Recomendado para o Agente

```
Cliente: "Quero agendar uma visita"
   │
   ├──> 1. CONSULTAR AGENDA
   │       GET /api/agente/consultar-agenda?dias=7
   │       └─> Verificar horários livres + regras
   │
   ├──> 2. PROPOR HORÁRIOS
   │       Baseado na agenda disponível
   │       Ex: "Tenho disponível: Terça 14h, Quarta 10h, Quinta 16h"
   │
   └──> 3. AGENDAR VISITA
          Cliente escolhe: "Quarta 10h"
          POST /api/agente/agendar-visita
          └─> Confirmar agendamento ao cliente
```

---

## 🔐 Autenticação

Token padrão: `dev-token-12345`

```bash
-H "Authorization: Bearer dev-token-12345"
```

**IMPORTANTE:** Trocar token em produção via variável `API_KEY` no `.env`

---

## 🧪 Testar Rapidamente

### 1. Iniciar servidor
```bash
cd SWARM/automations/dashboard-imoveis
python3 app.py
```

### 2. Consultar agenda
```bash
curl -X GET "http://localhost:5555/api/agente/consultar-agenda" \
  -H "Authorization: Bearer dev-token-12345"
```

### 3. Agendar visita de teste
```bash
curl -X POST "http://localhost:5555/api/agente/agendar-visita" \
  -H "Authorization: Bearer dev-token-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "nome_cliente": "Teste Cliente",
    "whatsapp": "5531999999999",
    "imovel_id": 1,
    "data_visita": "2025-11-15",
    "hora_visita": "10:00",
    "observacoes": "Teste automático"
  }'
```

---

## ✅ Checklist Integração Innoitune

**Tool 1: Consultar Agenda**
- ✅ URL: `https://seu-dominio.com/api/agente/consultar-agenda`
- ✅ Method: `GET`
- ✅ Headers: `Authorization: Bearer dev-token-12345`
- ✅ Descrição: "Consulta agenda disponível dos próximos 7 dias"

**Tool 2: Agendar Visita**
- ✅ URL: `https://seu-dominio.com/api/agente/agendar-visita`
- ✅ Method: `POST`
- ✅ Headers: `Authorization: Bearer dev-token-12345`, `Content-Type: application/json`
- ✅ Body: `{"nome_cliente":"{{customer_name}}","whatsapp":"{{whatsapp}}","imovel_id":{{property_id}},"data_visita":"{{visit_date}}","hora_visita":"{{visit_time}}","observacoes":"{{notes}}"}`
- ✅ Descrição: "Agenda visita para cliente em imóvel específico"

---

**Desenvolvido para integração com Innoitune Agent** 🤖
