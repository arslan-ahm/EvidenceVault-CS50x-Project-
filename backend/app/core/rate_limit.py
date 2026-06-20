from collections import defaultdict, deque
from dataclasses import dataclass
from time import monotonic


@dataclass
class RateLimitConfig:
    max_requests: int = 120
    window_seconds: int = 60


class InMemoryRateLimiter:
    def __init__(self, config: RateLimitConfig | None = None) -> None:
        self.config = config or RateLimitConfig()
        self.requests: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = monotonic()
        window_start = now - self.config.window_seconds
        queue = self.requests[key]
        while queue and queue[0] < window_start:
            queue.popleft()
        if len(queue) >= self.config.max_requests:
            return False
        queue.append(now)
        return True
