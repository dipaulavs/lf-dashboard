"""
Testes para Rate Limiter e Proteções de API
Valida comportamento de rate limiting, deduplicação e retry
"""
import pytest
import time
from rate_limiter import RateLimiter


class TestRateLimiter:
    """Testes do rate limiter básico"""

    def test_permite_requisicoes_dentro_do_limite(self):
        """Deve permitir requisições dentro do limite configurado"""
        limiter = RateLimiter(max_requests=5, window_seconds=1)

        # 5 requisições devem passar
        for i in range(5):
            allowed, reason = limiter.is_allowed("client1")
            assert allowed is True, f"Requisição {i+1} deveria ser permitida"
            assert reason is None

    def test_bloqueia_apos_exceder_limite(self):
        """Deve bloquear após exceder o limite"""
        limiter = RateLimiter(max_requests=3, window_seconds=1)

        # 3 passam
        for _ in range(3):
            allowed, _ = limiter.is_allowed("client1")
            assert allowed is True

        # 4ª é bloqueada
        allowed, reason = limiter.is_allowed("client1")
        assert allowed is False
        assert reason == "rate_limit"

    def test_clientes_independentes(self):
        """Limites devem ser independentes por cliente"""
        limiter = RateLimiter(max_requests=2, window_seconds=1)

        # Cliente 1: 2 requisições
        for _ in range(2):
            allowed, _ = limiter.is_allowed("client1")
            assert allowed is True

        # Cliente 2: também pode fazer 2
        for _ in range(2):
            allowed, _ = limiter.is_allowed("client2")
            assert allowed is True

        # Ambos bloqueados na 3ª
        assert limiter.is_allowed("client1")[0] is False
        assert limiter.is_allowed("client2")[0] is False

    def test_janela_deslizante_permite_novas_requisicoes(self):
        """Após janela expirar, deve permitir novas requisições"""
        limiter = RateLimiter(max_requests=2, window_seconds=0.1)  # 100ms

        # Esgotar limite
        limiter.is_allowed("client1")
        limiter.is_allowed("client1")

        # 3ª bloqueada
        allowed, _ = limiter.is_allowed("client1")
        assert allowed is False

        # Aguardar janela expirar
        time.sleep(0.15)

        # Agora deve permitir
        allowed, _ = limiter.is_allowed("client1")
        assert allowed is True

    def test_estatisticas_retornam_valores_corretos(self):
        """Stats devem refletir estado atual"""
        limiter = RateLimiter(max_requests=5, window_seconds=1)

        # Fazer 3 requisições
        for _ in range(3):
            limiter.is_allowed("client1")

        stats = limiter.get_stats("client1")

        assert stats["requests_in_window"] == 3
        assert stats["max_requests"] == 5
        assert stats["remaining"] == 2
        assert stats["window_seconds"] == 1


class TestDeduplication:
    """Testes de deduplicação de requisições"""

    def test_detecta_requisicoes_duplicadas(self):
        """Deve detectar requisições idênticas"""
        limiter = RateLimiter(dedup_window_seconds=1)

        request1 = {"whatsapp": "5531999887766", "score": 45}
        request2 = {"whatsapp": "5531999887766", "score": 45}

        # Primeira requisição
        is_dup, hash1 = limiter.is_duplicate(request1)
        assert is_dup is False

        # Segunda requisição (idêntica)
        is_dup, hash2 = limiter.is_duplicate(request2)
        assert is_dup is True
        assert hash1 == hash2

    def test_permite_requisicoes_diferentes(self):
        """Requisições diferentes devem passar"""
        limiter = RateLimiter(dedup_window_seconds=1)

        request1 = {"whatsapp": "5531999887766", "score": 45}
        request2 = {"whatsapp": "5531999887766", "score": 50}  # Score diferente

        is_dup, _ = limiter.is_duplicate(request1)
        assert is_dup is False

        is_dup, _ = limiter.is_duplicate(request2)
        assert is_dup is False  # Score diferente = requisição diferente

    def test_deduplicacao_expira_apos_janela(self):
        """Após janela expirar, mesma requisição deve passar"""
        limiter = RateLimiter(dedup_window_seconds=0.1)  # 100ms

        request = {"whatsapp": "5531999887766", "score": 45}

        # Primeira requisição
        is_dup, _ = limiter.is_duplicate(request)
        assert is_dup is False

        # Imediatamente duplicada
        is_dup, _ = limiter.is_duplicate(request)
        assert is_dup is True

        # Aguardar janela expirar
        time.sleep(0.15)

        # Agora deve permitir novamente
        is_dup, _ = limiter.is_duplicate(request)
        assert is_dup is False

    def test_ordem_dos_parametros_nao_importa(self):
        """Ordem dos parâmetros não deve afetar detecção"""
        limiter = RateLimiter(dedup_window_seconds=1)

        request1 = {"whatsapp": "123", "score": 45, "nome": "João"}
        request2 = {"score": 45, "nome": "João", "whatsapp": "123"}  # Ordem diferente

        is_dup, hash1 = limiter.is_duplicate(request1)
        assert is_dup is False

        is_dup, hash2 = limiter.is_duplicate(request2)
        assert is_dup is True  # Mesmos valores = duplicata
        assert hash1 == hash2


class TestCheckRequest:
    """Testes da verificação combinada (rate limit + dedup)"""

    def test_bloqueia_por_rate_limit_primeiro(self):
        """Rate limit deve ser verificado antes de dedup"""
        limiter = RateLimiter(max_requests=1, window_seconds=1)

        # 1ª requisição: passa
        allowed, reason = limiter.check_request(
            "client1",
            {"whatsapp": "123", "score": 45}
        )
        assert allowed is True

        # 2ª requisição: bloqueada por rate limit (não dedup)
        allowed, reason = limiter.check_request(
            "client1",
            {"whatsapp": "456", "score": 50}  # Dados diferentes
        )
        assert allowed is False
        assert reason == "rate_limit"

    def test_bloqueia_por_deduplicacao(self):
        """Deve bloquear requisições duplicadas"""
        limiter = RateLimiter(max_requests=10, dedup_window_seconds=1)

        request_data = {"whatsapp": "123", "score": 45}

        # 1ª: passa
        allowed, reason = limiter.check_request("client1", request_data)
        assert allowed is True

        # 2ª: mesmos dados = duplicata
        allowed, reason = limiter.check_request("client1", request_data)
        assert allowed is False
        assert reason == "duplicate"

    def test_permite_sem_deduplicacao(self):
        """Deve funcionar sem dados para dedup"""
        limiter = RateLimiter(max_requests=5)

        # Sem request_data = apenas rate limit
        for _ in range(5):
            allowed, reason = limiter.check_request("client1")
            assert allowed is True

        # 6ª bloqueada
        allowed, reason = limiter.check_request("client1")
        assert allowed is False
        assert reason == "rate_limit"


class TestThreadSafety:
    """Testes de thread safety (importância em Flask)"""

    def test_multiplos_clientes_simultaneos(self):
        """Deve suportar múltiplos clientes sem race conditions"""
        limiter = RateLimiter(max_requests=3, window_seconds=1)

        # Simular 3 clientes fazendo requisições
        clients = ["client1", "client2", "client3"]

        for client in clients:
            for _ in range(3):
                allowed, _ = limiter.is_allowed(client)
                assert allowed is True

        # Todos devem estar no limite
        for client in clients:
            allowed, _ = limiter.is_allowed(client)
            assert allowed is False


# Fixture para limpar estado entre testes
@pytest.fixture(autouse=True)
def cleanup():
    """Limpa estado antes de cada teste"""
    yield
    # Cleanup após teste se necessário


if __name__ == "__main__":
    # Permite rodar com: python test_rate_limiter.py
    pytest.main([__file__, "-v", "--tb=short"])
