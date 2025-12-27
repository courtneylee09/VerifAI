"""VerifAI agent-x402 FastAPI application with x402 payment wall."""
import os
from fastapi import FastAPI
from x402.fastapi.middleware import require_payment

from config.settings import (
    X402_PRICE, X402_NETWORK, X402_DESCRIPTION,
    MERCHANT_WALLET_ADDRESS
)
from src.middleware import setup_logging, rate_limit_and_log
from src.services import verify_claim_logic

# Setup logging
logger = setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title="VerifAI agent-x402",
    description="Paid AI verification service using x402 payment protocol with multi-agent debate",
    version="1.0.0"
)

# ============================================================================
# Middleware Registration
# ============================================================================

# Rate limiting and request logging (applied first)
@app.middleware("http")
async def add_rate_limit_and_log(request, call_next):
    return await rate_limit_and_log(request, call_next)


# x402 Payment wall (applied second)
# This tells the internet: 'You must pay 0.05 USDC on Base Sepolia to see the result'
# x402 expects the price WITHOUT decimals applied - it handles USDC decimals internally
app.middleware("http")(
    require_payment(
        price=X402_PRICE,  # Amount in USDC (x402 handles decimal conversion)
        pay_to_address=MERCHANT_WALLET_ADDRESS,
        network=X402_NETWORK,
        description=X402_DESCRIPTION
    )
)

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
