# Stress Testing Guide - VerifAI Launch Readiness

**Last Updated:** January 22, 2026  
**Status:** Ready for testing

---

## Quick Start

### Run Full Stress Test Suite (10-15 minutes)
```powershell
python run_all_stress_tests.py
```

### Run Quick Tests Only (3-5 minutes)
```powershell
python run_all_stress_tests.py --mode=quick
```

---

## Individual Tests

### 1. Concurrent Load Test - Small
Tests 5 workers with 20 claims each (100 total requests)
```powershell
python concurrent_stress_test.py --workers=5 --claims=20
```

### 2. Concurrent Load Test - Large
Tests 10 workers with 15 claims each (150 total requests)
```powershell
python concurrent_stress_test.py --workers=10 --claims=15
```

### 3. Payment Validation Test - Small
Tests 20 concurrent payment validations
```powershell
python payment_load_test.py --concurrent=20 --duration=60
```

### 4. Payment Validation Test - Large
Tests 50 concurrent payment validations
```powershell
python payment_load_test.py --concurrent=50 --duration=60
```

---

## Expected Results (Pass Criteria)

### Concurrent Load Test
| Metric | Target | Critical |
|--------|--------|----------|
| P50 Latency | < 15s | < 25s |
| P95 Latency | < 25s | < 30s |
| P99 Latency | < 30s | < 35s |
| Success Rate | >= 95% | >= 85% |

**Interpretation:**
- ✅ All targets met → **LAUNCH READY**
- ⚠️ Some critical met → **Monitor, launch with caution**
- ❌ Critical not met → **Fix before launch**

### Payment Validation Test
| Metric | Target | Critical |
|--------|--------|----------|
| P50 Latency | < 100ms | < 500ms |
| P95 Latency | < 500ms | < 2000ms |
| Success Rate | >= 95% | >= 85% |

**Interpretation:**
- ✅ All targets met → **Payment layer solid**
- ⚠️ Some metrics high → **Investigate middleware bottleneck**
- ❌ Critical not met → **Payment layer needs work**

---

## Interpreting Results

### Scenario 1: All Tests Pass ✅
```
✅ Concurrent Load (5 workers): P50=12s, P95=18s, P99=22s, Success=98%
✅ Payment Validation (50 concurrent): P50=45ms, P95=200ms, Success=99%
```
**Decision:** Launch to x402 bazaar

**Next Steps:**
1. Deploy to production
2. Add monitoring/alerting
3. Start light marketing
4. Monitor real user traffic

---

### Scenario 2: Latency High, Success OK ⚠️
```
⚠️ P95=28s, P99=35s (at edge of limits)
✅ Success rate 96%
```
**Decision:** Launch with caution

**Concerns:**
- Users at timeout edge may experience failures in production
- Peak traffic could push into failures

**Mitigations:**
1. Set up real-time latency monitoring
2. Implement request queuing if P95 stays >25s
3. Have rollback plan ready
4. Limit initial bazaar audience (50 users max)

---

### Scenario 3: Failures or Timeouts ❌
```
❌ Success rate 87% (fails >5% of requests)
❌ Timeouts: 3-5% of requests
```
**Decision:** DO NOT LAUNCH

**Root Causes to Investigate:**
1. **Payment middleware bottleneck** → Run payment_load_test.py
2. **LLM API rate limits** → Check DeepInfra/Claude quotas
3. **Exa search timeout** → Search takes >3s consistently
4. **Database/logging slowdown** → Check Railway logs

**Fixes:**
- Add request queuing (async queue)
- Implement timeout handling (return cached response)
- Reduce parallel agent calls if needed
- Scale Railway instances

---

## What Each Test Measures

### Concurrent Load Test (`concurrent_stress_test.py`)
**What it tests:**
- End-to-end verification flow under simultaneous load
- How many users can be served concurrently
- Payment header validation at scale
- Agent debate system parallelization

**What it measures:**
- Request latency (end-to-end)
- Success/failure rate
- Timeout distribution
- Payment validation speed

**Bottleneck indicators:**
- P95/P99 high but P50 low → Peak traffic issue
- P50 high → Systematic slowness
- Timeouts increasing → Server resource exhaustion

---

### Payment Validation Test (`payment_load_test.py`)
**What it tests:**
- x402 payment middleware speed
- EIP-712 signature validation at scale
- USDC contract interaction (simulated)
- Concurrent payment header parsing

**What it measures:**
- Payment validation latency
- Throughput (validations/sec)
- Middleware overhead

**Bottleneck indicators:**
- P95 > 500ms → Middleware slow
- High error rate → Signature validation failing
- Low throughput → Serialization issues

---

## Optimization Tips if Tests Fail

### If P50/P95 latency high:
1. **Check Exa timeout** (typically 2-3s)
   ```python
   # In verification.py
   EXA_SEARCH_TIMEOUT_SECONDS = 2  # Reduce from 3 if needed
   ```

2. **Check agent timeout** (typically 10-15s total)
   ```python
   # In verification.py
   DEBATE_TIMEOUT_SECONDS = 10  # Reduce from 15 if needed
   ```

3. **Add caching** for common claims
   ```python
   # In verification.py
   # Cache verdicts for identical claims (24 hour TTL)
   ```

### If payment validation slow:
1. **Profile signature validation** - might need parallel processing
2. **Check Railway CPU/memory** - might need larger instance
3. **Enable Redis caching** for token validation

### If success rate low:
1. **Check error logs** - most common failures
2. **Monitor API quotas** - DeepInfra/Claude rate limits
3. **Test fallback system** - Gemini fallback should trigger

---

## Production Monitoring Setup

After tests pass, set up monitoring:

### Metrics to Track
```
✅ Request latency (P50, P95, P99)
✅ Success rate (%)
✅ Error rate by type
✅ Payment validation time
✅ API costs per request
✅ Revenue per request
```

### Alert Thresholds
```
🚨 P99 > 40 seconds
🚨 Success rate < 90%
🚨 Payment validation > 2 seconds
🚨 Error rate > 10%
```

### Dashboard
- Real-time request latency
- Success/failure breakdown
- Cost analysis per claim type
- Revenue tracking

---

## Rollback Plan

If launch goes wrong:

### Immediate Actions
1. Scale down Railway instance (save costs)
2. Set all endpoints to return 429 (Service Unavailable)
3. Or redirect to maintenance page

### Investigation
1. Check logs for error patterns
2. Identify which component failing (Exa? DeepInfra? Claude?)
3. Fix configuration/limits

### Restart
1. Deploy fix
2. Test with small concurrent load first
3. Gradually re-enable traffic

---

## Timeline

**Phase 1 (Today - 2-4 hours):**
- Run concurrent_stress_test.py (5 workers)
- Run payment_load_test.py (20 concurrent)
- Review results

**Phase 2 (If Phase 1 passes - 1-2 hours):**
- Run concurrent_stress_test.py (10 workers)
- Run payment_load_test.py (50 concurrent)
- Final validation

**Phase 3 (If Phase 2 passes - Same day):**
- Deploy to production
- Add monitoring
- Launch on x402 bazaar (limited)

**Phase 4 (1 week - Monitor):**
- Real user traffic
- Collect actual latency data
- Adjust based on real load

---

## Questions Before Launch

✅ Can system handle 10 concurrent users?  
✅ Can payment validation keep up at scale?  
✅ Do timeouts stay under 30 seconds?  
✅ Do failures stay under 5%?  
✅ Are error logs clear/actionable?  
✅ Can you see costs per request?  

If all yes → **LAUNCH**  
If any no → **INVESTIGATE**

---

## Support & Debugging

### View test results
```powershell
# List all test results
ls logs/concurrent_load_test_*.json
ls logs/payment_load_test_*.json
ls logs/stress_test_suite_*.json

# Pretty print latest test
python -m json.tool logs/concurrent_load_test_*.json | tail -50
```

### Re-run specific test with debugging
```powershell
python concurrent_stress_test.py --workers=5 --claims=10  # Smaller test
python payment_load_test.py --concurrent=10 --duration=30  # Quick test
```

### Check production logs
```powershell
# Railway logs
railway logs

# Or via web dashboard
# https://railway.app → Select VerifAI project
```

---

**Good luck! 🚀**
