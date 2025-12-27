"""Rate limiting middleware: Per-IP rate limit enforcement."""
import time
import logging
from fastapi.responses import JSONResponse

from config.settings import RATE_LIMIT_MAX, RATE_LIMIT_WINDOW_SECONDS

logger = logging.getLogger(__name__)

# In-memory state for rate limiting
_rate_limit_state: dict[str, list[float]] = {}


async def rate_limit_and_log(request, call_next):
    """
    Lightweight per-IP rate limit (60 req/min) plus request logging.
    
    Maintains an in-memory bucket per IP address and rejects requests
    that exceed the rate limit.
    """
    client_ip = request.client.host if request.client else "unknown"
    now = time.monotonic()

    # Get or create bucket for this IP, remove stale timestamps
    bucket = _rate_limit_state.get(client_ip, [])
    bucket = [t for t in bucket if now - t < RATE_LIMIT_WINDOW_SECONDS]
    
    # Check if rate limit exceeded
    if len(bucket) >= RATE_LIMIT_MAX:
        logger.warning("rate_limit.exceeded ip=%s", client_ip)
        return JSONResponse({"detail": "Too Many Requests"}, status_code=429)
    
    # Add current timestamp to bucket
    bucket.append(now)
    _rate_limit_state[client_ip] = bucket

    # Process request and log response
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    
    logger.info(
        "request path=%s ip=%s status=%s ms=%.1f",
        request.url.path,
        client_ip,
        response.status_code,
        duration_ms,
    )
    
    return response
