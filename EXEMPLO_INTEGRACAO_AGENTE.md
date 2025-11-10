# Exemplo de Integração com Agente IA (Innoitune)

Este documento mostra como integrar o sistema de score/tags com um agente IA que responde clientes via WhatsApp.

## Fluxo de Integração

```
1. Cliente envia mensagem no WhatsApp
2. Evolution API → Webhook → Agente IA
3. Agente processa mensagem
4. Agente calcula score baseado na conversa
5. Agente usa ferramenta registrar_lead()
6. Dashboard atualiza automaticamente
```

## Exemplo de Código do Agente

```python
import sys
sys.path.append('/caminho/para/dashboard-imoveis')

from ferramentas.registrar_lead import registrar_lead

class AgenteImoveis:
    def __init__(self):
        self.scores_cache = {}  # Cache de scores atuais

    def processar_mensagem(self, whatsapp, nome, mensagem):
        """
        Processa mensagem do cliente e atualiza score
        """
        # Obter score atual do cache
        score_atual = self.scores_cache.get(whatsapp, 0)

        # Analisar mensagem e calcular incremento
        incremento = self._calcular_incremento(mensagem)
        novo_score = min(score_atual + incremento, 100)

        # Detectar se agendou visita
        agendou_visita = self._detectou_agendamento(mensagem)

        # Detectar imóvel mencionado
        imovel_id = self._detectar_imovel(mensagem)

        # Registrar no dashboard
        resultado = registrar_lead(
            whatsapp=whatsapp,
            nome=nome,
            imovel_id=imovel_id,
            score=novo_score,
            agendou_visita=agendou_visita
        )

        if resultado['success']:
            # Atualizar cache
            self.scores_cache[whatsapp] = novo_score

            # Log para debug
            print(f"✅ Lead atualizado: {nome} - Score: {score_atual} → {novo_score}")

            # Notificar equipe se virou lead quente
            if score_atual < 61 and novo_score >= 61:
                self._notificar_equipe_lead_quente(whatsapp, nome, imovel_id)

        return resultado

    def _calcular_incremento(self, mensagem):
        """
        Analisa mensagem e retorna pontos a adicionar
        """
        mensagem_lower = mensagem.lower()

        # Primeira mensagem
        if any(palavra in mensagem_lower for palavra in ['oi', 'olá', 'bom dia', 'boa tarde']):
            return 5

        # Perguntou preço
        if any(palavra in mensagem_lower for palavra in ['quanto custa', 'valor', 'preço', 'quanto é']):
            return 10

        # Pediu fotos/vídeos
        if any(palavra in mensagem_lower for palavra in ['foto', 'imagem', 'vídeo', 'ver mais']):
            return 10

        # Perguntou sobre financiamento
        if any(palavra in mensagem_lower for palavra in ['financiamento', 'parcela', 'entrada', 'banco']):
            return 15

        # Perguntou endereço
        if any(palavra in mensagem_lower for palavra in ['endereço', 'onde fica', 'localização', 'como chegar']):
            return 20

        # Marcou visita
        if self._detectou_agendamento(mensagem):
            return 30

        return 0

    def _detectou_agendamento(self, mensagem):
        """
        Detecta se cliente quer agendar visita
        """
        mensagem_lower = mensagem.lower()
        palavras_chave = [
            'agendar', 'visita', 'visitar', 'conhecer pessoalmente',
            'quero ver', 'posso ver', 'quando posso', 'horário'
        ]

        return any(palavra in mensagem_lower for palavra in palavras_chave)

    def _detectar_imovel(self, mensagem):
        """
        Detecta qual imóvel o cliente está interessado
        """
        mensagem_lower = mensagem.lower()

        # Mapear palavras-chave para IDs de imóveis
        mapeamento = {
            'chácara': 1,
            'itatiaiuçu': 1,
            'casa': 2,
            'barreiro': 2,
            'apartamento': 3,
            'centro': 3
        }

        for palavra, imovel_id in mapeamento.items():
            if palavra in mensagem_lower:
                return imovel_id

        return None

    def _notificar_equipe_lead_quente(self, whatsapp, nome, imovel_id):
        """
        Notifica equipe quando lead fica quente (score >= 61)
        """
        mensagem_notificacao = f"""
🔥 LEAD QUENTE DETECTADO!

Nome: {nome}
WhatsApp: {whatsapp}
Imóvel: ID {imovel_id}
Score: >= 61

Ação recomendada: Priorizar atendimento
        """

        print(mensagem_notificacao)
        # Aqui você pode enviar email, Telegram, Slack, etc.


# ==================== EXEMPLO DE USO ====================

if __name__ == '__main__':
    agente = AgenteImoveis()

    # Simulação de conversa com cliente

    print("=" * 60)
    print("CONVERSA 1: Lead Frio")
    print("=" * 60)

    agente.processar_mensagem(
        whatsapp="5531999887766",
        nome="João Silva",
        mensagem="Oi, bom dia!"
    )
    # Score: 0 → 5 (primeira mensagem)

    print("\n" + "=" * 60)
    print("CONVERSA 2: Lead Morno")
    print("=" * 60)

    agente.processar_mensagem(
        whatsapp="5531999887766",
        nome="João Silva",
        mensagem="Quanto custa a chácara em Itatiaiuçu?"
    )
    # Score: 5 → 15 (perguntou preço)

    agente.processar_mensagem(
        whatsapp="5531999887766",
        nome="João Silva",
        mensagem="Tem fotos da propriedade?"
    )
    # Score: 15 → 25 (pediu fotos)

    agente.processar_mensagem(
        whatsapp="5531999887766",
        nome="João Silva",
        mensagem="Aceita financiamento?"
    )
    # Score: 25 → 40 (perguntou financiamento)

    print("\n" + "=" * 60)
    print("CONVERSA 3: Lead Quente")
    print("=" * 60)

    agente.processar_mensagem(
        whatsapp="5531999887766",
        nome="João Silva",
        mensagem="Onde fica exatamente?"
    )
    # Score: 40 → 60 (perguntou endereço)

    agente.processar_mensagem(
        whatsapp="5531999887766",
        nome="João Silva",
        mensagem="Quero agendar uma visita para amanhã"
    )
    # Score: 60 → 90 (marcou visita)
    # Notificação enviada: LEAD QUENTE!
```

## Integração com Innoitune (HTTP Request Node)

### Configuração no Innoitune

1. **Adicionar HTTP Request Tool ao agente**

2. **Configurar endpoint:**
   - URL: `https://dashboard-imoveis.loop9.com.br/api/leads/registrar`
   - Método: POST
   - Headers:
     ```
     Authorization: Bearer dev-token-12345
     Content-Type: application/json
     ```

3. **Body (JSON):**
   ```json
   {
     "whatsapp": "{{whatsapp_number}}",
     "nome": "{{customer_name}}",
     "imovel_id": {{imovel_id}},
     "score": {{calculated_score}},
     "agendou_visita": {{scheduled_visit}}
   }
   ```

4. **Variáveis do agente:**
   - `whatsapp_number`: Extraído do webhook Evolution
   - `customer_name`: Nome do contato
   - `imovel_id`: Detectado via NLP
   - `calculated_score`: Calculado pelo agente
   - `scheduled_visit`: true/false

### Exemplo de Prompt do Agente

```
Você é um assistente de vendas de imóveis.

INSTRUÇÕES:

1. Analise a mensagem do cliente
2. Identifique o imóvel de interesse (use IDs: 1=Chácara, 2=Casa, 3=Apartamento)
3. Calcule o score baseado nas ações:
   - Primeira mensagem: +5
   - Perguntou preço: +10
   - Pediu fotos: +10
   - Perguntou financiamento: +15
   - Perguntou endereço: +20
   - Marcou visita: +30

4. Após cada mensagem, USE A FERRAMENTA registrar_lead com:
   - whatsapp: número do cliente
   - nome: nome do cliente
   - imovel_id: ID do imóvel mencionado
   - score: score acumulado
   - agendou_visita: true se mencionou agendar/visitar

5. Responda ao cliente de forma natural e amigável

EXEMPLO:
Cliente: "Oi, quanto custa a chácara?"
Você:
  1. Identifica: imovel_id = 1 (chácara)
  2. Calcula: score = 5 (primeira msg) + 10 (preço) = 15
  3. USA FERRAMENTA: registrar_lead(whatsapp="...", nome="...", imovel_id=1, score=15, agendou_visita=false)
  4. Responde: "Olá! A chácara em Itatiaiuçu está R$ 65.000. Quer saber mais detalhes?"
```

## Testando a Integração

### 1. Iniciar Dashboard

```bash
cd SWARM/automations/dashboard-imoveis
python3 app.py
```

### 2. Executar script de teste

```bash
python3 EXEMPLO_INTEGRACAO_AGENTE.md  # (copiar código Python acima)
```

### 3. Verificar no Dashboard

```
1. Acessar http://localhost:5555
2. Clicar na aba "Leads"
3. Ver lead "João Silva" com score 90 🔥
4. Ver gráfico atualizado
```

### 4. Exportar dados

```
1. Filtrar: Leads Quentes (61-100)
2. Clicar "Exportar CSV"
3. Arquivo baixado: leads_2025-11-09.csv
```

## Boas Práticas

### 1. Cache de Scores

Sempre manter cache local para evitar múltiplas queries:

```python
self.scores_cache[whatsapp] = novo_score
```

### 2. Validação de Dados

```python
# Limpar WhatsApp
whatsapp = whatsapp.replace('+', '').replace(' ', '').replace('-', '')

# Validar nome
if not nome or len(nome) < 2:
    nome = "Cliente Sem Nome"
```

### 3. Tratamento de Erros

```python
resultado = registrar_lead(...)

if not resultado['success']:
    print(f"❌ Erro ao registrar lead: {resultado.get('error')}")
    # Tentar novamente ou logar erro
```

### 4. Limites de Score

```python
# Nunca ultrapassar 100
novo_score = min(score_atual + incremento, 100)
```

## Métricas para Acompanhar

1. **Taxa de conversão score → agendamento**
   - Quantos leads de score X agendaram visita?

2. **Tempo médio até lead quente**
   - Quantas mensagens até score 61?

3. **Imóveis mais populares**
   - Qual imóvel gera mais leads?

4. **Taxa de abandono**
   - Leads que pararam de responder (score estagnado)

## Troubleshooting

### Erro: "Connection refused"

```bash
# Verificar se dashboard está rodando
ps aux | grep app.py

# Verificar porta
lsof -i :5555
```

### Erro: "API Key inválida"

```bash
# Verificar token na ferramenta
cat ferramentas/registrar_lead.py | grep API_KEY

# Verificar token no app.py
cat app.py | grep API_KEY
```

### Lead não aparece no dashboard

```bash
# Verificar banco de dados
sqlite3 data/dashboard.db "SELECT * FROM leads;"

# Verificar logs
tail -f logs/app.log  # se configurado
```

## Conclusão

Com esta integração, você tem:

✅ Score automático baseado em conversas
✅ Dashboard visual em tempo real
✅ Filtros e exportação de leads
✅ Gráficos para análise
✅ Priorização automática de atendimento

**Próximo passo:** Implementar no seu agente IA e começar a capturar leads!
