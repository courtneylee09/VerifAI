"""
Entry point for VerifAI agent-x402 FastAPI server.
Starts Uvicorn with the configured app and settings.
Supports Railway deployment by reading PORT from environment.
"""
import os
import uvicorn
from config.settings import SERVER_HOST

if __name__ == "__main__":
    # Railway sets PORT environment variable; fall back to config for local dev
    port = int(os.getenv("PORT", 8001))
    
    uvicorn.run(
        "src.app:app",
        host=SERVER_HOST,
        port=port,
        reload=False,
        log_level="info"
    )
