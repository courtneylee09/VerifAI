"""VerifAI agent-x402 FastAPI application with x402 payment wall.
Version: 1.0.1 - CORS enabled for wallet compatibility
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
try:
    from x402.fastapi.middleware import require_payment
    HAS_X402 = True
except ImportError:
    HAS_X402 = False
    # Fallback: dummy middleware that logs but doesn't block
    async def require_payment(*args, **kwargs):
        async def middleware(request, call_next):
            return await call_next(request)
        return middleware

from config.settings import (
    X402_PRICE, X402_NETWORK, X402_DESCRIPTION,
    MERCHANT_WALLET_ADDRESS, SERVICE_BASE_URL
)
from src.middleware import setup_logging, rate_limit_and_log
from src.services import verify_claim_logic
from performance_log import PerformanceLogger

# Setup logging
logger = setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title="VerifAI agent-x402",
    description="Paid AI verification service using x402 payment protocol with multi-agent debate",
    version="1.0.0"
)

# ============================================================================
# CORS Configuration (for x402 wallet compatibility)
# ============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for x402 wallet compatibility
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers including X-PAYMENT
    expose_headers=["X-PAYMENT", "X-402-Version"],  # Expose x402 headers to clients
)

# ============================================================================
# Middleware Registration
# ============================================================================

# Fix Railway proxy headers (Railway uses HTTP internally but HTTPS externally)
@app.middleware("http")
async def fix_proxy_headers(request, call_next):
    """Ensure x402 detects HTTPS correctly from Railway's proxy headers."""
    # Railway sets X-Forwarded-Proto to 'https' for external requests
    if request.headers.get("x-forwarded-proto") == "https":
        request.scope["scheme"] = "https"
    return await call_next(request)

# Rate limiting and request logging
@app.middleware("http")
async def add_rate_limit_and_log(request, call_next):
    return await rate_limit_and_log(request, call_next)


# x402 Payment wall
# This tells the internet: 'You must pay 0.05 USDC on Base Sepolia to see the result'
# x402 expects the price WITHOUT decimals applied - it handles USDC decimals internally
if HAS_X402:
    app.middleware("http")(
        require_payment(
            price=X402_PRICE,  # Amount in USDC (x402 handles decimal conversion)
            pay_to_address=MERCHANT_WALLET_ADDRESS,
            network=X402_NETWORK,
            description=X402_DESCRIPTION
            # Let x402 auto-detect resource URL from request (will use HTTPS from proxy headers)
        )
    )
else:
    logger.warning("x402 module not available - payment middleware disabled")

# ============================================================================
# Endpoints
# ============================================================================

@app.get("/verify")
async def verify(claim: str):
    """
    Verify a claim using multi-agent debate.
    
    This endpoint requires x402 payment before execution.
    
    Args:
        claim: The claim to verify
        
    Returns:
        Verification result with verdict, confidence_score, citations, and debate details
    """
    logger.info("endpoint.verify.called claim=%s", claim)
    result = await verify_claim_logic(claim)
    return result


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "VerifAI agent-x402"}


@app.get("/metrics/economics")
async def metrics_economics():
    """
    Public economics endpoint: Shows profit summary and earnings.
    
    Returns aggregate statistics on:
    - Total requests served
    - Revenue earned (USDC)
    - LLM costs
    - Net profit and margin
    - Token usage
    """
    try:
        summary = PerformanceLogger.get_summary()
        return {
            "status": "ok",
            "metrics": summary
        }
    except Exception as e:
        logger.error("metrics.economics.failed err=%s", e)
        return {
            "status": "error",
            "error": str(e),
            "metrics": {
                "total_requests": 0,
                "total_revenue_usd": 0.0,
                "total_cost_usd": 0.0,
                "total_profit_usd": 0.0
            }
        }


@app.get("/metrics/logs")
async def metrics_logs(limit: int = 10):
    """
    Public logs endpoint: Returns recent verification requests with economics.
    
    Args:
        limit: Number of recent logs to return (default 10, max 100)
        
    Returns:
        List of recent verification requests with token usage and profit data
    """
    limit = min(limit, 100)  # Cap at 100
    try:
        logs = PerformanceLogger.read_logs()
        recent = logs[-limit:] if len(logs) > limit else logs
        
        return {
            "status": "ok",
            "count": len(recent),
            "total_logged": len(logs),
            "logs": recent
        }
    except Exception as e:
        logger.error("metrics.logs.failed err=%s", e)
        return {
            "status": "error",
            "error": str(e),
            "count": 0,
            "logs": []
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
