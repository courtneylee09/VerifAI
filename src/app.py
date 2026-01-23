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
from src.services.verification import verify_news_claim_logic
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
                .evidence-list {{ list-style: none; padding: 0; }}
                .evidence-item {{ margin: 12px 0; padding: 12px; background: white; border-radius: 6px; border-left: 3px solid #2563eb; }}
                .evidence-for {{ border-left-color: #16a34a; }}
                .evidence-against {{ border-left-color: #dc2626; }}
                .evidence-source {{ font-weight: 600; color: #374151; }}
                .evidence-weight {{ font-size: 0.85em; color: #6b7280; }}
            </style>
        </head>
        <body>
            <h1>VerifAI Verification Result</h1>
            <p><strong>Claim:</strong> {claim}</p>
            <div class="verdict {result['verdict'].lower()}">{result['verdict']}</div>
            <div class="confidence">Confidence: {result['confidence']:.0%}</div>
            
            <div class="section">
                <h2>⚖️ Judge's Analysis</h2>
                <p>{result.get('reasoning', result.get('summary', ''))}</p>
            </div>
            
            <div class="section">
                <h2>✅ Supporting Evidence (Weight: {sum(e.get('weight', 1.0) for e in result.get('evidence_for', [])):.1f})</h2>
                {('<ul class="evidence-list">' + ''.join(f'<li class="evidence-item evidence-for"><span class="evidence-source">{e.get("source", "Unknown")}</span> <span class="evidence-weight">(weight: {e.get("weight", 1.0)}x)</span><br>{e.get("point", "")}</li>' for e in result.get('evidence_for', [])) + '</ul>') if result.get('evidence_for') else '<p style="color: #6b7280;">No supporting evidence found</p>'}
            </div>
            
            <div class="section">
                <h2>❌ Contradicting Evidence (Weight: {sum(e.get('weight', 1.0) for e in result.get('evidence_against', [])):.1f})</h2>
                {('<ul class="evidence-list">' + ''.join(f'<li class="evidence-item evidence-against"><span class="evidence-source">{e.get("source", "Unknown")}</span> <span class="evidence-weight">(weight: {e.get("weight", 1.0)}x)</span><br>{e.get("point", "")}</li>' for e in result.get('evidence_against', [])) + '</ul>') if result.get('evidence_against') else '<p style="color: #6b7280;">No contradicting evidence found</p>'}
            </div>
            
            <div class="section">
                <h2>📚 Sources Consulted</h2>
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


@app.post("/verify/batch")
async def verify_batch(request: Request):
    """
    Batch verification endpoint - verify multiple claims in one request.
    
    Supports bulk discounts:
    - 5-9 claims: 10% discount
    - 10+ claims: 15% discount
    
    Example request:
    {
        "claims": ["Earth is round", "Water is wet", "Sky is blue"]
    }
    
    Example response:
    {
        "total_claims": 3,
        "total_cost": 0.15,
        "bulk_discount": 0.00,
        "results": [...]
    }
    """
    import asyncio
    from fastapi.responses import JSONResponse
    
    logger.info("endpoint.verify_batch.called")
    
    try:
        body = await request.json()
        claims = body.get("claims", [])
        
        if not claims:
            return JSONResponse(
                status_code=400,
                content={"error": "No claims provided. Include 'claims' array in request body."}
            )
        
        if len(claims) > 100:
            return JSONResponse(
                status_code=400,
                content={"error": "Maximum 100 claims per batch. Please reduce batch size."}
            )
        
        logger.info("batch.processing count=%d", len(claims))
        
        # Process all claims in parallel
        tasks = [verify_claim_logic(claim) for claim in claims]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "claim": claims[i],
                    "verdict": "Error",
                    "confidence_score": 0.0,
                    "summary": f"Processing error: {str(result)}",
                    "payment_status": "refunded_due_to_system_error"
                })
            else:
                # Add original claim to result
                result["claim"] = claims[i]
                processed_results.append(result)
        
        # Calculate totals
        base_cost = len(claims) * 0.05
        refunded_count = sum(1 for r in processed_results if r.get("payment_status", "").startswith("refunded"))
        successful_count = len(claims) - refunded_count
        
        # Bulk discount: 10% off for 5+ claims, 15% off for 10+ claims
        discount_percent = 0
        if len(claims) >= 10:
            discount_percent = 15
        elif len(claims) >= 5:
            discount_percent = 10
        
        discount_amount = (successful_count * 0.05) * (discount_percent / 100)
        final_cost = (successful_count * 0.05) - discount_amount
        
        logger.info(
            "batch.done total=%d successful=%d cost=%.4f discount=%.4f",
            len(claims), successful_count, final_cost, discount_amount
        )
        
        return {
            "total_claims": len(claims),
            "successful_verifications": successful_count,
            "base_cost": base_cost,
            "discount_percent": discount_percent,
            "discount_amount": discount_amount,
            "final_cost": final_cost,
            "results": processed_results
        }
    except Exception as e:
        logger.error("batch.failed err=%s", e)
        return JSONResponse(
            status_code=500,
            content={"error": f"Batch processing failed: {str(e)}"}
        )


@app.get("/verify/news")
async def verify_news(request: Request, claim: str):
    """
    Real-time news verification endpoint optimized for breaking news and current events.
    
    Features:
    - Searches NewsAPI for last 48 hours
    - Weights recent sources higher (24h = 1.5x, 7d = 1.2x)
    - Returns publication timestamps for each source
    - Shows age of newest source
    
    Example:
    GET /verify/news?claim=Elon Musk bought Twitter
    
    Response includes:
    - Standard verification result (verdict, confidence, evidence)
    - sources: Array with publication dates and age in hours
    - newest_source_age_hours: Age of most recent source
    """
    logger.info("endpoint.verify_news.called claim=%s", claim)
    
    # Get verification result with news-specific search
    result = await verify_news_claim_logic(claim)
    
    # Content negotiation (same as /verify)
    accept_header = request.headers.get("accept", "application/json").lower()
    
    if not accept_header or accept_header == "*/*" or "application/json" in accept_header:
        return result
    
    elif "text/html" in accept_header:
        from fastapi.responses import HTMLResponse
        
        # Format source timestamps
        sources_html = ""
        if result.get("sources"):
            for s in result["sources"]:
                age_str = f"{s['age_hours']}h ago" if s.get('age_hours') is not None else "Unknown age"
                weight_str = f"weight: {s.get('weight', 1.0):.1f}x"
                sources_html += f'<li><a href="{s["url"]}" target="_blank">{s["url"]}</a><br><small>Published: {age_str} | {weight_str}</small></li>'
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>VerifAI News Result: {claim}</title>
            <style>
                body {{ font-family: system-ui, -apple-system, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }}
                .verdict {{ font-size: 2em; font-weight: bold; margin: 20px 0; }}
                .verified {{ color: #16a34a; }}
                .unverified {{ color: #dc2626; }}
                .inconclusive {{ color: #ea580c; }}
                .confidence {{ font-size: 1.2em; color: #6b7280; }}
                .section {{ margin: 30px 0; padding: 20px; background: #f9fafb; border-radius: 8px; }}
                .news-badge {{ display: inline-block; background: #3b82f6; color: white; padding: 4px 12px; border-radius: 4px; font-size: 0.9em; margin-bottom: 10px; }}
                .freshness {{ color: #16a34a; font-weight: 600; }}
                .sources {{ list-style: none; padding: 0; }}
                .sources li {{ margin: 10px 0; }}
                .sources a {{ color: #2563eb; }}
                .evidence-list {{ list-style: none; padding: 0; }}
                .evidence-item {{ margin: 12px 0; padding: 12px; background: white; border-radius: 6px; border-left: 3px solid #2563eb; }}
                .evidence-for {{ border-left-color: #16a34a; }}
                .evidence-against {{ border-left-color: #dc2626; }}
                .evidence-source {{ font-weight: 600; color: #374151; }}
                .evidence-weight {{ font-size: 0.85em; color: #6b7280; }}
            </style>
        </head>
        <body>
            <h1>VerifAI News Verification</h1>
            <span class="news-badge">🔴 LIVE NEWS</span>
            <p><strong>Claim:</strong> {claim}</p>
            <div class="verdict {result['verdict'].lower()}">{result['verdict']}</div>
            <div class="confidence">Confidence: {result['confidence_score']:.0%}</div>
            {f'<p class="freshness">⚡ Newest source: {result.get("newest_source_age_hours")}h ago</p>' if result.get('newest_source_age_hours') else ''}
            
            <div class="section">
                <h2>⚖️ Judge's Analysis</h2>
                <p>{result.get('reasoning', result.get('summary', ''))}</p>
            </div>
            
            <div class="section">
                <h2>✅ Supporting Evidence (Weight: {sum(e.get('weight', 1.0) for e in result.get('evidence_for', [])):.1f})</h2>
                {('<ul class="evidence-list">' + ''.join(f'<li class="evidence-item evidence-for"><span class="evidence-source">{e.get("source", "Unknown")}</span> <span class="evidence-weight">(weight: {e.get("weight", 1.0)}x)</span><br>{e.get("point", "")}</li>' for e in result.get('evidence_for', [])) + '</ul>') if result.get('evidence_for') else '<p style="color: #6b7280;">No supporting evidence found</p>'}
            </div>
            
            <div class="section">
                <h2>❌ Contradicting Evidence (Weight: {sum(e.get('weight', 1.0) for e in result.get('evidence_against', [])):.1f})</h2>
                {('<ul class="evidence-list">' + ''.join(f'<li class="evidence-item evidence-against"><span class="evidence-source">{e.get("source", "Unknown")}</span> <span class="evidence-weight">(weight: {e.get("weight", 1.0)}x)</span><br>{e.get("point", "")}</li>' for e in result.get('evidence_against', [])) + '</ul>') if result.get('evidence_against') else '<p style="color: #6b7280;">No contradicting evidence found</p>'}
            </div>
            
            <div class="section">
                <h2>📰 News Sources</h2>
                <ul class="sources">
                    {sources_html}
                </ul>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    
    else:
        return result


@app.post("/verify/batch")
async def verify_batch_old(request: Request):
    """
    Batch verification endpoint - verify multiple claims in one request.
    
    Requires x402 payment for the batch (price = 0.05 * number of claims).
    All claims are processed in parallel for faster results.
    
    Request body:
    {
        "claims": ["Claim 1", "Claim 2", "Claim 3"]
    }
    
    Returns:
    {
        "total_claims": 3,
        "total_cost": 0.15,
        "bulk_discount": 0.00,
        "results": [...]
    }
    """
    import asyncio
    from fastapi.responses import JSONResponse
    
    logger.info("endpoint.verify_batch.called")
    
    try:
        body = await request.json()
        claims = body.get("claims", [])
        
        if not claims:
            return JSONResponse(
                status_code=400,
                content={"error": "No claims provided. Include 'claims' array in request body."}
            )
        
        if len(claims) > 100:
            return JSONResponse(
                status_code=400,
                content={"error": "Maximum 100 claims per batch. Please reduce batch size."}
            )
        
        logger.info("batch.processing count=%d", len(claims))
        
        # Process all claims in parallel
        tasks = [verify_claim_logic(claim) for claim in claims]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "claim": claims[i],
                    "verdict": "Error",
                    "confidence_score": 0.0,
                    "summary": f"Processing error: {str(result)}",
                    "payment_status": "refunded_due_to_system_error"
                })
            else:
                # Add original claim to result
                result["claim"] = claims[i]
                processed_results.append(result)
        
        # Calculate totals
        base_cost = len(claims) * 0.05
        refunded_count = sum(1 for r in processed_results if r.get("payment_status", "").startswith("refunded"))
        successful_count = len(claims) - refunded_count
        
        # Bulk discount: 10% off for 5+ claims, 15% off for 10+ claims
        discount_percent = 0
        if len(claims) >= 10:
            discount_percent = 15
        elif len(claims) >= 5:
            discount_percent = 10
        
        discount_amount = (successful_count * 0.05 * discount_percent / 100)
        final_cost = (successful_count * 0.05) - discount_amount
        
        return {
            "total_claims": len(claims),
            "successful_claims": successful_count,
            "refunded_claims": refunded_count,
            "base_cost_usd": base_cost,
            "bulk_discount_percent": discount_percent,
            "bulk_discount_usd": round(discount_amount, 4),
            "final_cost_usd": round(final_cost, 4),
            "results": processed_results
        }
        
    except Exception as e:
        logger.error("batch.failed err=%s", e)
        return JSONResponse(
            status_code=500,
            content={"error": f"Batch processing failed: {str(e)}"}
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


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    Returns service status and basic metrics.
    """
    import psutil
    import time
    
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "VerifAI agent-x402",
        "version": "1.0.2",
        "payment": {
            "enabled": HAS_X402,
            "network": X402_NETWORK,
            "price": X402_PRICE
        },
        "system": {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
    }


@app.post("/feedback")
async def submit_feedback(request: Request):
    """
    Collect user feedback about verification quality.
    
    Request body:
    {
        "claim": "The claim that was verified",
        "rating": 1-5,
        "comment": "Optional feedback text",
        "verdict_received": "True/False/Inconclusive",
        "helpful": true/false
    }
    """
    import json
    import time
    from pathlib import Path
    
    try:
        feedback_data = await request.json()
        
        # Add timestamp and metadata
        feedback_entry = {
            "timestamp": time.time(),
            "user_ip": request.client.host if request.client else "unknown",
            **feedback_data
        }
        
        # Append to feedback log file
        feedback_file = Path("logs/feedback.jsonl")
        feedback_file.parent.mkdir(exist_ok=True)
        
        with open(feedback_file, "a") as f:
            f.write(json.dumps(feedback_entry) + "\n")
        
        logger.info("feedback.submitted rating=%s", feedback_data.get("rating"))
        
        return {
            "status": "success",
            "message": "Thank you for your feedback!"
        }
    
    except Exception as e:
        logger.error("feedback.failed err=%s", e)
        return {
            "status": "error",
            "message": str(e)
        }


@app.get("/metrics")
async def metrics_summary():
    """
    Prometheus-style metrics endpoint for monitoring systems.
    Returns key performance indicators in a structured format.
    """
    import time
    
    try:
        # Get performance metrics
        perf_metrics = PerformanceLogger.get_summary()
        logs = PerformanceLogger.read_logs()
        
        # Calculate uptime metrics
        recent_logs = [log for log in logs if time.time() - log.get("timestamp", 0) < 3600]  # Last hour
        
        # Calculate error rate
        total_recent = len(recent_logs)
        failed_recent = sum(1 for log in recent_logs if log.get("error"))
        error_rate = (failed_recent / total_recent * 100) if total_recent > 0 else 0
        
        return {
            "timestamp": time.time(),
            "performance": {
                "total_requests": perf_metrics.get("total_requests", 0),
                "requests_last_hour": total_recent,
                "error_rate_percent": round(error_rate, 2),
                "avg_execution_time_seconds": perf_metrics.get("avg_execution_time", 0)
            },
            "economics": {
                "total_revenue_usd": perf_metrics.get("total_revenue_usd", 0),
                "total_cost_usd": perf_metrics.get("total_cost_usd", 0),
                "total_profit_usd": perf_metrics.get("total_profit_usd", 0),
                "profit_margin_percent": perf_metrics.get("avg_profit_margin_pct", 0)
            },
            "verdicts": {
                "true_count": sum(1 for log in logs if log.get("verdict") == "True"),
                "false_count": sum(1 for log in logs if log.get("verdict") == "False"),
                "inconclusive_count": sum(1 for log in logs if log.get("verdict") == "Inconclusive")
            }
        }
    
    except Exception as e:
        logger.error("metrics.failed err=%s", e)
        return {
            "timestamp": time.time(),
            "error": str(e),
            "status": "unavailable"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
