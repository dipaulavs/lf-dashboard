# 🏠 L&F Imóveis - Dashboard

Dashboard profissional para gestão de imóveis e leads com integração de agente IA.

## ✨ Features

- **📦 Gestão de Imóveis:** CRUD completo de propriedades
- **👥 Gestão de Leads:** Sistema de scoring e acompanhamento
- **📅 Agenda do Corretor:** Agendamento de visitas com sincronização
- **🤖 API para Agente IA:** Endpoints REST para integração com Innoitune
- **📊 Analytics:** Gráficos e métricas em tempo real

## 🎨 Design

Design inspirado em **MotherDuck Style:**
- Cores: Beige warm + Yellow accent + Dark gray
- Tipografia: SF Mono (monospace) + Inter (sans-serif)
- Bordas: Sharp (2px solid)
- Efeitos: Offset shadows ao hover

## 🚀 Quick Start

### Local Development

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar servidor
python3 app.py

# Acessar dashboard
open http://localhost:5555
```

### Docker

```bash
# Build
docker build -t lf-dashboard .

# Run
docker run -p 5555:5555 -v $(pwd)/data:/app/data lf-dashboard
```

## 📡 API Endpoints

### Dashboard (Público)

- `GET /api/imoveis` - Listar imóveis
- `POST /api/imoveis` - Criar imóvel
- `PUT /api/imoveis/:id` - Atualizar imóvel
- `DELETE /api/imoveis/:id` - Deletar imóvel
- `GET /api/agenda/agendamentos` - Listar agendamentos
- `POST /api/agenda/observacoes` - Salvar observações

### Agente IA (Autenticado)

- `GET /api/agente/consultar-agenda` - Consultar agenda disponível
- `POST /api/agente/agendar-visita` - Agendar visita automaticamente

**API Key:** `dev-token-12345` (configurar no app.py)

## 🔧 Configuração

```bash
# Criar arquivo .env (opcional)
FLASK_PORT=5555
API_KEY=dev-token-12345
```

## 📂 Estrutura

```
dashboard-imoveis/
├── app.py              # Flask app principal
├── database.py         # SQLite ORM
├── static/
│   ├── index.html      # Dashboard SPA
│   ├── style.css       # MotherDuck style
│   ├── script.js       # Gestão de imóveis
│   ├── leads_v2.js     # Gestão de leads
│   └── agenda.js       # Sistema de agenda
├── data/
│   ├── imoveis.json    # Índice de imóveis
│   └── leads.db        # Banco SQLite
└── requirements.txt
```

## 🛠️ Tecnologias

- **Backend:** Python 3 + Flask + SQLite
- **Frontend:** Vanilla JS + MotherDuck CSS
- **Deploy:** Docker + Traefik + SSL automático

## 📝 License

MIT

---

**Desenvolvido para L&F Imóveis** 🏡
