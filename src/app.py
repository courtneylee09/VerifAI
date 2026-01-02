"""VerifAI agent-x402 FastAPI application with x402 payment wall.
Version: 1.0.2 - Dashboard UI with analytics
"""
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
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
    X402_PRICE, X402_NETWORK, X402_DESCRIPTION, X402_MIME_TYPE, X402_OUTPUT_SCHEMA,
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
    version="1.0.2"
)

# Mount static files (CSS, images, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates for HTML rendering
templates = Jinja2Templates(directory="templates")

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

# Fix HTTPS scheme for Railway - MUST run before x402
@app.middleware("http")
async def fix_https_scheme(request, call_next):
    """
    Railway uses X-Forwarded-Proto to indicate HTTPS.
    This fixes the scheme so x402 generates correct HTTPS URLs.
    """
    forwarded_proto = request.headers.get("x-forwarded-proto", "").lower()
    if forwarded_proto == "https":
        request.scope["scheme"] = "https"
    
    response = await call_next(request)
    return response


# Rate limiting and request logging
@app.middleware("http")
async def add_rate_limit_and_log(request, call_next):
    return await rate_limit_and_log(request, call_next)


# x402 Payment wall - Let x402 auto-detect resource URL (now with HTTPS)
# This tells the internet: 'You must pay 0.05 USDC on Base Sepolia to see the result'
# EXCLUDED PATHS: /dashboard, /analytics, /static, /health, /metrics (free access)
if HAS_X402:
    payment_middleware = require_payment(
        price=X402_PRICE,
        pay_to_address=MERCHANT_WALLET_ADDRESS,
        network=X402_NETWORK,
        description=X402_DESCRIPTION,
        mime_type=X402_MIME_TYPE,
        output_schema=X402_OUTPUT_SCHEMA
    )
    
    @app.middleware("http")
    async def conditional_payment_wall(request, call_next):
        """Apply x402 payment only to /verify endpoint, not dashboard/metrics."""
        path = request.url.path
        
        # Exempt these paths from payment
        exempt_paths = [
            "/", "/health", "/dashboard", "/analytics", 
            "/metrics/economics", "/metrics/logs",
            "/.well-known/x402.json"
        ]
        exempt_prefixes = ["/static"]
        
        is_exempt = (
            path in exempt_paths or 
            any(path.startswith(prefix) for prefix in exempt_prefixes)
        )
        
        if is_exempt:
            # Skip payment for exempt paths
            return await call_next(request)
        else:
            # Require payment for /verify and other paths
            return await payment_middleware(request, call_next)
else:
    logger.warning("x402 module not available - payment middleware disabled")

# ============================================================================
# Endpoints
# ============================================================================

@app.get("/")
async def root(request: Request):
    """
    Root endpoint - serves landing page for browsers, JSON for API clients.
    
    Content negotiation:
    - Browsers (text/html): Landing page
    - API clients (application/json): Service info
    """
    accept_header = request.headers.get("accept", "").lower()
    
    # If browser requests HTML, show landing page
    if "text/html" in accept_header:
        return templates.TemplateResponse("home.html", {"request": request})
    
    # Otherwise return JSON (for API clients, curl, etc.)
    return {
        "service": "VerifAI agent-x402",
        "version": "1.0.2",
        "description": "Multi-agent AI fact-checking with x402 payment",
        "endpoints": {
            "verify": "/verify?claim={your_claim}",
            "dashboard": "/dashboard",
            "analytics": "/analytics",
            "health": "/health",
            "metrics": "/metrics/economics",
            "manifest": "/.well-known/x402.json"
        },
        "payment": {
            "price": "0.05 USDC",
            "network": "base-sepolia"
        }
    }


@app.get("/verify")
async def verify(request: Request, claim: str):
    """
    Verify a claim using multi-agent debate.
    
    This endpoint requires x402 payment before execution.
    Supports content negotiation via Accept header:
    - application/json (default): Machine-readable JSON - RECOMMENDED for M2M
    - text/html: Human-readable HTML page
    - text/plain: Simple text format
    
    For machine-to-machine integration, omit Accept header or use application/json.
    
    Args:
        request: FastAPI request object (for Accept header)
        claim: The claim to verify
        
    Returns:
        Verification result in requested format
    """
    logger.info("endpoint.verify.called claim=%s", claim)
    
    # Get verification result
    result = await verify_claim_logic(claim)
    
    # Check what format the client wants (content negotiation)
    accept_header = request.headers.get("accept", "application/json").lower()
    
    # For M2M: if no Accept header or */* or application/json -> return JSON
    # This is the most common pattern in production APIs
    if not accept_header or accept_header == "*/*" or "application/json" in accept_header:
        # Default: Return JSON (best for machines)
        return result
    
    # Human-friendly formats (optional)
    elif "text/html" in accept_header:
        # Return HTML for browsers/humans
        from fastapi.responses import HTMLResponse
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>VerifAI Result: {claim}</title>
            <style>
                body {{ font-family: system-ui, -apple-system, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }}
                .verdict {{ font-size: 2em; font-weight: bold; margin: 20px 0; }}
                .true {{ color: #16a34a; }}
                .false {{ color: #dc2626; }}
                .inconclusive {{ color: #ea580c; }}
                .confidence {{ font-size: 1.2em; color: #6b7280; }}
                .section {{ margin: 30px 0; padding: 20px; background: #f9fafb; border-radius: 8px; }}
                .sources {{ list-style: none; padding: 0; }}
                .sources li {{ margin: 10px 0; }}
                .sources a {{ color: #2563eb; }}
            </style>
        </head>
        <body>
            <h1>VerifAI Verification Result</h1>
            <p><strong>Claim:</strong> {claim}</p>
            <div class="verdict {result['verdict'].lower()}">{result['verdict']}</div>
            <div class="confidence">Confidence: {result['confidence']:.0%}</div>
            
            <div class="section">
                <h2>Judge's Reasoning</h2>
                <p>{result['reasoning']}</p>
            </div>
            
            <div class="section">
                <h2>Supporting Arguments (Prover)</h2>
                <p>{result['prover_argument']}</p>
            </div>
            
            <div class="section">
                <h2>Counter-Arguments (Debunker)</h2>
                <p>{result['debunker_argument']}</p>
            </div>
            
            <div class="section">
                <h2>Sources</h2>
                <ul class="sources">
                    {"".join(f'<li><a href="{s["url"]}" target="_blank">{s["title"]}</a><br><small>{s["snippet"][:200]}...</small></li>' for s in result['sources'])}
                </ul>
            </div>
            
            <p style="color: #9ca3af; font-size: 0.9em;">
                Execution time: {result['execution_time_seconds']:.2f}s | Cost: ${result['total_cost_usd']:.4f}
            </p>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    
    elif "text/plain" in accept_header:
        # Return plain text for simple parsing
        from fastapi.responses import PlainTextResponse
        text_content = f"""VERIFAI VERIFICATION RESULT
        
Claim: {claim}
Verdict: {result['verdict']}
Confidence: {result['confidence']:.0%}

REASONING:
{result['reasoning']}

SUPPORTING ARGUMENTS:
{result['prover_argument']}

COUNTER-ARGUMENTS:
{result['debunker_argument']}

SOURCES:
{chr(10).join(f"- {s['title']}: {s['url']}" for s in result['sources'])}

Execution time: {result['execution_time_seconds']:.2f}s
Cost: ${result['total_cost_usd']:.4f}
"""
        return PlainTextResponse(content=text_content)
    
    # If they request something we don't support, return JSON with a hint
    else:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            content=result,
            headers={
                "X-Supported-Formats": "application/json, text/html, text/plain"
            }
        )


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


@app.get("/dashboard")
async def dashboard(request: Request):
    """
    Dashboard page showing verification history.
    
    Displays recent verifications with:
    - Claim, verdict, confidence
    - Revenue, costs, profit per request
    - Execution time and status
    """
    try:
        # Get metrics and logs
        metrics = PerformanceLogger.get_summary()
        logs = PerformanceLogger.read_logs()
        
        # Return HTML dashboard
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "metrics": metrics,
                "logs": logs[-50:] if len(logs) > 50 else logs  # Show last 50
            }
        )
    except Exception as e:
        logger.error("dashboard.failed err=%s", e)
        # Return error page
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "metrics": {
                    "total_requests": 0,
                    "total_revenue_usd": 0.0,
                    "total_cost_usd": 0.0,
                    "total_profit_usd": 0.0,
                    "avg_profit_margin_pct": 0.0
                },
                "logs": []
            }
        )


@app.get("/analytics")
async def analytics(request: Request):
    """
    Analytics page with performance metrics and charts.
    
    Shows:
    - Verdict distribution
    - Economics breakdown (revenue vs costs vs profit)
    - Token usage by agent
    - Agent performance table
    """
    try:
        # Get metrics and logs
        metrics = PerformanceLogger.get_summary()
        logs = PerformanceLogger.read_logs()
        
        # Calculate verdict distribution for chart
        verdict_counts = {}
        for log in logs:
            verdict = log.get("verdict", "Unknown")
            verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
        
        verdict_labels = list(verdict_counts.keys())
        verdict_values = list(verdict_counts.values())
        
        # Return HTML analytics page
        return templates.TemplateResponse(
            "analytics.html",
            {
                "request": request,
                "metrics": metrics,
                "verdict_labels": verdict_labels,
                "verdict_counts": verdict_values
            }
        )
    except Exception as e:
        logger.error("analytics.failed err=%s", e)
        # Return error page with defaults
        return templates.TemplateResponse(
            "analytics.html",
            {
                "request": request,
                "metrics": {
                    "total_requests": 0,
                    "total_revenue_usd": 0.0,
                    "total_cost_usd": 0.0,
                    "total_profit_usd": 0.0,
                    "avg_profit_margin_pct": 0.0,
                    "avg_cost_per_request": 0.0,
                    "avg_profit_per_request": 0.0,
                    "total_tokens": 0,
                    "avg_execution_time": 0.0,
                    "avg_prover_cost": 0.0,
                    "avg_debunker_cost": 0.0,
                    "avg_judge_cost": 0.0,
                    "total_prover_cost": 0.0,
                    "total_debunker_cost": 0.0,
                    "total_judge_cost": 0.0,
                    "avg_prover_input_tokens": 0,
                    "avg_prover_output_tokens": 0,
                    "avg_debunker_input_tokens": 0,
                    "avg_debunker_output_tokens": 0,
                    "avg_judge_input_tokens": 0,
                    "avg_judge_output_tokens": 0
                },
                "verdict_labels": [],
                "verdict_counts": []
            }
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
