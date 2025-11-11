"""
Rate Limiter + Request Deduplication
Protege API contra burst e requisições duplicadas
"""
import time
from collections import defaultdict
from threading import Lock
from typing import Dict, Tuple, Optional
import hashlib


class RateLimiter:
    """
    Rate limiter com sliding window + deduplicação

    Protege contra:
    1. Burst de requisições (max 10 req/s por IP)
    2. Requisições duplicadas (mesmo payload em 5s)
    """

    def __init__(
        self,
        max_requests: int = 10,
        window_seconds: int = 1,
        dedup_window_seconds: int = 5
    ):
        """
        Args:
            max_requests: Máximo de requisições por janela
            window_seconds: Tamanho da janela em segundos
            dedup_window_seconds: Janela de deduplicação em segundos
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.dedup_window_seconds = dedup_window_seconds

        # Rate limiting storage: {ip: [(timestamp1, timestamp2, ...)]}
        self.requests: Dict[str, list] = defaultdict(list)

        # Deduplication storage: {request_hash: timestamp}
        self.recent_requests: Dict[str, float] = {}

        # Thread-safe locks
        self.rate_lock = Lock()
        self.dedup_lock = Lock()

    def is_allowed(self, client_id: str) -> Tuple[bool, Optional[str]]:
        """
        Verifica se cliente pode fazer requisição

        Args:
            client_id: Identificador do cliente (IP, user_id, etc)

        Returns:
            (permitido, motivo_bloqueio)
            - (True, None) se permitido
            - (False, "rate_limit") se excedeu limite
        """
        with self.rate_lock:
            now = time.time()

            # Limpar requisições antigas
            cutoff = now - self.window_seconds
            self.requests[client_id] = [
                ts for ts in self.requests[client_id]
                if ts > cutoff
            ]

            # Verificar limite
            if len(self.requests[client_id]) >= self.max_requests:
                return False, "rate_limit"

            # Registrar nova requisição
            self.requests[client_id].append(now)

            return True, None

    def is_duplicate(self, request_data: Dict) -> Tuple[bool, Optional[str]]:
        """
        Verifica se requisição é duplicada

        Args:
            request_data: Dados da requisição (whatsapp, score, etc)

        Returns:
            (é_duplicada, hash_da_requisicao)
        """
        with self.dedup_lock:
            now = time.time()

            # Gerar hash da requisição
            request_str = str(sorted(request_data.items()))
            request_hash = hashlib.md5(request_str.encode()).hexdigest()

            # Limpar requisições antigas
            cutoff = now - self.dedup_window_seconds
            self.recent_requests = {
                h: ts for h, ts in self.recent_requests.items()
                if ts > cutoff
            }

            # Verificar se é duplicada
            if request_hash in self.recent_requests:
                return True, request_hash

            # Registrar nova requisição
            self.recent_requests[request_hash] = now

            return False, request_hash

    def check_request(
        self,
        client_id: str,
        request_data: Optional[Dict] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Verificação completa: rate limit + deduplicação

        Args:
            client_id: IP ou identificador do cliente
            request_data: Dados da requisição (opcional)

        Returns:
            (permitido, motivo_bloqueio)
            - (True, None) se permitido
            - (False, "rate_limit") se excedeu taxa
            - (False, "duplicate") se requisição duplicada
        """
        # 1. Verificar rate limit
        allowed, reason = self.is_allowed(client_id)
        if not allowed:
            return False, reason

        # 2. Verificar deduplicação (se dados fornecidos)
        if request_data:
            is_dup, _ = self.is_duplicate(request_data)
            if is_dup:
                return False, "duplicate"

        return True, None

    def get_stats(self, client_id: str) -> Dict:
        """Retorna estatísticas do rate limiter"""
        with self.rate_lock:
            now = time.time()
            cutoff = now - self.window_seconds

            recent = [ts for ts in self.requests.get(client_id, []) if ts > cutoff]

            return {
                "requests_in_window": len(recent),
                "max_requests": self.max_requests,
                "window_seconds": self.window_seconds,
                "remaining": max(0, self.max_requests - len(recent)),
                "reset_at": cutoff + self.window_seconds if recent else now
            }


# Instância global (compartilhada entre requisições)
rate_limiter = RateLimiter(
    max_requests=10,  # 10 req/s
    window_seconds=1,
    dedup_window_seconds=5  # 5s dedup window
)
