# Dashboard de Imóveis - Sistema Completo

Dashboard profissional para gestão de leads e agendamentos de visitas em imobiliárias, com sistema de pontuação (score) e integração via API REST.

## Status: ✅ PRODUÇÃO

**Última atualização:** 2025-11-10
**Versão:** 1.1.0 🆕
**URL Produção:** https://untwilled-unsymptomatical-bayleigh.ngrok-free.dev

---

## 🎯 Funcionalidades Implementadas

### ✅ Sistema de Leads
- Score 0-100 automático baseado em interações
- Tags automáticas: Frio (0-30), Morno (31-60), Quente (61-100)
- Histórico completo de mudanças
- Filtros avançados por score/imóvel/status
- Exportação CSV
- **🗑️ Deletar leads com 1 clique (sem popup, atualização automática)**

### ✅ Sistema de Agenda
- Agendamento de visitas (CRUD completo)
- Consulta inteligente de disponibilidade
- Regras de negócio configuráveis
- Estatísticas de agendamentos
- **🗑️ Deletar agendamentos com 1 clique (sem popup, atualização automática)**

### ✅ Dashboard Visual
- Aba Leads: gráficos + tabela interativa + botão deletar
- Aba Agenda: calendário + lista + botão deletar
- Aba Imóveis: gestão de propriedades
- Totalmente responsivo

---

## 🚀 Endpoints API - Quick Reference

### LEADS (GET - Campos Separados)

```bash
# 1. Definir Imóvel (OBRIGATÓRIO PRIMEIRO)
GET /api/leads/imovel?whatsapp=5531999887766&nome=João Silva&imovel_id=4

# 2. Atualizar Score (REQUER: nome + imovel_id)
GET /api/leads/score?whatsapp=5531999887766&nome=João Silva&imovel_id=4&score=45

# 3. Marcar Flag Agendamento
GET /api/leads/agendar?whatsapp=5531999887766&nome=João Silva&agendou=true

# 4. Deletar Lead
DELETE /api/leads/5531999887766
```

### AGENDA (Agente IA)

```bash
# 1. Consultar Agenda
GET /api/agente/consultar-agenda?dias=7

# 2. Agendar Visita
POST /api/agente/agendar-visita
{
  "nome_cliente": "João Silva",
  "whatsapp": "5531999887766",
  "imovel_id": 4,
  "data_visita": "2025-01-22",
  "hora_visita": "10:00",
  "observacoes": "Cliente preferiu manhã"
}

# 3. Deletar Agendamento
DELETE /api/agenda/agendamentos/{id}
```

**Authorization:** `Bearer dev-token-12345` (todos endpoints)

---

## ⚡ Quick Start

```bash
# Local
cd SWARM/automations/dashboard-imoveis
python3 app.py
# Acesse: http://localhost:5555

# Produção (ngrok)
python3 app.py &
ngrok http 5555
```

---

## 🤖 Fluxo de Integração com Agente IA

```
Cliente WhatsApp → Agente IA → Dashboard API

1. Lead inicia conversa + captura nome
   → Aguarda identificar interesse em imóvel

2. Lead pergunta sobre imóvel (PRIMEIRO REGISTRO)
   → GET /api/leads/imovel?whatsapp=XXX&nome=João Silva&imovel_id=4
   ✅ Lead registrado com dados mínimos

3. Lead demonstra interesse (ATUALIZAR SCORE)
   → GET /api/leads/score?whatsapp=XXX&nome=João Silva&imovel_id=4&score=35
   ✅ Score atualizado (REQUER nome + imovel_id)

4. Lead quer agendar
   → GET /api/agente/consultar-agenda?dias=7
   → POST /api/agente/agendar-visita
   → GET /api/leads/agendar?whatsapp=XXX&nome=João Silva&agendou=true
   → GET /api/leads/score?whatsapp=XXX&nome=João Silva&imovel_id=4&score=90
```

---

## 🗄️ Banco de Dados

**Arquivo:** `data/dashboard.db` (SQLite)

**Tabelas:**
- `leads` - Leads com score e flag agendamento
- `agendamentos` - Visitas agendadas
- `score_historico` - Rastreamento de mudanças
- `configuracoes` - Regras de negócio

---

## 📊 Imóveis Cadastrados (8 total)

- **ID 4:** Apartamento Leblon Vista Mar - R$ 2.5M
- **ID 5:** Casa Barra Condomínio - R$ 1.8M  
- **ID 6:** Cobertura Ipanema Duplex - R$ 4.2M
- **ID 7:** Apartamento Copacabana - R$ 1.2M
- **ID 8:** Chácara Itatiaiuçu 5000m² - R$ 850K

---

## 🔄 Status dos Componentes

| Componente | Status | Validação |
|------------|--------|-----------|
| API Leads (score/imóvel/flag/delete) | ✅ Produção | ✅ Testado |
| API Agenda (consultar/agendar/delete) | ✅ Produção | ✅ Testado |
| Dashboard Frontend (com botões delete) | ✅ Produção | ✅ Testado |
| Banco SQLite | ✅ Produção | ✅ Testado |
| Integração ngrok | ✅ Produção | ✅ Testado |

---

## 📚 Documentação Completa

- **[README_LEADS.md](README_LEADS.md)** - Sistema de leads completo (score, tags, CSV)
- **[app.py](app.py)** - Código principal da API
- **[database.py](database.py)** - Estrutura do banco

---

## 🔑 Credenciais

- **API Key:** `dev-token-12345`
- **Porta:** `5555`
- **Database:** `data/dashboard.db`

---

## 🛠️ Stack Tecnológica

- Backend: Flask + Python 3
- Frontend: HTML + Vanilla JS
- Database: SQLite
- Gráficos: Chart.js
- Proxy: ngrok

---

## 📝 Changelog

### v1.1.0 - 2025-11-10 (NOVA VERSÃO)

**🗑️ Funcionalidade de Deletar Implementada**

- ✅ Botão deletar em Leads (coluna Ações)
- ✅ Botão deletar em Agendamentos (coluna Ações)
- ✅ DELETE sem popup de confirmação
- ✅ Atualização automática da tabela após delete
- ✅ Endpoint `DELETE /api/leads/{whatsapp}` com autenticação
- ✅ Endpoint `DELETE /api/agenda/agendamentos/{id}` sem autenticação
- ✅ Método `deletar_lead()` no database.py (remove lead + histórico)
- ✅ Função JavaScript `deletarLead()` e `deletarAgendamento()`

**Arquivos Modificados:**
- `static/index.html` - Adicionada coluna "Ações" nas tabelas
- `static/leads_v2.js` - Função `deletarLead()` + botão na renderização
- `static/agenda.js` - Função `deletarAgendamento()` já existia
- `database.py` - Método `deletar_lead(whatsapp)`
- `app.py` - Endpoints DELETE para leads e agendamentos

---

**🎯 Sistema 100% funcional e pronto para produção!**
