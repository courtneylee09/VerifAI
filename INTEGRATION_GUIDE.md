# VerifAI Machine-to-Machine Integration Guide

## Standard Integration Pattern (Recommended)

For seamless M2M integration, VerifAI follows **standard REST API conventions** used by 98% of production APIs.

### Quick Start (Python)

```python
import requests

# 1. Discover payment requirements (no payment needed for 402 response)
response = requests.get(
    "https://verifai-production.up.railway.app/verify?claim=Is the Earth round?"
)

# Server returns 402 Payment Required with payment details
payment_info = response.json()
# {
#   "x402Version": 1,
#   "accepts": [{
#     "network": "base-sepolia",
#     "payTo": "0x3615af...",
#     "amount": "50000",  # 0.05 USDC
#     "resource": "https://verifai-production.up.railway.app/verify?claim=...",
#     "mimeType": "application/json",
#     "outputSchema": {...}  # JSON Schema of response
#   }]
# }

# 2. Generate payment signature (using your wallet)
payment_signature = your_wallet.sign_x402_payment(payment_info)

# 3. Make paid request with signature
response = requests.get(
    "https://verifai-production.up.railway.app/verify?claim=Is the Earth round?",
    headers={
        "X-PAYMENT": payment_signature  # Base64-encoded payment proof
    }
)

# 4. Parse JSON result (default format)
result = response.json()
print(f"Verdict: {result['verdict']}")
print(f"Confidence: {result['confidence']}")
print(f"Reasoning: {result['reasoning']}")
```

### Standard M2M Conventions Used

✅ **JSON by default** - No Accept header needed, just works  
✅ **HTTP status codes** - 402 for payment required, 200 for success  
✅ **Standard headers** - Accept, Content-Type, X-PAYMENT (x402 spec)  
✅ **RESTful URLs** - `/verify?claim={claim}` (readable, cacheable)  
✅ **JSON Schema** - Machine-readable schema in payment response  
✅ **HTTPS only** - Secure by default  

### Content Negotiation (Optional)

**Most M2M clients don't need this** - just use the default JSON. But if you want other formats:

```python
# Request HTML (for human viewing)
response = requests.get(
    "https://verifai-production.up.railway.app/verify?claim=...",
    headers={
        "Accept": "text/html",
        "X-PAYMENT": "..."
    }
)
html_page = response.text

# Request plain text (for simple parsing)
response = requests.get(
    "https://verifai-production.up.railway.app/verify?claim=...",
    headers={
        "Accept": "text/plain",
        "X-PAYMENT": "..."
    }
)
text_result = response.text
```

### Response Schema (JSON)

```json
{
  "claim": "Is the Earth round?",
  "verdict": "True",
  "confidence": 0.95,
  "reasoning": "Overwhelming scientific consensus...",
  "prover_argument": "Arguments supporting the claim...",
  "debunker_argument": "Potential counter-arguments...",
  "sources": [
    {
      "title": "Earth - Wikipedia",
      "url": "https://en.wikipedia.org/wiki/Earth",
      "snippet": "The Earth is an oblate spheroid..."
    }
  ],
  "execution_time_seconds": 12.34,
  "total_cost_usd": 0.0035
}
```

### Error Handling

```python
response = requests.get("https://verifai-production.up.railway.app/verify?claim=...")

if response.status_code == 402:
    # Payment required - normal first response
    payment_info = response.json()
    # Generate payment signature and retry...
    
elif response.status_code == 200:
    # Success - paid request completed
    result = response.json()
    
elif response.status_code == 429:
    # Rate limit exceeded (60 requests/minute)
    retry_after = response.headers.get('Retry-After')
    
elif response.status_code == 422:
    # Validation error (missing claim parameter, etc.)
    error = response.json()
    
elif response.status_code >= 500:
    # Server error - retry with exponential backoff
    pass
```

## Integration Checklist

- [ ] **Use HTTPS** - All requests must use https://
- [ ] **Default to JSON** - Don't send Accept header unless you need HTML/text
- [ ] **Handle 402** - First request returns payment info, second request includes X-PAYMENT header
- [ ] **Validate schema** - Check outputSchema in payment response matches your expectations
- [ ] **Handle rate limits** - Max 60 requests/minute per IP
- [ ] **Implement retries** - Use exponential backoff for 5xx errors
- [ ] **Cache results** - Same claim = same answer (for 24h)
- [ ] **Check confidence** - Use confidence score to decide if you trust the verdict

## Comparison to Other Standards

### REST API (what we use)
```
✅ Universal support (every language/framework)
✅ Human-readable URLs
✅ HTTP status codes for errors
✅ Cacheable responses
```

### GraphQL
```
❌ Not suitable for x402 (payment happens before query execution)
❌ Requires GraphQL client library
✅ Flexible queries (not needed for single-purpose verification)
```

### gRPC
```
❌ Binary protocol (not browser-compatible for wallets)
❌ Requires protobuf definitions
✅ Faster (but negligible for AI workloads)
```

### x402 Protocol
```
✅ Built on top of standard HTTP/REST
✅ Works with any HTTP client
✅ No special libraries needed (just add X-PAYMENT header)
```

## Why This Approach is Standard

1. **99% of production APIs use REST + JSON** - Stripe, OpenAI, GitHub, AWS, etc.
2. **Accept header is optional** - Most M2M clients just use default JSON
3. **x402 adds payment, not complexity** - Same REST patterns, just add one header
4. **Framework-agnostic** - Works from any language: Python, JS, Go, Rust, etc.
5. **Browser-compatible** - Wallets can use it without special protocols

## Example Integrations

### JavaScript/Node.js
```javascript
const response = await fetch(
  'https://verifai-production.up.railway.app/verify?claim=...',
  {
    headers: {
      'X-PAYMENT': paymentSignature
    }
  }
);
const result = await response.json();
```

### Go
```go
req, _ := http.NewRequest("GET", "https://verifai-production.up.railway.app/verify?claim=...", nil)
req.Header.Set("X-PAYMENT", paymentSignature)
resp, _ := client.Do(req)
var result map[string]interface{}
json.NewDecoder(resp.Body).Decode(&result)
```

### curl (command line)
```bash
curl "https://verifai-production.up.railway.app/verify?claim=test" \
  -H "X-PAYMENT: base64_signature_here"
```

---

**Bottom line:** VerifAI uses the same patterns as every major API (Stripe, OpenAI, etc.). If you've integrated with any REST API before, this will feel familiar. x402 just adds payment - everything else is standard HTTP.
