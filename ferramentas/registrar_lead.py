"""
Ferramenta para o Agente IA registrar leads no Dashboard
"""
import requests
import os
from typing import Optional

# Configurações (podem ser setadas via variáveis de ambiente)
DASHBOARD_URL = os.getenv('DASHBOARD_URL', 'http://localhost:5555')
API_KEY = os.getenv('DASHBOARD_API_KEY', 'dev-token-12345')

def registrar_lead(
    whatsapp: str,
    nome: str,
    imovel_id: Optional[int] = None,
    score: int = 0,
    agendou_visita: bool = False
) -> dict:
    """
    Registra ou atualiza lead no Dashboard de Imóveis

    Esta ferramenta deve ser usada pelo agente IA quando:
    - Cliente demonstra interesse em um imóvel específico
    - Cliente faz perguntas que aumentam o score (preço, visita, etc)
    - Cliente agenda visita

    Args:
        whatsapp (str): Número WhatsApp (apenas dígitos, ex: "5531999887766")
        nome (str): Nome do cliente
        imovel_id (int, optional): ID do imóvel de interesse
        score (int): Score de 0 a 100
            - 0-30: Lead frio ❄️
            - 31-60: Lead morno 🌡️
            - 61-100: Lead quente 🔥
        agendou_visita (bool): True se cliente agendou visita

    Returns:
        dict: {
            "success": bool,
            "lead_id": int,
            "acao": "created" ou "updated",
            "score": int
        }

    Exemplos de uso:

        # Cliente perguntou sobre um imóvel (primeira mensagem)
        >>> registrar_lead(
        ...     whatsapp="5531999887766",
        ...     nome="João Silva",
        ...     imovel_id=1,
        ...     score=10
        ... )

        # Cliente perguntou preço (aumenta score)
        >>> registrar_lead(
        ...     whatsapp="5531999887766",
        ...     nome="João Silva",
        ...     imovel_id=1,
        ...     score=25
        ... )

        # Cliente agendou visita (score alto)
        >>> registrar_lead(
        ...     whatsapp="5531999887766",
        ...     nome="João Silva",
        ...     imovel_id=1,
        ...     score=55,
        ...     agendou_visita=True
        ... )
    """
    # Validações
    if not whatsapp or not nome:
        return {
            "success": False,
            "error": "whatsapp e nome são obrigatórios"
        }

    if score < 0 or score > 100:
        return {
            "success": False,
            "error": "score deve estar entre 0 e 100"
        }

    # Limpar whatsapp
    whatsapp = str(whatsapp).replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')

    # Preparar payload
    payload = {
        "whatsapp": whatsapp,
        "nome": nome,
        "score": score,
        "agendou_visita": agendou_visita
    }

    if imovel_id is not None:
        payload["imovel_id"] = imovel_id

    # Headers com autenticação
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        # Fazer request para o dashboard
        url = f"{DASHBOARD_URL}/api/leads/registrar"
        response = requests.post(url, json=payload, headers=headers, timeout=10)

        # Retornar resposta
        if response.status_code in [200, 201]:
            return response.json()
        else:
            return {
                "success": False,
                "error": f"Erro HTTP {response.status_code}: {response.text}"
            }

    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": f"Não foi possível conectar ao dashboard em {DASHBOARD_URL}"
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Timeout ao conectar ao dashboard"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Erro inesperado: {str(e)}"
        }


# Exemplo de uso direto (para testes)
if __name__ == '__main__':
    # Teste 1: Criar novo lead
    print("Teste 1: Criar novo lead")
    resultado = registrar_lead(
        whatsapp="5531999887766",
        nome="João Silva Teste",
        imovel_id=1,
        score=15,
        agendou_visita=False
    )
    print(resultado)
    print()

    # Teste 2: Atualizar score
    print("Teste 2: Atualizar score (cliente perguntou preço)")
    resultado = registrar_lead(
        whatsapp="5531999887766",
        nome="João Silva Teste",
        imovel_id=1,
        score=30,
        agendou_visita=False
    )
    print(resultado)
    print()

    # Teste 3: Cliente agendou visita
    print("Teste 3: Cliente agendou visita")
    resultado = registrar_lead(
        whatsapp="5531999887766",
        nome="João Silva Teste",
        imovel_id=1,
        score=60,
        agendou_visita=True
    )
    print(resultado)
