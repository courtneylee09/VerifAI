# 🚀 Quick Start - Stress Testing VerifAI

**TL;DR:** Run these commands to test if you're ready to launch

---

## 30-Minute Launch Readiness Test

### Step 1: Quick Baseline (5 minutes)
```powershell
cd "c:\Users\Courtney Hamilton\verification-agent"
python concurrent_stress_test.py --workers=5 --claims=20
```

**What to expect:**
- See 100 requests run concurrently
- Should complete in ~5-10 minutes
- Look for: P50 latency around 12-15 seconds

**Pass criteria:**
```
✅ P50 < 15s
✅ P95 < 25s
✅ Success rate >= 95%
```

### Step 2: Payment Test (2 minutes)
```powershell
python payment_load_test.py --concurrent=20 --duration=60
```

**What to expect:**
- 20 concurrent payment validations
- Should take ~1-2 minutes
- Look for: P50 latency around 50-100ms

**Pass criteria:**
```
✅ P50 < 100ms
✅ P95 < 500ms
✅ Success rate >= 95%
```

### Step 3: Full Validation (10 minutes)
If both above passed:
```powershell
python run_all_stress_tests.py --mode=full
```

**What this does:**
- Runs 4 stress tests in sequence
- Takes ~15 minutes total
- Generates comprehensive JSON report
- Tells you PASS/FAIL for launch

---

## Reading the Results

### Green Light ✅
```
✅ All tests passed
✅ P50 < 15 seconds
✅ P95 < 25 seconds
✅ Success rate >= 95%
✅ Payment validation fast

→ READY TO LAUNCH
```

### Yellow Light ⚠️
```
⚠️ Tests passed but some metrics high
⚠️ P95 = 27s (target 25s)
⚠️ Success rate = 96% (target 95%+)

→ Can launch but monitor closely
→ Have rollback plan ready
```

### Red Light ❌
```
❌ Any test failed
❌ Success rate < 90%
❌ P99 > 40 seconds
❌ Timeouts occurring

→ DO NOT LAUNCH
→ Investigate failure
→ Fix and re-test
```

---

## If Tests Pass: Next Steps (Today)

### 1. Create x402 Bazaar Listing
```
Name: VerifAI
Price: 0.05 USDC per request
Network: Base Sepolia
Status: Beta (limited to 100 users)
URL: https://verifai-production.up.railway.app/verify
```

### 2. Set Up Monitoring
- Real-time latency dashboard
- Alert if P99 > 40 seconds
- Alert if success rate drops below 90%

### 3. Monitor First 24 Hours
- Check every hour for errors
- Track actual costs vs. projected
- Look for any unusual patterns

---

## If Tests Fail: Debug Steps

### Step 1: Identify the Problem
```powershell
# Run just the failing test again
python concurrent_stress_test.py --workers=5 --claims=10  # Smaller test

# Check if it's payment-specific
python payment_load_test.py --concurrent=10 --duration=30  # Smaller test
```

### Step 2: Check Logs
```powershell
# View last 50 error logs
Get-Content logs/test_error.txt -Tail 50

# Check production logs
railway logs  # If you have railway CLI installed
```

### Step 3: Common Fixes
- **If latency high:** Reduce claim complexity or add caching
- **If payment slow:** Check EIP-712 signature generation
- **If timeout:** Reduce concurrent workers, increase timeout
- **If failures:** Check API rate limits (Exa, DeepInfra, Claude)

### Step 4: Re-Test
```powershell
# Fix the issue, then test again
python concurrent_stress_test.py --workers=5 --claims=20
```

---

## Files You Can Now Use

| File | Purpose | How to Use |
|------|---------|-----------|
| `concurrent_stress_test.py` | Load test | `python concurrent_stress_test.py --workers=5` |
| `payment_load_test.py` | Payment test | `python payment_load_test.py --concurrent=20` |
| `run_all_stress_tests.py` | Full suite | `python run_all_stress_tests.py --mode=full` |
| `STRESS_TESTING_GUIDE.md` | Full guide | Read for detailed info |
| `LAUNCH_READINESS_CHECKLIST.md` | Checklist | Reference before launch |

---

## Decision Tree

```
START
  ↓
Run: python concurrent_stress_test.py --workers=5 --claims=20
  ↓
  ├─ FAILS? 
  │   ├─ Investigate (check logs, API limits)
  │   ├─ Fix issue
  │   └─ Re-test
  │
  └─ PASSES?
      ↓
      Run: python payment_load_test.py --concurrent=20 --duration=60
      ↓
      ├─ FAILS?
      │   ├─ Check payment middleware
      │   ├─ Investigate EIP-712 validation
      │   └─ Re-test
      │
      └─ PASSES?
          ↓
          Run: python run_all_stress_tests.py --mode=full
          ↓
          ├─ ANY FAIL?
          │   ├─ Investigate that specific test
          │   └─ Re-test
          │
          └─ ALL PASS?
              ↓
              ✅ LAUNCH TO x402 BAZAAR
              ↓
              Monitor real traffic for 24 hours
```

---

## Pro Tips

### 1. Run tests at consistent time
- Reduces noise from Railway auto-scaling
- Easier to compare results over time

### 2. Check Railway dashboard before testing
- Make sure service is healthy
- No recent error spikes
- CPU/memory usage reasonable

### 3. Start small, scale up
- Test 5 workers first
- Then 10 workers
- Then 20+ if comfortable

### 4. Save results
```powershell
# Results auto-saved to:
ls logs/concurrent_load_test_*.json
ls logs/payment_load_test_*.json

# Compare runs:
Get-Content logs/concurrent_load_test_20260122_120000.json | ConvertFrom-Json
```

### 5. Document your findings
```powershell
# After running tests, save a note:
"[2026-01-22] Testing complete: P50=12s, P95=18s, Success=98%"
```

---

## You're Ready! 

Everything is set up. The test files are:
- ✅ Syntactically valid
- ✅ Ready to run
- ✅ Will give you clear pass/fail
- ✅ Should complete in 30 minutes

### Action: Run this now
```powershell
python concurrent_stress_test.py --workers=5 --claims=20
```

### Expected time: 5-10 minutes
### Expected outcome: Clear metrics showing if you can launch

---

## Questions?

| Question | Answer |
|----------|--------|
| **Where are results saved?** | `logs/concurrent_load_test_*.json` |
| **How do I see results?** | Check terminal output OR `python -m json.tool logs/*.json` |
| **Can I run tests multiple times?** | Yes, unlimited - results timestamp automatically |
| **What if I get errors?** | Read error message, check STRESS_TESTING_GUIDE.md |
| **Should I test multiple times?** | Yes - run 2-3 times to average out noise |
| **How long until launch?** | If all tests pass: Same day. If failures: 1-2 days to fix |

---

**Let's go! 🚀**
