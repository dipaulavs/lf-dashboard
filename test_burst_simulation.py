#!/usr/bin/env python3
"""
Simulação de Burst de Requisições
Testa proteções contra cenário real do n8n
"""
import time
from rate_limiter import RateLimiter


def simulate_n8n_burst():
    """
    Simula n8n enviando burst de 50 requisições em 1 segundo
    Cenário real que causava database locked
    """
    print("="*60)
    print("🔥 SIMULAÇÃO DE BURST - CENÁRIO N8N")
    print("="*60)
    print()

    limiter = RateLimiter(max_requests=10, window_seconds=1, dedup_window_seconds=5)

    print("📊 Configuração:")
    print(f"  - Rate limit: 10 req/s por IP")
    print(f"  - Dedup window: 5s")
    print(f"  - Burst simulado: 50 requisições em 1s")
    print()

    # Simular 50 leads diferentes
    leads = [
        {"whatsapp": f"5531999{i:06d}", "score": 45 + (i % 50)}
        for i in range(50)
    ]

    print("🚀 Enviando burst de 50 requisições...")
    print()

    results = {
        "success": 0,
        "rate_limit_blocked": 0,
        "duplicate_blocked": 0,
        "total": 50
    }

    start_time = time.time()

    for i, lead_data in enumerate(leads, 1):
        # Verificar rate limit + dedup
        allowed, reason = limiter.check_request("n8n_client", lead_data)

        if allowed:
            results["success"] += 1
            status = "✅"
        elif reason == "rate_limit":
            results["rate_limit_blocked"] += 1
            status = "⚠️  RATE LIMIT"
        elif reason == "duplicate":
            results["duplicate_blocked"] += 1
            status = "⚠️  DUPLICATE"
        else:
            status = "❌"

        # Mostrar progresso a cada 10 requisições
        if i % 10 == 0:
            print(f"  [{i:2d}/50] {status} - {lead_data['whatsapp']}")

    elapsed = time.time() - start_time

    print()
    print("="*60)
    print("📈 RESULTADOS")
    print("="*60)
    print(f"✅ Processadas:         {results['success']:2d}/50 ({results['success']/50*100:.0f}%)")
    print(f"⚠️  Rate limit:         {results['rate_limit_blocked']:2d}/50 ({results['rate_limit_blocked']/50*100:.0f}%)")
    print(f"⚠️  Duplicatas:         {results['duplicate_blocked']:2d}/50 ({results['duplicate_blocked']/50*100:.0f}%)")
    print(f"⏱️  Tempo total:        {elapsed:.3f}s")
    print()

    # Estatísticas finais
    stats = limiter.get_stats("n8n_client")
    print("📊 Estatísticas do Rate Limiter:")
    print(f"  - Requisições na janela: {stats['requests_in_window']}")
    print(f"  - Limite máximo: {stats['max_requests']}")
    print(f"  - Restantes: {stats['remaining']}")
    print()

    # Verificar se comportamento é esperado
    print("="*60)
    print("✅ VALIDAÇÃO")
    print("="*60)

    checks = []

    # Check 1: Exatamente 10 requisições processadas (rate limit)
    if results['success'] == 10:
        checks.append(("Rate limit funciona corretamente (10 req/s)", True))
    else:
        checks.append((f"Rate limit deveria processar 10, processou {results['success']}", False))

    # Check 2: 40 requisições bloqueadas por rate limit
    if results['rate_limit_blocked'] == 40:
        checks.append(("Bloqueio de rate limit correto (40 bloqueadas)", True))
    else:
        checks.append((f"Deveria bloquear 40, bloqueou {results['rate_limit_blocked']}", False))

    # Check 3: Nenhuma duplicata (leads diferentes)
    if results['duplicate_blocked'] == 0:
        checks.append(("Deduplicação não bloqueou leads diferentes", True))
    else:
        checks.append((f"Deduplicação bloqueou {results['duplicate_blocked']} leads diferentes", False))

    # Check 4: Tempo razoável (< 1s já que não há sleep)
    if elapsed < 1.0:
        checks.append((f"Performance aceitável ({elapsed:.3f}s < 1s)", True))
    else:
        checks.append((f"Performance ruim ({elapsed:.3f}s >= 1s)", False))

    all_passed = True
    for check, passed in checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")
        if not passed:
            all_passed = False

    print()

    if all_passed:
        print("🎉 SUCESSO! Proteções funcionando corretamente!")
        print()
        print("💡 Próximo passo: Testar com Flask app rodando")
        return 0
    else:
        print("⚠️  Algumas verificações falharam. Revisar implementação.")
        return 1


def simulate_duplicate_requests():
    """
    Simula n8n fazendo retry da mesma requisição múltiplas vezes
    Cenário: n8n recebe timeout e faz retry com mesmos dados
    """
    print()
    print("="*60)
    print("🔄 SIMULAÇÃO DE REQUISIÇÕES DUPLICADAS")
    print("="*60)
    print()

    limiter = RateLimiter(max_requests=20, window_seconds=1, dedup_window_seconds=5)

    print("📊 Cenário: n8n recebe timeout e faz 5 retries da mesma requisição")
    print()

    lead_data = {"whatsapp": "5531999887766", "score": 45}

    print(f"📝 Requisição: {lead_data}")
    print()

    for i in range(1, 6):
        allowed, reason = limiter.check_request("n8n_client", lead_data)

        if allowed:
            print(f"  Tentativa {i}: ✅ PROCESSADA")
        else:
            print(f"  Tentativa {i}: ⚠️  BLOQUEADA ({reason})")

        time.sleep(0.5)  # 500ms entre tentativas

    print()
    print("✅ Resultado esperado:")
    print("  - 1ª tentativa: PROCESSADA")
    print("  - 2ª-5ª tentativas: BLOQUEADAS (duplicate)")
    print()


def simulate_multiple_clients():
    """
    Simula múltiplos clientes (diferentes IPs) fazendo requisições simultâneas
    Cenário: Múltiplas instâncias do n8n ou clientes diferentes
    """
    print("="*60)
    print("👥 SIMULAÇÃO DE MÚLTIPLOS CLIENTES")
    print("="*60)
    print()

    limiter = RateLimiter(max_requests=5, window_seconds=1)

    clients = ["client_1", "client_2", "client_3"]

    print(f"📊 Cenário: 3 clientes fazendo 7 requisições cada")
    print(f"   Limite: 5 req/s por cliente")
    print()

    for client in clients:
        success = 0
        blocked = 0

        for i in range(1, 8):
            allowed, reason = limiter.is_allowed(client)

            if allowed:
                success += 1
            else:
                blocked += 1

        print(f"  {client}: ✅ {success} processadas | ⚠️  {blocked} bloqueadas")

    print()
    print("✅ Resultado esperado: Cada cliente processa 5 e bloqueia 2")
    print("   (limites independentes por cliente)")
    print()


def main():
    """Runner principal"""
    print()
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "TESTE DE PROTEÇÕES - BURST SIMULATION" + " "*11 + "║")
    print("╚" + "="*58 + "╝")
    print()

    # Teste 1: Burst de 50 requisições (cenário crítico)
    exit_code = simulate_n8n_burst()

    # Teste 2: Requisições duplicadas
    simulate_duplicate_requests()

    # Teste 3: Múltiplos clientes
    simulate_multiple_clients()

    print("="*60)
    print("🏁 SIMULAÇÕES CONCLUÍDAS")
    print("="*60)
    print()

    return exit_code


if __name__ == "__main__":
    exit(main())
