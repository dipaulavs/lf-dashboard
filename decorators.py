"""
Flask Decorators para Proteção de API
Previne database locks via rate limiting e deduplicação
"""
from functools import wraps
from flask import request, jsonify
from typing import Callable, Optional
import logging

# Import rate limiter global
from rate_limiter import rate_limiter

# Configurar logging
logger = logging.getLogger(__name__)


def rate_limit(max_requests: int = 10, window_seconds: int = 1) -> Callable:
    """
    Decorator de rate limiting para endpoints Flask

    Limita número de requisições por IP em janela de tempo.
    Retorna 429 Too Many Requests se exceder limite.

    Args:
        max_requests: Máximo de requisições permitidas
        window_seconds: Janela de tempo em segundos

    Usage:
        @app.route('/api/endpoint')
        @rate_limit(max_requests=10, window_seconds=1)
        def my_endpoint():
            return {"status": "ok"}

    Returns:
        429 se rate limit excedido
        Chama função original se permitido
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Identificar cliente por IP
            client_ip = request.remote_addr or "unknown"

            # Verificar rate limit
            allowed, reason = rate_limiter.is_allowed(client_ip)

            if not allowed:
                logger.warning(
                    f"Rate limit exceeded for {client_ip} on {request.path}"
                )

                # Obter estatísticas para retry
                stats = rate_limiter.get_stats(client_ip)

                return jsonify({
                    "success": False,
                    "error": "Too many requests",
                    "reason": reason,
                    "retry_after": stats["window_seconds"],
                    "limit": stats["max_requests"],
                    "remaining": 0
                }), 429

            # Rate limit ok, executar função
            response = func(*args, **kwargs)

            # Adicionar headers de rate limit na resposta
            if isinstance(response, tuple):
                resp_obj = response[0]
            else:
                resp_obj = response

            stats = rate_limiter.get_stats(client_ip)

            # Se resposta é jsonify, adicionar headers
            if hasattr(resp_obj, 'headers'):
                resp_obj.headers['X-RateLimit-Limit'] = str(stats["max_requests"])
                resp_obj.headers['X-RateLimit-Remaining'] = str(stats["remaining"])
                resp_obj.headers['X-RateLimit-Reset'] = str(int(stats["reset_at"]))

            return response

        return wrapper
    return decorator


def deduplicate(window_seconds: int = 5, check_params: Optional[list] = None) -> Callable:
    """
    Decorator de deduplicação para endpoints Flask

    Previne processamento de requisições duplicadas baseado em parâmetros.
    Útil quando n8n faz retry e envia mesma requisição múltiplas vezes.

    Args:
        window_seconds: Janela de tempo para considerar duplicatas
        check_params: Lista de query params para verificar (None = todos)

    Usage:
        @app.route('/api/endpoint')
        @deduplicate(window_seconds=5, check_params=['whatsapp', 'score'])
        def my_endpoint():
            return {"status": "ok"}

    Returns:
        409 Conflict se requisição duplicada
        Chama função original se nova requisição
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extrair parâmetros da requisição
            if request.method == 'GET':
                params = dict(request.args)
            elif request.method == 'POST':
                params = dict(request.get_json() or {})
            else:
                params = {}

            # Filtrar apenas parâmetros especificados
            if check_params:
                params = {k: v for k, v in params.items() if k in check_params}

            # Verificar se é duplicada
            is_dup, req_hash = rate_limiter.is_duplicate(params)

            if is_dup:
                logger.info(
                    f"Duplicate request detected: {request.path} "
                    f"params={params} hash={req_hash[:8]}"
                )

                return jsonify({
                    "success": False,
                    "error": "Duplicate request",
                    "reason": "duplicate",
                    "message": f"Same request received within {window_seconds}s window",
                    "window_seconds": window_seconds
                }), 409

            # Nova requisição, executar
            return func(*args, **kwargs)

        return wrapper
    return decorator


def retry_on_lock(max_retries: int = 3, log_retries: bool = True) -> Callable:
    """
    Decorator que captura erros de database locked e retorna 503

    Usado quando todas tentativas de retry no database.py falharam.
    Indica ao cliente que servidor está temporariamente sobrecarregado.

    Args:
        max_retries: Informativo - quantas tentativas foram feitas
        log_retries: Se deve logar tentativas

    Usage:
        @app.route('/api/endpoint')
        @retry_on_lock(max_retries=3)
        def my_endpoint():
            db.write_operation()  # Pode dar OperationalError

    Returns:
        503 Service Unavailable se database locked após todas tentativas
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Detectar database locked
                if "database is locked" in str(e).lower():
                    if log_retries:
                        logger.error(
                            f"Database locked after {max_retries} retries "
                            f"on {request.path}: {e}"
                        )

                    return jsonify({
                        "success": False,
                        "error": "Service temporarily unavailable",
                        "reason": "database_busy",
                        "message": "Database is busy, please retry in a few seconds",
                        "retry_after": 2
                    }), 503

                # Outros erros, re-raise
                raise

        return wrapper
    return decorator


# Decorator combinado (conveniente)
def protect_endpoint(
    max_requests: int = 10,
    window_seconds: int = 1,
    dedup_window: int = 5,
    dedup_params: Optional[list] = None
) -> Callable:
    """
    Decorator combinado com todas proteções

    Aplica em ordem:
    1. Rate limiting (10 req/s por IP)
    2. Deduplicação (5s window)
    3. Retry on lock (captura database errors)

    Usage:
        @app.route('/api/endpoint')
        @protect_endpoint(
            max_requests=10,
            dedup_params=['whatsapp', 'score']
        )
        def my_endpoint():
            return {"status": "ok"}
    """
    def decorator(func: Callable) -> Callable:
        # Aplicar decorators em ordem reversa (inside-out)
        protected = func
        protected = retry_on_lock()(protected)
        protected = deduplicate(dedup_window, dedup_params)(protected)
        protected = rate_limit(max_requests, window_seconds)(protected)
        return protected
    return decorator
