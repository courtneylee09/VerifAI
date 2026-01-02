# Getting Started with VerifAI

**Welcome to VerifAI** - Your AI-powered fact-checking service using advanced multi-agent debate.

---

## What is VerifAI?

VerifAI helps you verify claims, facts, and statements using cutting-edge AI technology. Instead of relying on a single AI model, VerifAI uses **three specialized AI agents** that debate each claim:

- 🔵 **Prover** - Finds evidence supporting the claim
- 🔴 **Debunker** - Finds evidence against the claim  
- ⚖️ **Judge** - Weighs both sides and delivers a final verdict

This multi-agent approach gives you more reliable, balanced results than asking a single AI.

---

## How It Works (Simple)

1. **Submit a claim** - Ask any factual question
2. **Pay $0.05 USDC** - One-time payment via crypto wallet
3. **Get your verdict** - Verified, Unverified, or Inconclusive with full reasoning
4. **View history** - See all your past verifications in the dashboard

---

## Quick Start Guide

### Step 1: Visit the Service

Go to: **https://verifai-production.up.railway.app**

### Step 2: Make Your First Verification

**Option A: Use the API** (for developers)
```
GET https://verifai-production.up.railway.app/verify?claim=The Earth is round
```

**Option B: Use a Wallet Client** (coming soon)
- Install an x402-compatible wallet
- Navigate to VerifAI
- Enter your claim
- Approve the $0.05 USDC payment
- Receive instant results

### Step 3: View Your Results

Visit the **Dashboard** to see your verification history:
- https://verifai-production.up.railway.app/dashboard

---

## What Can You Verify?

### ✅ Great Questions for VerifAI

**Factual Claims:**
- "The Great Wall of China is visible from space"
- "Drinking 8 glasses of water daily is necessary"
- "Bitcoin was invented in 2009"

**Historical Facts:**
- "The first moon landing was in 1969"
- "Albert Einstein won the Nobel Prize in Physics"
- "The internet was invented by the military"

**Scientific Claims:**
- "Vaccines cause autism" (VerifAI will debunk this)
- "Climate change is caused by human activity"
- "Honey never spoils"

**Current Events:**
- "Did [politician] make this statement?"
- "What's the latest unemployment rate?"
- "Is this news article accurate?"

### ❌ Questions VerifAI Can't Answer Well

**Opinions/Subjective Matters:**
- "Is capitalism good?" - This is opinion-based
- "Who is the best athlete?" - Subjective
- "Is this art beautiful?" - Personal preference

**Future Predictions (with caveats):**
- "Will it rain tomorrow?" - VerifAI can check forecasts but can't predict the future
- "Who will win the election?" - No one knows for certain

**Personal Information:**
- "What's my account balance?" - VerifAI has no access to private data
- "Do I have a medical condition?" - Not a replacement for medical advice

---

## Understanding Your Results

### Verdict Types

**✅ Verified** (Confidence: 70-100%)
- The claim is **likely true** based on available evidence
- Strong support from multiple reliable sources
- Little to no contradicting evidence

**❌ Unverified** (Confidence: 70-100%)
- The claim is **likely false** based on available evidence
- Strong contradicting evidence
- Reliable sources dispute the claim

**⚠️ Inconclusive** (Confidence: 40-70%)
- **Not enough evidence** to determine truth
- Conflicting information from sources
- May be partially true or context-dependent
- **Automatic refund** - You won't be charged for these

**❓ Uncertain** (Confidence: <40%)
- **Highly uncertain** - extremely limited evidence
- Question may be too vague or subjective
- **Automatic refund** - You won't be charged

### What's Included in Each Result

1. **Verdict** - Verified, Unverified, Inconclusive, or Uncertain
2. **Confidence Score** - How certain VerifAI is (0-100%)
3. **Judge's Reasoning** - Why this verdict was reached
4. **Prover's Arguments** - Evidence supporting the claim
5. **Debunker's Arguments** - Evidence against the claim
6. **Sources** - Links to real websites where evidence was found
7. **Execution Time** - How long the verification took

---

## Pricing & Payment

### Simple Pricing
- **$0.05 USDC** per verification
- Pay only for **conclusive results** (confidence ≥40%)
- **Automatic refunds** for inconclusive/uncertain results
- No subscriptions, no hidden fees

### Payment Method
- **USDC** (USD Coin) on Base Sepolia testnet
- Pay via any x402-compatible wallet
- Instant, gasless transactions

### Why So Cheap?
- Uses efficient AI models (92%+ profit margin)
- Automated process with no human overhead
- Volume pricing - we serve many users

---

## Privacy & Security

### What We Collect
- Your claim/question
- Timestamp of verification
- Verdict and confidence score
- Public wallet address (for payment)

### What We DON'T Collect
- Personal information
- Email addresses
- IP addresses (beyond rate limiting)
- Private wallet keys

### Data Retention
- Verification results stored indefinitely in logs
- Used for improving service quality
- Aggregated analytics only (no personal data shared)

---

## FAQ

### How accurate is VerifAI?
VerifAI uses three state-of-the-art AI models and searches real web sources. For well-documented facts, accuracy is very high (90%+). For nuanced or recent claims, check the confidence score.

### What if I disagree with the verdict?
The confidence score tells you how certain VerifAI is. Low confidence (40-70%) means there's debate. You can review the sources and judge for yourself.

### Do I get refunded for inconclusive results?
**Yes!** If confidence is below 40%, you get an automatic refund. You only pay for conclusive answers.

### Can I verify multiple claims at once?
Currently, each verification is separate. Bulk API coming in Phase 2.

### How fast is verification?
Most verifications complete in **10-15 seconds**.

### What if the service is down?
Check https://verifai-production.up.railway.app/health for status. We have 99%+ uptime.

### Can I use this commercially?
Yes! Use VerifAI for fact-checking in your app, website, or business. Contact us for API access.

### Is my payment secure?
Yes! Payments use the x402 protocol with cryptographic signatures. Your wallet keys never leave your device.

---

## Support & Contact

### Need Help?
- **Dashboard:** https://verifai-production.up.railway.app/dashboard
- **API Docs:** https://verifai-production.up.railway.app/
- **Health Check:** https://verifai-production.up.railway.app/health

### Report Issues
- GitHub: https://github.com/courtneylee09/VerifAI
- Check logs: https://verifai-production.up.railway.app/analytics

---

## Next Steps

1. **Try a verification** - Start with a simple factual claim
2. **Explore the dashboard** - See how verdicts are distributed
3. **Check analytics** - View performance metrics and economics
4. **Read the API docs** - Integrate VerifAI into your app

**Ready to get started?** Visit https://verifai-production.up.railway.app/verify?claim=Your+question+here
