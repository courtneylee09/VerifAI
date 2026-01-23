# 🚀 Base Mainnet Migration Guide

## Network Comparison

| Aspect | Base Sepolia (Testnet) | Base (Mainnet) |
|--------|----------------------|----------------|
| **Chain ID** | 84532 | 8453 |
| **USDC Contract** | 0x036CbD53842c5426634e7929541eC2318f3dCF7e | 0x833589fCD6eDb6E08f4c7C32D4f71b1566469c18 |
| **RPC URL** | https://sepolia.base.org | https://mainnet.base.org |
| **Real Money** | ❌ Test tokens | ✅ Real USDC |
| **User Base** | Small (developers) | Large (public) |
| **Cost** | Free (faucet) | Requires funding |
| **X402 Bazaar** | Unknown support | Full support (assumed) |

---

## ✅ Checklist for Mainnet Launch

### 1. Create Production Merchant Wallet

**Option A: High Security (Recommended for >$1000)**
```bash
# Create multisig wallet (requires 2-of-3 signatures)
# Use services like Safe (formerly Gnosis Safe) or Coinbase Custody
# Prevents single key compromise
```

**Option B: Standard (Simple setup)**
```bash
# Use MetaMask or Coinbase Wallet on Base mainnet
# Keep private key secure in Railway environment variables
# Consider hardware wallet for extra security
```

**Get the address:**
```bash
# MetaMask: Settings → Accounts → Copy address
# Format: 0x...
```

---

### 2. Fund Merchant Wallet with Real USDC

**Option A: Coinbase/Kraken (Easiest)**
1. Buy USDC on Coinbase/Kraken
2. Withdraw to Base mainnet
3. Send to your merchant wallet
4. **Start with $50-100** (~1000-2000 verifications)

**Option B: Bridge from Ethereum**
1. Get USDC on Ethereum mainnet
2. Bridge via Stargate/Portal/Across
3. Select Base as destination
4. Receive USDC in merchant wallet

**Option C: Swap on DEX**
1. Get any crypto on Base (ETH, Optimism, etc.)
2. Swap to USDC on Uniswap/Curve
3. Send to merchant wallet

**Verify funding:**
```bash
# Check balance on BaseScan
# Visit: https://basescan.org/address/YOUR_WALLET_ADDRESS
```

---

### 3. Update Configuration

#### Locally (for testing):
```bash
cd "c:\Users\Courtney Hamilton\verification-agent"

# Update settings manually
# Edit config/settings.py:
# X402_NETWORK = "base"  (change from "base-sepolia")
```

#### On Railway (production):
```bash
# Go to Railway dashboard → Environment
# Add new variable:
# X402_NETWORK = "base"
```

---

### 4. Update Smart Contract Configuration

The USDC contract address changes on mainnet. Check if your code needs updates:

```bash
# Search for hardcoded contract addresses
grep -r "036CbD53842c5426634e7929541eC2318f3dCF7e" .
# Should be empty - if found, update to mainnet address:
# 0x833589fCD6eDb6E08f4c7C32D4f71b1566469c18
```

---

### 5. Update Listing Metadata

Edit [x402_bazaar_listing.json](x402_bazaar_listing.json):

**Before (Testnet):**
```json
{
  "pricing": {
    "network": "base-sepolia"
  },
  "status": "beta",
  "testnet_only": true
}
```

**After (Mainnet):**
```json
{
  "pricing": {
    "network": "base",
    "amount": "0.05"  // Adjust price if needed (was 0.05 test USDC)
  },
  "status": "production",
  "testnet_only": false
}
```

**Pricing Decision:**
- **Sepolia:** 0.05 test USDC (arbitrary)
- **Mainnet Options:**
  - **0.01 USDC:** Cheap, high volume, low margins
  - **0.05 USDC:** Mid-range (keep same)
  - **0.10 USDC:** Premium, lower volume, higher margins
  - **0.25 USDC:** Very premium, niche users

**Recommendation:** Keep 0.05 USDC to start, adjust based on demand

---

### 6. Deploy & Test on Mainnet

**Step 1: Update code locally**
```bash
# Update config/settings.py with X402_NETWORK env var support
# Deploy to Railway:
git add .
git commit -m "Prepare mainnet migration: add X402_NETWORK env var"
git push origin main
```

**Step 2: Set Railway environment variable**
```
X402_NETWORK = "base"
```

**Step 3: Run real transaction test**
```bash
# Create test request with real payment
# Expected: 0.05 USDC deducted from merchant wallet
# Check BaseScan: https://basescan.org/tx/YOUR_TX_HASH
```

**Step 4: Verify merchant wallet debit**
```bash
# Before: 100 USDC
# After: 99.95 USDC (fee applied)
# ✅ Payment working!
```

---

### 7. Submit to X402 Bazaar

**Once mainnet is live:**
1. Update [x402_bazaar_listing.json](x402_bazaar_listing.json) with mainnet config
2. Submit to x402 bazaar marketplace
3. Set status: **Production** (remove beta tag)
4. Optionally: Advertise on x402 community channels

---

## ⚠️ Critical Security Checks

Before going mainnet, verify:

- ✅ Private key NOT in code (use Railway secrets)
- ✅ HTTPS only (Railway enforces this)
- ✅ Rate limiting active (prevent spam)
- ✅ Error messages don't leak sensitive data
- ✅ Payment validation working (test transaction)
- ✅ Logs don't contain wallet addresses or keys
- ✅ No test mode enabled in production
- ✅ SSL certificate valid (automatic on Railway)

---

## 💰 Cost Comparison

| Item | Testnet | Mainnet |
|------|---------|---------|
| **USDC per verification** | 0.05 (test) | 0.05 (real) |
| **Gas fee** | $0 | $0.001-0.01 |
| **Max daily revenue** | $0 (test) | $500+ (if 1000s users) |
| **Wallet balance risk** | None | High if low funded |
| **Refund liability** | None | Real money involved |

---

## 🎯 Recommended Timeline

**Phase 1: This Week**
- ✅ Finalize mainnet merchant wallet
- ✅ Fund with initial USDC ($50-100)
- ✅ Update code with network config

**Phase 2: Next Week**
- ✅ Deploy to mainnet (small test first)
- ✅ Run 5 real transactions ($0.25)
- ✅ Verify payment settlement
- ✅ Monitor for 24 hours

**Phase 3: Launch**
- ✅ Update x402 bazaar listing
- ✅ Announce production service
- ✅ Monitor daily for revenue/errors
- ✅ Top up wallet as needed

---

## 🔧 Mainnet Config Checklist

```
✅ X402_NETWORK = "base" (set in Railway environment)
✅ Merchant wallet = [YOUR_MAINNET_ADDRESS]
✅ Merchant wallet funded = $50+ USDC
✅ USDC contract = 0x833589fCD6eDb6E08f4c7C32D4f71b1566469c18
✅ RPC endpoint = https://mainnet.base.org
✅ x402_bazaar_listing.json updated to mainnet config
✅ Error handling robust (no crashes on payment failure)
✅ Monitoring active (/health, /metrics, /feedback)
✅ Daily wallet balance checks set up
✅ Support contact included in responses
```

---

## 🚨 Emergency Procedures

**If wallet runs out of funds:**
1. Deposits temporarily fail (users get 402 Payment Required)
2. Top up wallet on BaseScan
3. Resume accepting payments

**If payment system breaks:**
1. Check Railway logs for errors
2. Verify merchant wallet still exists
3. Test /health endpoint
4. Restart service if needed

**If you need to refund users:**
- Log refund transaction on BaseScan
- Include refund reason in logs
- Email affected users with proof

---

## 📊 Success Metrics (Mainnet)

**Week 1:**
- ✅ 0 errors
- ✅ Payment settlement working
- ✅ Wallet monitored daily

**Week 2-4:**
- ✅ 10+ paying users
- ✅ $5+ revenue collected
- ✅ <5% error rate
- ✅ >4.0⭐ average rating

**Month 2+:**
- ✅ 100+ cumulative users
- ✅ $50+ revenue
- ✅ >99% uptime
- ✅ Feature improvements based on feedback

---

## Next Steps

1. **Today:** Create/fund mainnet merchant wallet
2. **Tomorrow:** Update Railway environment variables
3. **This week:** Deploy to mainnet (test first)
4. **Next week:** Go live on x402 bazaar

**Ready to launch on mainnet? Let me know your merchant wallet address!**
