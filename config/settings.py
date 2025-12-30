"""
Configuration and environment variables for VerifAI agent-x402.
Centralizes all settings to enable easy customization.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# API Keys and Credentials
# ============================================================================
EXA_API_KEY = os.getenv("EXA_API_KEY")
DEEPINFRA_API_KEY = os.getenv("DEEPINFRA_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MERCHANT_WALLET_ADDRESS = os.getenv("MERCHANT_WALLET_ADDRESS")

# ============================================================================
# x402 Payment Configuration
# ============================================================================
X402_PRICE = "0.05"  # USDC per verification
X402_NETWORK = "base-sepolia"
X402_DESCRIPTION = "VerifAI agent-x402 Verification Check"

# Default MIME type (clients can override with Accept header)
X402_MIME_TYPE = "application/json"  # Default to JSON for machines

# Supported output formats (via Accept header content negotiation)
SUPPORTED_FORMATS = {
    "application/json": "Machine-readable JSON with full data",
    "text/html": "Human-readable HTML page with formatting",
    "text/plain": "Simple plain text format"
}

# Output schema - tells machines what JSON structure to expect
X402_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "claim": {"type": "string", "description": "The claim that was verified"},
        "verdict": {"type": "string", "enum": ["True", "False", "Inconclusive"], "description": "Final verdict from the judge"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1, "description": "Confidence score (0-1)"},
        "reasoning": {"type": "string", "description": "Judge's reasoning for the verdict"},
        "prover_argument": {"type": "string", "description": "Arguments supporting the claim"},
        "debunker_argument": {"type": "string", "description": "Arguments contradicting the claim"},
        "sources": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "url": {"type": "string"},
                    "snippet": {"type": "string"}
                }
            },
            "description": "Web sources used in verification"
        },
        "execution_time_seconds": {"type": "number"},
        "total_cost_usd": {"type": "number"}
    },
    "required": ["claim", "verdict", "confidence", "reasoning"],
    "note": "Use Accept header to request different formats: application/json (default), text/html, or text/plain"
}

# Base URL for production (Railway uses HTTPS)
SERVICE_BASE_URL = os.getenv("SERVICE_BASE_URL", "https://verifai-production.up.railway.app")

# ============================================================================
# Rate Limiting Configuration
# ============================================================================
RATE_LIMIT_MAX = 60  # requests per window per IP
RATE_LIMIT_WINDOW_SECONDS = 60

# ============================================================================
# AI Model Configuration
# ============================================================================
DEEPINFRA_BASE_URL = "https://api.deepinfra.com/v1/openai"
PROVER_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
DEBUNKER_MODEL = "deepseek-ai/DeepSeek-V3"
JUDGE_MODEL = "claude-3-5-haiku-20241022"
GEMINI_FALLBACK_MODEL = "gemini-2.0-flash-exp"

# ============================================================================
# Timeout Configuration (Circuit Breaker Pattern)
# ============================================================================
EXA_SEARCH_TIMEOUT_SECONDS = 20
DEBATE_TIMEOUT_SECONDS = 30

# ============================================================================
# Verification Configuration
# ============================================================================
EXA_NUM_RESULTS = 5
MAX_SOURCE_TEXT_LENGTH = 500

PREDICTION_KEYWORDS = [
    'will', 'forecast', 'predict', 'expect', 'likely', 'probably',
    'going to', 'next week', 'tomorrow', 'this week', 'future',
    'by 2026', 'by 2030', 'in the coming'
]

# ============================================================================
# HITL (Human-in-the-Loop) Configuration
# ============================================================================
CONFIDENCE_THRESHOLD_FOR_MANUAL_REVIEW = 0.65  # Confidence below this triggers manual review

# ============================================================================
# Logging Configuration
# ============================================================================
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"

# ============================================================================
# Prover Agent Configuration
# ============================================================================
PROVER_TEMPERATURE = 0.3
PROVER_MAX_TOKENS = 200
PROVER_SYSTEM_PROMPT = "You are a persuasive advocate who supports the claim using provided sources."

# ============================================================================
# Debunker Agent Configuration
# ============================================================================
DEBUNKER_TEMPERATURE = 0.4
DEBUNKER_MAX_TOKENS = 200
DEBUNKER_SYSTEM_PROMPT = "You are a critical fact-checker who finds flaws in claims using provided sources."

# ============================================================================
# Judge Agent Configuration
# ============================================================================
JUDGE_MAX_TOKENS = 500

# ============================================================================
# Server Configuration
# ============================================================================
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8001
