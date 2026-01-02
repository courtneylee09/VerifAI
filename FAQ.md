# VerifAI FAQ - Frequently Asked Questions

**Quick answers to common questions about VerifAI**

---

## General Questions

### What is VerifAI?

VerifAI is an AI-powered fact-checking service that uses three specialized AI agents to verify claims. Instead of asking one AI for an answer, VerifAI has agents debate both sides of your claim before a judge delivers a final verdict.

### How is VerifAI different from ChatGPT or other AI tools?

| Feature | VerifAI | Single AI (ChatGPT, etc.) |
|---------|---------|---------------------------|
| **Approach** | Multi-agent debate | Single response |
| **Bias Control** | Agents challenge each other | Potential confirmation bias |
| **Sources** | Real-time web search | Training data only |
| **Verification** | Prover + Debunker + Judge | One model's opinion |
| **Confidence** | Explicit score (0-100%) | Often overconfident |
| **Refunds** | Auto-refund if uncertain | No refunds |

### Is VerifAI free?

No, VerifAI costs **$0.05 USDC** per verification. However:
- You only pay for conclusive results
- Inconclusive results (confidence <40%) are automatically refunded
- No subscription fees
- No hidden costs

---

## How It Works

### What are the three agents?

1. **Prover** (Llama 3.3 70B) - Finds evidence FOR your claim
2. **Debunker** (DeepSeek-V3) - Finds evidence AGAINST your claim
3. **Judge** (Claude 3.5 Haiku) - Weighs both arguments and decides

### How long does verification take?

Most verifications complete in **10-15 seconds**. Complex claims with many sources may take up to 20 seconds.

### Where does VerifAI get its information?

VerifAI searches the live web using Exa API, including:
- News websites
- Wikipedia (weighted at 50% trust)
- Academic sources (.edu domains)
- Government sites (.gov domains)
- Reputable publications

### Can VerifAI access paywalled content?

No. VerifAI only searches publicly available web content.

---

## Accuracy & Reliability

### How accurate is VerifAI?

Accuracy depends on the claim type:

- **Well-documented facts:** 90-95% accurate
- **Recent events:** 80-90% accurate (depends on source quality)
- **Controversial topics:** 70-85% accurate (confidence score reflects uncertainty)
- **Subjective claims:** Automatically marked inconclusive (refunded)

Always check the **confidence score** and review **sources** yourself for important decisions.

### What does the confidence score mean?

| Score | Interpretation |
|-------|----------------|
| **90-100%** | Extremely confident - very likely accurate |
| **80-89%** | Highly confident - trust this result |
| **70-79%** | Confident - generally reliable |
| **60-69%** | Moderately confident - some uncertainty |
| **50-59%** | Uncertain - conflicting evidence |
| **40-49%** | Low confidence - **refunded** |
| **0-39%** | Very uncertain - **refunded** |

### What if VerifAI gets something wrong?

VerifAI is a tool, not perfect. If you believe a result is wrong:
1. Check the sources provided - click through and read them
2. Look at the confidence score - was it low?
3. Review both Prover and Debunker arguments
4. Consider the nuance - was the claim partially true?

For persistent issues, report via GitHub.

### Can VerifAI be biased?

VerifAI is designed to minimize bias through:
- **Adversarial agents** - Prover and Debunker challenge each other
- **Multiple models** - Different AI companies, different training
- **Real sources** - Live web search, not just training data
- **Transparent reasoning** - You see both sides of the argument

However, AI can still have inherent biases. Always think critically.

---

## Pricing & Payment

### Why does VerifAI cost money?

Running three state-of-the-art AI models and real-time web searches costs money. The $0.05 fee covers:
- AI model API costs (~$0.004)
- Web search costs
- Server infrastructure
- Service maintenance

### What payment methods are accepted?

Currently: **USDC (USD Coin)** on Base Sepolia testnet

Coming soon: Mainnet deployment with real USDC

### Do I pay if the result is "Inconclusive"?

**No!** If confidence is below 40%, you get an automatic refund. You only pay for conclusive answers.

### Are there any refund policies?

**Automatic refunds:**
- Confidence <40%: Full refund
- Philosophical/subjective claims: Full refund
- Service errors: Full refund

**No refunds for:**
- Conclusive results (confidence ≥40%)
- Results you disagree with (but were conclusive)

### Can I get bulk pricing?

Not yet. Volume discounts coming in Phase 2. Contact us for enterprise needs.

---

## Technical Questions

### What AI models does VerifAI use?

- **Prover:** Meta Llama 3.3 70B (via DeepInfra)
- **Debunker:** DeepSeek-V3 (via DeepInfra)
- **Judge:** Claude 3.5 Haiku (via Anthropic)
- **Fallback:** Gemini 2.0 Flash (free tier)

### What is x402?

x402 is a protocol for paid API requests using cryptocurrency. It allows:
- Pay-per-use pricing
- Instant, gasless payments
- No user accounts needed
- Cryptographic payment proofs

### What is Base Sepolia?

Base Sepolia is a testnet (test network) for Base, an Ethereum Layer 2. It uses test USDC (not real money yet). Mainnet deployment coming soon.

### Do you store my data?

We store:
- ✅ Claims you verify (for service improvement)
- ✅ Verdicts and confidence scores
- ✅ Timestamps
- ✅ Public wallet addresses (for payment)

We DON'T store:
- ❌ Personal information
- ❌ Email addresses
- ❌ Private keys
- ❌ IP addresses (beyond temporary rate limiting)

### Is my payment secure?

Yes! Payments use EIP-712 signatures, which are:
- Cryptographically secure
- Gasless (no transaction fees)
- Non-custodial (your keys stay with you)
- Instant

---

## Using VerifAI

### What types of claims work best?

**Best for VerifAI:**
- ✅ Historical facts: "World War II ended in 1945"
- ✅ Scientific claims: "Water boils at 100°C at sea level"
- ✅ Verifiable stats: "The Earth has ~8 billion people"
- ✅ News fact-checking: "Did this politician say X?"

**Not ideal:**
- ❌ Opinions: "Is democracy the best system?"
- ❌ Predictions: "Will Bitcoin reach $100k?"
- ❌ Subjective: "Is this movie good?"
- ❌ Personal data: "What's my password?"

### Can I verify future predictions?

VerifAI can evaluate predictions based on current data (e.g., weather forecasts), but cannot predict the future. Confidence will be low for speculative claims.

### Can I verify images or videos?

Not yet. Currently, VerifAI only verifies text-based claims. Multimodal verification coming in future phases.

### How many verifications can I do?

Rate limit: **60 requests per minute** per IP address. For higher limits, contact us.

### Can I verify claims in other languages?

Currently, VerifAI works best with English claims. Other languages may work but aren't officially supported yet.

---

## Dashboard & Analytics

### What can I see in the dashboard?

- Total verifications you've made
- Revenue (how much you've spent)
- Verification history table with all past results
- Verdict distribution
- Cost breakdown per request

### Who can see my verification history?

Only you can see your specific verifications. The dashboard shows:
- **Private:** Your individual verifications (only visible to you via wallet)
- **Public:** Aggregate statistics (total verifications, economics)

### What do the analytics show?

- Verdict distribution (pie chart)
- Economics (revenue vs costs vs profit)
- Token usage by AI agent
- Agent performance metrics
- Average execution time

### Why is profit margin shown?

Transparency! VerifAI shows you exactly how much it costs to run (LLM API costs) vs. what you pay. Typical margin is 92%+.

---

## Troubleshooting

### My verification returned "Inconclusive"

This means:
- Evidence was contradictory
- Sources disagreed
- Claim was too vague or subjective

You were **automatically refunded**. Try:
1. Rephrasing your claim more specifically
2. Breaking complex claims into simpler parts
3. Adding context (dates, locations, etc.)

### I got "Payment Required" but I paid

Possible causes:
1. Payment didn't process - check wallet
2. Network delay - wait 30 seconds and retry
3. Insufficient USDC balance
4. Wrong network (must be Base Sepolia)

### Dashboard shows "No verifications yet"

Causes:
- You haven't made any verifications yet
- Verifications were on a different wallet address
- Cache issue - hard refresh (Ctrl+F5)

### Sources look unreliable

VerifAI searches the live web, which includes:
- High-quality sources (Wikipedia, .edu, .gov)
- News sites (varies in quality)
- Blogs (lowest trust)

**What to do:**
1. Check the confidence score - low scores mean questionable sources
2. Click through and verify sources yourself
3. Trust the Debunker - it will challenge bad sources

### Verification taking too long

Normal time: 10-15 seconds

If longer than 30 seconds:
1. Check /health endpoint for service status
2. Your claim may be complex (many sources)
3. Service may be under heavy load
4. Report if persistent

---

## Account & Billing

### Do I need to create an account?

No! VerifAI is account-free. Just pay with your wallet and verify.

### How do I track my spending?

Visit the dashboard: https://verifai-production.up.railway.app/dashboard

It shows all your verifications and total spent.

### Can I get a receipt?

Your wallet transaction is the receipt. Check your wallet history for:
- Transaction hash
- Amount paid (0.05 USDC)
- Timestamp
- Recipient address

### What if I run out of USDC?

Add more USDC to your wallet on Base Sepolia testnet. Once mainnet launches, you can use real USDC.

---

## Enterprise & Developers

### Is there an API?

Yes! Visit https://verifai-production.up.railway.app/ for API docs.

### Can I integrate VerifAI into my app?

Absolutely! See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for:
- API endpoints
- Payment flow
- Response schema
- Example code

### Do you offer webhooks?

Not yet. Coming in Phase 2.

### Can I white-label VerifAI?

Enterprise licensing available. Contact us to discuss.

### What about SLAs?

Currently: Best-effort (99%+ uptime)

Enterprise SLAs available for high-volume users.

---

## Safety & Ethics

### Can VerifAI be used to spread misinformation?

VerifAI is designed to **combat** misinformation by:
- Providing transparent, source-backed verdicts
- Showing confidence scores
- Refunding uncertain results
- Exposing both supporting and contradicting evidence

Misuse is against our terms of service.

### What if someone verifies harmful content?

VerifAI verifies claims, not opinions. It will:
- Mark subjective/harmful claims as inconclusive
- Provide factual context where applicable
- Not make moral judgments

### Is VerifAI GDPR compliant?

We don't collect personal data, so GDPR is minimal concern. We store:
- Claims (anonymized in analytics)
- Public wallet addresses
- Timestamps

No email, name, or private data is collected.

### Can VerifAI be audited?

Yes! The code is open-source on GitHub. Performance logs are public in the dashboard.

---

## Future Features

### What's coming next?

**Phase 2 (Q1 2026):**
- Mainnet deployment (real USDC)
- Batch verification API
- Webhook support
- Enhanced dashboard filters

**Phase 3 (Q2 2026):**
- Multi-language support
- Image/video verification
- Dispute resolution
- Custom verification templates

### Will pricing change?

Current price ($0.05) is stable for Phase 1. Future changes will be announced with notice.

### Can I suggest features?

Yes! Open an issue on GitHub: https://github.com/courtneylee09/VerifAI

---

## Still Have Questions?

- **Documentation:** [GETTING_STARTED.md](GETTING_STARTED.md) | [USER_GUIDE.md](USER_GUIDE.md)
- **Dashboard:** https://verifai-production.up.railway.app/dashboard
- **Health Check:** https://verifai-production.up.railway.app/health
- **GitHub:** https://github.com/courtneylee09/VerifAI
