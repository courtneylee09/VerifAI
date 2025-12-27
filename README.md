# VerifAI agent-x402

Paid AI verification service using x402 payment protocol with multi-agent debate architecture.

- **Prover Agent**: Builds strongest case FOR the claim (Meta Llama 3.3 70B via DeepInfra)
- **Debunker Agent**: Finds flaws and counter-evidence (DeepSeek-V3 via DeepInfra)
- **Judge Agent**: Weighs arguments and issues final verdict (Claude 3.5 Haiku via Anthropic)
- **Fact Checking**: Real web sources via Exa API with Wikipedia weighted at 0.5x
- **Prediction Support**: Handles weather forecasts, event predictions, and trend analysis
- **Payment**: 0.05 USDC per verification via x402 on Base Sepolia
- **Production Hardening**: Rate limiting, structured logging, circuit-breaker timeouts, HITL thresholding

## Project Structure

```
verification-agent/
├── config/
│   └── settings.py          # Centralized configuration & environment variables
├── src/
│   ├── __init__.py
│   ├── app.py               # FastAPI application with x402 payment wall
│   ├── agents/              # AI agents (Prover, Debunker, Judge)
│   │   ├── __init__.py
│   │   ├── prover.py        # Supporting evidence agent
│   │   ├── debunker.py      # Counter-evidence agent
│   │   └── judge.py         # Verdict synthesis agent
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── search.py        # Exa web search integration
│   │   └── verification.py  # Main verification orchestrator
│   └── middleware/          # Cross-cutting concerns
│       ├── __init__.py
│       ├── rate_limit.py    # Per-IP rate limiting (60 req/min)
│       └── logging_setup.py # Structured logging configuration
├── tests/
│   ├── test_direct.py       # Direct logic testing (bypasses payment)
│   ├── test_weather.py      # Prediction handling test
│   ├── test_goat.py         # Subjective claim test
│   ├── test_paywall.py      # x402 payment flow test
│   └── test_buyer.py        # End-to-end buyer simulation
├── run.py                   # Entry point: starts Uvicorn server
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (not in repo)
├── .env.example             # Template for .env
├── x402.json                # x402 service manifest
└── README.md                # This file
```

## Setup

### Prerequisites

- Python 3.11+
- Base Sepolia testnet RPC (via Coinbase Facilitator)
- API keys for: Exa, DeepInfra, Anthropic, Google Gemini

### Installation

1. **Clone and navigate to project**:
```bash
cd verification-agent
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**:
```bash
cp .env.example .env
# Edit .env with your API keys:
```

Required environment variables:
```
EXA_API_KEY=<your-exa-api-key>
DEEPINFRA_API_KEY=<your-deepinfra-api-key>
ANTHROPIC_API_KEY=<your-anthropic-api-key>
GEMINI_API_KEY=<your-google-gemini-api-key>
MERCHANT_WALLET_ADDRESS=0x3615af0cE7c8e525B9a9C6cE281e195442596559
```

## Running

### Start the Server

```bash
python run.py
```

Server will start on `http://localhost:8001`

Available endpoints:
- `GET /verify?claim=<claim>` - Verify a claim (requires x402 payment)
- `GET /health` - Health check

### Example Requests

**Verify a factual claim**:
```bash
curl "http://localhost:8001/verify?claim=Is%20Rihanna%20the%20founder%20of%20Fenty%20Beauty%3F"
```

**Verify a prediction**:
```bash
curl "http://localhost:8001/verify?claim=Will%20it%20rain%20tomorrow%20in%20New%20York%3F"
```

### Testing

Run verification logic without payment (useful for development):

```bash
# Test basic verification
python -m pytest tests/test_direct.py -v

# Test prediction handling
python -m pytest tests/test_weather.py -v

# Test subjective claims
python -m pytest tests/test_goat.py -v

# Or run directly
python tests/test_direct.py
python tests/test_weather.py
```

## Configuration

All settings are centralized in `config/settings.py`:

- **Rate Limiting**: 60 requests per minute per IP
- **Timeouts**: 20s for Exa search, 30s for debate
- **HITL Threshold**: Confidence < 0.65 triggers manual review flag
- **Source Weighting**: Wikipedia 0.5x, others 1.0x
- **Models**: Llama 70B (Prover), DeepSeek-V3 (Debunker), Claude Haiku (Judge)
- **Fallback**: Gemini 2.0 Flash when DeepInfra fails

## How It Works

1. **Source Retrieval**: Exa API searches for 5 web sources relevant to the claim
2. **Debate Phase**: 
   - Prover finds supporting evidence in parallel
   - Debunker finds counter-evidence in parallel
3. **Judgment**: Claude synthesizes both arguments with source weights
4. **Verification**: Returns verdict (Verified/Unverified/Inconclusive) with confidence score
5. **HITL**: Low confidence (< 0.65) automatically flags for human review

## Payment (x402)

The `/verify` endpoint requires x402 payment of **0.05 USDC on Base Sepolia** before execution.

- x402 middleware intercepts unauthenticated requests
- Returns 402 Payment Required with payment instructions
- After payment confirmed by Coinbase Facilitator, request executes
- Merchant receives payment at configured wallet address

To make verified calls, use an x402-compatible client:
```python
# Example with x402-client
from x402.clients import HttpClient

client = HttpClient(
    endpoint="http://localhost:8001/verify",
    private_key="your_private_key",
    network="base-sepolia"
)

response = client.get("/verify?claim=...")
```

## Performance Metrics

Typical response time: 3-8 seconds
- Source retrieval: ~2-3s (Exa)
- Agent debate: ~2-4s (parallel Prover + Debunker)
- Judge synthesis: ~0.5-1s (Claude)

## Logging

Structured logging provides observability:
```
2024-12-26 10:15:42,123 | INFO | verify.start claim=Is Rihanna the founder of Fenty Beauty?
2024-12-26 10:15:42,234 | INFO | claim.type=factual
2024-12-26 10:15:44,567 | INFO | sources.retrieved count=5
2024-12-26 10:15:44,789 | INFO | debate.start
2024-12-26 10:15:45,234 | INFO | debate.done prover_len=142 debunker_len=156
2024-12-26 10:15:45,678 | INFO | verify.done verdict=Verified confidence=0.95 ms=3567.8 manual_review=False
2024-12-26 10:15:45,789 | INFO | request path=/verify ip=127.0.0.1 status=200 ms=34.5
```

## Deployment

### Railway / Render

1. Push code to GitHub
2. Create new project, connect repo
3. Set environment variables in dashboard
4. Configure startup command: `python run.py`
5. Expose port 8001

### Docker (Optional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "run.py"]
```

## Production Considerations

- ✅ Rate limiting per IP (prevents abuse)
- ✅ Circuit-breaker timeouts (prevents hanging requests)
- ✅ HITL threshold (flags low-confidence verdicts for review)
- ✅ Structured logging (enables debugging and monitoring)
- ✅ Fallback models (DeepInfra → Gemini graceful degradation)
- ⚠️ Consider: Caching for repeated claims
- ⚠️ Consider: Database for audit trail retention
- ⚠️ Consider: Redis for distributed rate limiting
- ⚠️ Consider: Observability (DataDog, NewRelic, etc.)

## API Response Format

```json
{
  "verdict": "Verified|Unverified|Inconclusive",
  "confidence_score": 0.95,
  "citations": ["https://example.com", ...],
  "claim_type": "factual|prediction",
  "summary": "Based on X and Y sources, the claim is verified with high confidence.",
  "debate": {
    "prover": "Evidence supporting the claim: ...",
    "debunker": "Counter-evidence: ..."
  },
  "audit_trail": "Multi-agent debate: Prover (...) vs Debunker (...). Judge: (...)",
  "manual_review": false
}
```

## Troubleshooting

**DeepInfra 401 Unauthorized**: Check `DEEPINFRA_API_KEY` is correct and account has credits
**DeepInfra 402 No Balance**: Top up account balance at deepinfra.com
**Exa 429 Rate Limited**: Check Exa API key and rate limit quota
**Agent Timeouts**: Increase `DEBATE_TIMEOUT_SECONDS` in `config/settings.py`
**x402 Payment Issues**: Verify merchant wallet address matches configuration

## License

This project is provided as-is for educational and commercial use.

## Contact

For questions or issues, please file a GitHub issue or contact the development team.
