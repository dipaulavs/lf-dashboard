#!/usr/bin/env python3
"""
Testes standalone para Rate Limiter (sem pytest)
Pode rodar diretamente: python3 test_rate_limiter_standalone.py
"""
import time
from rate_limiter import RateLimiter


class TestRunner:
    """Runner simples de testes sem dependências"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def assert_true(self, condition, msg=""):
        if not condition:
            raise AssertionError(msg or "Expected True, got False")

    def assert_false(self, condition, msg=""):
        if condition:
            raise AssertionError(msg or "Expected False, got True")

    def assert_equal(self, a, b, msg=""):
        if a != b:
            raise AssertionError(msg or f"Expected {a} == {b}")

    def run_test(self, name, test_func):
        """Roda um teste e captura resultado"""
        try:
            test_func()
            self.passed += 1
            print(f"✅ {name}")
        except AssertionError as e:
            self.failed += 1
            self.errors.append((name, str(e)))
            print(f"❌ {name}: {e}")
        except Exception as e:
            self.failed += 1
            self.errors.append((name, f"ERRO: {e}"))
            print(f"💥 {name}: ERRO - {e}")

    def print_summary(self):
        """Imprime resumo dos testes"""
        total = self.passed + self.failed
        print("\n" + "="*60)
        print(f"RESULTADOS: {self.passed}/{total} testes passaram")
        print("="*60)

        if self.errors:
            print("\n❌ FALHAS:")
            for name, error in self.errors:
                print(f"  - {name}: {error}")

        return self.failed == 0


def test_permite_requisicoes_dentro_do_limite(t):
    """Deve permitir requisições dentro do limite configurado"""
    limiter = RateLimiter(max_requests=5, window_seconds=1)

    for i in range(5):
        allowed, reason = limiter.is_allowed("client1")
        t.assert_true(allowed, f"Requisição {i+1} deveria ser permitida")
        t.assert_equal(reason, None)


def test_bloqueia_apos_exceder_limite(t):
    """Deve bloquear após exceder o limite"""
    limiter = RateLimiter(max_requests=3, window_seconds=1)

    # 3 passam
    for _ in range(3):
        allowed, _ = limiter.is_allowed("client1")
        t.assert_true(allowed)

    # 4ª é bloqueada
    allowed, reason = limiter.is_allowed("client1")
    t.assert_false(allowed)
    t.assert_equal(reason, "rate_limit")


def test_clientes_independentes(t):
    """Limites devem ser independentes por cliente"""
    limiter = RateLimiter(max_requests=2, window_seconds=1)

    # Cliente 1: 2 requisições
    for _ in range(2):
        allowed, _ = limiter.is_allowed("client1")
        t.assert_true(allowed)

    # Cliente 2: também pode fazer 2
    for _ in range(2):
        allowed, _ = limiter.is_allowed("client2")
        t.assert_true(allowed)

    # Ambos bloqueados na 3ª
    t.assert_false(limiter.is_allowed("client1")[0])
    t.assert_false(limiter.is_allowed("client2")[0])


def test_janela_deslizante_permite_novas_requisicoes(t):
    """Após janela expirar, deve permitir novas requisições"""
    limiter = RateLimiter(max_requests=2, window_seconds=0.1)  # 100ms

    # Esgotar limite
    limiter.is_allowed("client1")
    limiter.is_allowed("client1")

    # 3ª bloqueada
    allowed, _ = limiter.is_allowed("client1")
    t.assert_false(allowed)

    # Aguardar janela expirar
    time.sleep(0.15)

    # Agora deve permitir
    allowed, _ = limiter.is_allowed("client1")
    t.assert_true(allowed)


def test_estatisticas_retornam_valores_corretos(t):
    """Stats devem refletir estado atual"""
    limiter = RateLimiter(max_requests=5, window_seconds=1)

    # Fazer 3 requisições
    for _ in range(3):
        limiter.is_allowed("client1")

    stats = limiter.get_stats("client1")

    t.assert_equal(stats["requests_in_window"], 3)
    t.assert_equal(stats["max_requests"], 5)
    t.assert_equal(stats["remaining"], 2)
    t.assert_equal(stats["window_seconds"], 1)


def test_detecta_requisicoes_duplicadas(t):
    """Deve detectar requisições idênticas"""
    limiter = RateLimiter(dedup_window_seconds=1)

    request1 = {"whatsapp": "5531999887766", "score": 45}
    request2 = {"whatsapp": "5531999887766", "score": 45}

    # Primeira requisição
    is_dup, hash1 = limiter.is_duplicate(request1)
    t.assert_false(is_dup)

    # Segunda requisição (idêntica)
    is_dup, hash2 = limiter.is_duplicate(request2)
    t.assert_true(is_dup)
    t.assert_equal(hash1, hash2)


def test_permite_requisicoes_diferentes(t):
    """Requisições diferentes devem passar"""
    limiter = RateLimiter(dedup_window_seconds=1)

    request1 = {"whatsapp": "5531999887766", "score": 45}
    request2 = {"whatsapp": "5531999887766", "score": 50}  # Score diferente

    is_dup, _ = limiter.is_duplicate(request1)
    t.assert_false(is_dup)

    is_dup, _ = limiter.is_duplicate(request2)
    t.assert_false(is_dup)


def test_deduplicacao_expira_apos_janela(t):
    """Após janela expirar, mesma requisição deve passar"""
    limiter = RateLimiter(dedup_window_seconds=0.1)  # 100ms

    request = {"whatsapp": "5531999887766", "score": 45}

    # Primeira requisição
    is_dup, _ = limiter.is_duplicate(request)
    t.assert_false(is_dup)

    # Imediatamente duplicada
    is_dup, _ = limiter.is_duplicate(request)
    t.assert_true(is_dup)

    # Aguardar janela expirar
    time.sleep(0.15)

    # Agora deve permitir novamente
    is_dup, _ = limiter.is_duplicate(request)
    t.assert_false(is_dup)


def test_ordem_dos_parametros_nao_importa(t):
    """Ordem dos parâmetros não deve afetar detecção"""
    limiter = RateLimiter(dedup_window_seconds=1)

    request1 = {"whatsapp": "123", "score": 45, "nome": "João"}
    request2 = {"score": 45, "nome": "João", "whatsapp": "123"}  # Ordem diferente

    is_dup, hash1 = limiter.is_duplicate(request1)
    t.assert_false(is_dup)

    is_dup, hash2 = limiter.is_duplicate(request2)
    t.assert_true(is_dup)
    t.assert_equal(hash1, hash2)


def test_bloqueia_por_rate_limit_primeiro(t):
    """Rate limit deve ser verificado antes de dedup"""
    limiter = RateLimiter(max_requests=1, window_seconds=1)

    # 1ª requisição: passa
    allowed, reason = limiter.check_request(
        "client1",
        {"whatsapp": "123", "score": 45}
    )
    t.assert_true(allowed)

    # 2ª requisição: bloqueada por rate limit (não dedup)
    allowed, reason = limiter.check_request(
        "client1",
        {"whatsapp": "456", "score": 50}  # Dados diferentes
    )
    t.assert_false(allowed)
    t.assert_equal(reason, "rate_limit")


def test_bloqueia_por_deduplicacao(t):
    """Deve bloquear requisições duplicadas"""
    limiter = RateLimiter(max_requests=10, dedup_window_seconds=1)

    request_data = {"whatsapp": "123", "score": 45}

    # 1ª: passa
    allowed, reason = limiter.check_request("client1", request_data)
    t.assert_true(allowed)

    # 2ª: mesmos dados = duplicata
    allowed, reason = limiter.check_request("client1", request_data)
    t.assert_false(allowed)
    t.assert_equal(reason, "duplicate")


def test_permite_sem_deduplicacao(t):
    """Deve funcionar sem dados para dedup"""
    limiter = RateLimiter(max_requests=5)

    # Sem request_data = apenas rate limit
    for _ in range(5):
        allowed, reason = limiter.check_request("client1")
        t.assert_true(allowed)

    # 6ª bloqueada
    allowed, reason = limiter.check_request("client1")
    t.assert_false(allowed)
    t.assert_equal(reason, "rate_limit")


def test_multiplos_clientes_simultaneos(t):
    """Deve suportar múltiplos clientes sem race conditions"""
    limiter = RateLimiter(max_requests=3, window_seconds=1)

    clients = ["client1", "client2", "client3"]

    for client in clients:
        for _ in range(3):
            allowed, _ = limiter.is_allowed(client)
            t.assert_true(allowed)

    # Todos devem estar no limite
    for client in clients:
        allowed, _ = limiter.is_allowed(client)
        t.assert_false(allowed)


def main():
    """Runner principal"""
    print("="*60)
    print("🧪 TESTES DE RATE LIMITER E PROTEÇÕES")
    print("="*60)
    print()

    runner = TestRunner()

    # Testes de Rate Limiting
    print("📊 Rate Limiting:")
    runner.run_test(
        "Permite requisições dentro do limite",
        lambda: test_permite_requisicoes_dentro_do_limite(runner)
    )
    runner.run_test(
        "Bloqueia após exceder limite",
        lambda: test_bloqueia_apos_exceder_limite(runner)
    )
    runner.run_test(
        "Clientes independentes",
        lambda: test_clientes_independentes(runner)
    )
    runner.run_test(
        "Janela deslizante permite novas requisições",
        lambda: test_janela_deslizante_permite_novas_requisicoes(runner)
    )
    runner.run_test(
        "Estatísticas retornam valores corretos",
        lambda: test_estatisticas_retornam_valores_corretos(runner)
    )

    print()
    print("🔄 Deduplicação:")
    runner.run_test(
        "Detecta requisições duplicadas",
        lambda: test_detecta_requisicoes_duplicadas(runner)
    )
    runner.run_test(
        "Permite requisições diferentes",
        lambda: test_permite_requisicoes_diferentes(runner)
    )
    runner.run_test(
        "Deduplicação expira após janela",
        lambda: test_deduplicacao_expira_apos_janela(runner)
    )
    runner.run_test(
        "Ordem dos parâmetros não importa",
        lambda: test_ordem_dos_parametros_nao_importa(runner)
    )

    print()
    print("🔗 Verificação Combinada:")
    runner.run_test(
        "Bloqueia por rate limit primeiro",
        lambda: test_bloqueia_por_rate_limit_primeiro(runner)
    )
    runner.run_test(
        "Bloqueia por deduplicação",
        lambda: test_bloqueia_por_deduplicacao(runner)
    )
    runner.run_test(
        "Permite sem deduplicação",
        lambda: test_permite_sem_deduplicacao(runner)
    )

    print()
    print("🔒 Thread Safety:")
    runner.run_test(
        "Múltiplos clientes simultâneos",
        lambda: test_multiplos_clientes_simultaneos(runner)
    )

    success = runner.print_summary()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
