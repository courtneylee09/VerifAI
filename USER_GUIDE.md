# VerifAI User Guide

**The Complete Guide to Using VerifAI for Fact-Checking**

---

## Table of Contents

1. [Understanding VerifAI](#understanding-verifai)
2. [Making Your First Verification](#making-your-first-verification)
3. [Reading Results](#reading-results)
4. [Using the Dashboard](#using-the-dashboard)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

---

## Understanding VerifAI

### The Three-Agent System

VerifAI doesn't just ask one AI for an answer. Instead, it uses a **debate-style approach**:

**1. The Prover (Llama 3.3 70B)**
- Role: Defense attorney
- Job: Find the strongest evidence SUPPORTING your claim
- Searches: Real-time web sources
- Bias: Optimistic - assumes the claim might be true

**2. The Debunker (DeepSeek-V3)**
- Role: Prosecutor
- Job: Find evidence AGAINST your claim
- Searches: Same real-time sources
- Bias: Skeptical - looks for flaws and contradictions

**3. The Judge (Claude 3.5 Haiku)**
- Role: Impartial decision-maker
- Job: Read both arguments and decide
- Output: Final verdict with confidence score
- Bias: None - weighs evidence objectively

### Why This Works Better

**Single AI problems:**
- ❌ Confirmation bias
- ❌ Hallucinations
- ❌ No self-correction

**Multi-agent benefits:**
- ✅ Balanced perspective
- ✅ Self-checking (agents challenge each other)
- ✅ Higher confidence in results
- ✅ Transparent reasoning

---

## Making Your First Verification

### Step-by-Step Process

#### Step 1: Formulate Your Question

**Good questions are:**
- Specific: "Bitcoin was invented in 2009" ✅
- Not vague: "Is Bitcoin good?" ❌

- Factual: "The Eiffel Tower is 330 meters tall" ✅
- Not opinion: "The Eiffel Tower is beautiful" ❌

- Clear: "Did Albert Einstein win a Nobel Prize?" ✅
- Not ambiguous: "Was Einstein successful?" ❌

#### Step 2: Submit Your Claim

**Method A: Direct API Request**

Using your browser or API tool:
```
https://verifai-production.up.railway.app/verify?claim=The Earth orbits the Sun
```

**Method B: Via Wallet (Recommended)**

1. Open your x402-compatible wallet
2. Navigate to VerifAI service
3. Type your claim in the input field
4. Click "Verify"

#### Step 3: Review Payment Details

You'll see:
- **Price:** $0.05 USDC
- **Network:** Base Sepolia
- **Recipient:** VerifAI merchant wallet
- **What you get:** Full verification with sources

#### Step 4: Approve Payment

- Your wallet will request approval
- Transaction is gasless (no gas fees!)
- Uses EIP-712 signature (secure)
- Payment processes instantly

#### Step 5: Receive Results

Within 10-15 seconds, you'll get:
- ✅ Verdict (Verified/Unverified/Inconclusive)
- 📊 Confidence score
- 📝 Detailed reasoning
- 🔗 Source links
- 💬 Both agents' arguments

---

## Reading Results

### The Verdict Screen

Here's what each part means:

```
┌─────────────────────────────────────┐
│ CLAIM: "Bitcoin was invented in 2009" │
│                                     │
│ VERDICT: ✅ Verified                │
│ CONFIDENCE: 95%                     │
└─────────────────────────────────────┘
```

#### Confidence Score Guide

| Score | Meaning | Action |
|-------|---------|--------|
| **90-100%** | Extremely confident | Trust this verdict |
| **70-89%** | Very confident | Likely accurate |
| **50-69%** | Moderately confident | Some uncertainty remains |
| **40-49%** | Low confidence | Inconclusive (refunded) |
| **0-39%** | Very uncertain | Inconclusive (refunded) |

### Judge's Reasoning

Example:
```
"Based on overwhelming historical evidence and multiple 
reliable sources including the original Bitcoin whitepaper 
published by Satoshi Nakamoto in October 2008, and the 
first Bitcoin transaction in January 2009, this claim is 
verified. The Debunker found no credible contradicting 
evidence."
```

**What to look for:**
- ✅ Mentions specific sources
- ✅ Acknowledges counterarguments
- ✅ Explains confidence level
- ✅ Notes any caveats or context

### Prover's Argument

Shows evidence SUPPORTING the claim:
```
"The Bitcoin whitepaper was published in October 2008,
and the first block was mined on January 3, 2009. This
is documented across multiple sources including:
- bitcoin.org (official site)
- Wikipedia
- Blockchain explorer records"
```

### Debunker's Argument

Shows evidence AGAINST the claim (if any):
```
"While the claim states 2009, technically development 
began in 2008 with the whitepaper. However, the actual
network launch and first transaction did occur in 
January 2009, so the claim is substantially accurate."
```

### Sources Section

Each source shows:
- 📄 **Title** - Name of the webpage
- 🔗 **URL** - Direct link (click to verify yourself)
- 📝 **Snippet** - Relevant excerpt from the page

**Source quality indicators:**
- Wikipedia - Weighted 50% (cautious but useful baseline)
- .edu domains - Academic (high trust)
- .gov domains - Government (high trust)
- News sites - Varies (check reputation)

---

## Using the Dashboard

### Overview Page

Visit: https://verifai-production.up.railway.app/dashboard

**Top Cards Show:**
1. **Total Verifications** - How many you've done
2. **Revenue** - How much you've spent (USDC)
3. **Net Profit** - Service economics (transparency!)
4. **Profit Margin** - Typically 92%+ (we're efficient)

**Verification History Table:**
- **Time** - When you submitted
- **Claim** - Your question (truncated)
- **Verdict** - Result (color-coded)
- **Confidence** - Certainty level with bar
- **Revenue** - Your payment ($0.05 or $0 if refunded)
- **Cost** - LLM processing cost
- **Profit** - What VerifAI earned
- **Duration** - Processing time

**Color Coding:**
- 🟢 Green = Verified
- 🔴 Red = Unverified
- 🟠 Orange = Inconclusive
- 🔵 Blue = Uncertain

### Analytics Page

Visit: https://verifai-production.up.railway.app/analytics

**Charts:**
1. **Verdict Distribution** (Pie Chart)
   - See how many Verified vs Unverified vs Inconclusive
   - Helps you understand claim quality

2. **Economics Breakdown** (Bar Chart)
   - Revenue vs Costs vs Profit
   - Full transparency into service economics

3. **Token Usage by Agent** (Horizontal Bar)
   - How much each AI agent "thinks"
   - Input tokens = reading, Output tokens = writing

**Agent Performance Table:**
- Shows which AI model is most expensive
- Tracks average tokens per agent
- Helps understand processing costs

---

## Best Practices

### Writing Good Claims

**✅ DO:**
- Be specific: "Mount Everest is 8,848 meters tall"
- Use exact dates: "World War II ended in 1945"
- State clearly: "Caffeine is a stimulant"
- Provide context: "As of 2024, the US population exceeds 330 million"

**❌ DON'T:**
- Be vague: "Is crypto good?"
- Ask opinions: "Who's the best president?"
- Use unclear pronouns: "Did he say that?"
- Mix multiple claims: "Bitcoin is from 2009 and Ethereum from 2015"

### When to Trust Results

**High confidence (80%+):**
- Well-documented historical facts
- Scientific consensus
- Publicly verifiable data
- Clear yes/no questions

**Medium confidence (50-80%):**
- Recent events (still developing)
- Nuanced claims (partially true)
- Statistical claims (depends on source)
- Controversial topics (conflicting sources)

**Low confidence (<50%):**
- Subjective matters
- Future predictions
- Poorly documented topics
- Contradictory sources (refunded!)

### Verifying Important Claims

For critical decisions:

1. **Check the sources** - Click through and read them yourself
2. **Look at confidence** - <80% means uncertainty
3. **Read both arguments** - Prover AND Debunker
4. **Consider context** - Is the claim oversimplified?
5. **Verify independently** - VerifAI is a tool, not gospel

---

## Troubleshooting

### "Payment Required" Error

**Cause:** You haven't paid yet or payment didn't process

**Fix:**
1. Check your wallet has USDC on Base Sepolia
2. Approve the payment transaction
3. Wait for confirmation (instant)
4. Retry the verification

### "Rate Limit Exceeded"

**Cause:** More than 60 requests per minute from your IP

**Fix:**
- Wait 60 seconds
- Reduce request frequency
- Contact us for higher limits

### "Service Unavailable"

**Cause:** VerifAI is down or restarting

**Fix:**
1. Check https://verifai-production.up.railway.app/health
2. Wait 1-2 minutes for restart
3. Check the dashboard for status
4. Report if down >5 minutes

### "Inconclusive Result"

**Not an error!** This means:
- Evidence was contradictory
- Sources disagreed
- Claim was too vague
- Topic is subjective

**What happens:**
- You get an automatic refund
- No charge for uncertain results
- Try rephrasing your question more specifically

### Dashboard Not Loading

**Common causes:**
- Browser cache (hard refresh: Ctrl+F5)
- Old cached 402 payment screen
- Network issues

**Fix:**
1. Clear browser cache
2. Try incognito/private mode
3. Check internet connection
4. Try different browser

### Sources Look Wrong

**Remember:**
- VerifAI searches the live web
- Sources can be biased
- Wikipedia is weighted 50% (trusted less)
- Always click through to verify

**If truly wrong:**
- Note the confidence score (probably low)
- Check if Debunker caught the issue
- Report persistent problems

---

## Advanced Tips

### Crafting Complex Queries

**Breaking down compound claims:**

❌ Bad: "Bitcoin was invented in 2009 and is better than gold"

✅ Good (separate verifications):
1. "Bitcoin was invented in 2009"
2. "Bitcoin's market cap exceeds $1 trillion" (factual aspect)

### Understanding Edge Cases

**Partially True Claims:**
- VerifAI will note this in Judge's reasoning
- Confidence usually 50-70%
- Read carefully to understand nuance

**Time-Sensitive Claims:**
- Add date context: "As of January 2026..."
- Predictions get lower confidence
- Verify recent results against current news

**Statistical Claims:**
- Depends heavily on source
- Check if sources agree on numbers
- Look for margin of error mentions

### Using VerifAI Ethically

**Good uses:**
- Fact-checking news articles
- Verifying historical claims
- Checking scientific statements
- Researching unfamiliar topics

**Inappropriate uses:**
- Spreading misinformation if it says "Unverified"
- Ignoring low confidence scores
- Using as sole source for critical decisions
- Expecting verification of opinions

---

## Getting More Help

### Documentation
- **Getting Started:** [GETTING_STARTED.md](GETTING_STARTED.md)
- **API Guide:** [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
- **FAQ:** See GETTING_STARTED.md FAQ section

### Live Monitoring
- **Dashboard:** https://verifai-production.up.railway.app/dashboard
- **Analytics:** https://verifai-production.up.railway.app/analytics
- **Health:** https://verifai-production.up.railway.app/health

### Technical Support
- **GitHub Issues:** https://github.com/courtneylee09/VerifAI
- **Service Status:** Check /health endpoint
- **Logs:** Available in analytics page

---

**Ready to verify?** Visit https://verifai-production.up.railway.app/verify?claim=Your+claim+here
