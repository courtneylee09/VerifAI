# Production Monitoring & Alerting Setup

## 🎯 Overview

Your VerifAI service now has **4 new endpoints** for monitoring, metrics, and user feedback:

1. **`/health`** - System health check (CPU, memory, disk, payment status)
2. **`/metrics`** - Performance metrics (requests, errors, economics)
3. **`/feedback`** - User feedback collection (POST endpoint)
4. **Enhanced error logging** - All existing endpoints log detailed metrics

---

## 📊 Available Endpoints

### 1. `/health` - Health Check

**Purpose:** Monitor service availability and system resources

**URL:** `https://verifai-production.up.railway.app/health`

**Response Example:**
```json
{
  "status": "healthy",
  "timestamp": 1737584765.123,
  "service": "VerifAI agent-x402",
  "version": "1.0.2",
  "payment": {
    "enabled": true,
    "network": "base-sepolia",
    "price": "0.05"
  },
  "system": {
    "cpu_percent": 12.5,
    "memory_percent": 45.3,
    "disk_percent": 38.7
  }
}
```

**Use Cases:**
- Uptime monitoring (UptimeRobot, Pingdom, StatusPage)
- Load balancer health checks
- Auto-scaling triggers (Railway auto-scaling)

---

### 2. `/metrics` - Performance Metrics

**Purpose:** Track request volume, error rates, and economics

**URL:** `https://verifai-production.up.railway.app/metrics`

**Response Example:**
```json
{
  "timestamp": 1737584765.123,
  "performance": {
    "total_requests": 1247,
    "requests_last_hour": 23,
    "error_rate_percent": 2.3,
    "avg_execution_time_seconds": 0.85
  },
  "economics": {
    "total_revenue_usd": 62.35,
    "total_cost_usd": 18.47,
    "total_profit_usd": 43.88,
    "profit_margin_percent": 70.4
  },
  "verdicts": {
    "true_count": 542,
    "false_count": 398,
    "inconclusive_count": 307
  }
}
```

**Use Cases:**
- Grafana/Prometheus dashboards
- Business analytics (revenue tracking)
- Performance optimization (identify slow requests)

---

### 3. `/feedback` - User Feedback Collection

**Purpose:** Collect user ratings and comments about verification quality

**URL:** `https://verifai-production.up.railway.app/feedback`  
**Method:** `POST`

**Request Body:**
```json
{
  "claim": "The James Webb Space Telescope discovered water on K2-18b",
  "rating": 5,
  "comment": "Excellent verification with strong sources!",
  "verdict_received": "True",
  "helpful": true
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Thank you for your feedback!"
}
```

**Stored in:** `logs/feedback.jsonl` (one JSON object per line)

**Use Cases:**
- Quality improvement (identify bad verdicts)
- Customer satisfaction tracking
- Feature prioritization

---

## 🔔 Setting Up Alerts

### Option 1: UptimeRobot (Free, Recommended)

**Setup:**
1. Go to [uptimerobot.com](https://uptimerobot.com)
2. Create free account (50 monitors free)
3. Add HTTP(s) monitor:
   - URL: `https://verifai-production.up.railway.app/health`
   - Interval: 5 minutes
   - Alert when: Status code != 200
   - Alert contacts: Your email

**What it monitors:**
- ✅ Service uptime
- ✅ Response time
- ✅ SSL certificate validity
- ✅ Downtime notifications via email/SMS

---

### Option 2: Railway Monitoring (Built-in)

**Railway Dashboard Already Shows:**
- CPU/Memory usage graphs
- Request count & latency
- Error logs in real-time
- Deployment history

**How to Access:**
1. Go to [railway.app](https://railway.app)
2. Navigate to your VerifAI project
3. Click "Metrics" tab
4. Set up alerts in Settings → Notifications

---

### Option 3: Custom Webhook Alerts

**Create a monitoring script:**

```python
# monitor.py - Run this every 5 minutes via cron/Railway scheduled job
import requests
import os

WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")  # Or Discord, Telegram, etc.

def check_health():
    try:
        resp = requests.get("https://verifai-production.up.railway.app/health", timeout=10)
        data = resp.json()
        
        # Alert if CPU > 80%
        if data["system"]["cpu_percent"] > 80:
            send_alert(f"🚨 High CPU: {data['system']['cpu_percent']}%")
        
        # Alert if memory > 90%
        if data["system"]["memory_percent"] > 90:
            send_alert(f"🚨 High Memory: {data['system']['memory_percent']}%")
        
        # Alert if payment disabled
        if not data["payment"]["enabled"]:
            send_alert("🚨 Payment middleware disabled!")
        
    except Exception as e:
        send_alert(f"🚨 Health check failed: {e}")

def send_alert(message):
    requests.post(WEBHOOK_URL, json={"text": message})

if __name__ == "__main__":
    check_health()
```

**Run via cron:**
```bash
*/5 * * * * cd /app && python monitor.py
```

---

## 📈 Integrating with Grafana

**If you want fancy dashboards:**

1. **Install Prometheus exporter** (convert /metrics to Prometheus format):
```python
# Add to requirements.txt:
# prometheus-client>=0.19.0

from prometheus_client import Counter, Histogram, Gauge, generate_latest

requests_total = Counter('verifai_requests_total', 'Total requests')
request_duration = Histogram('verifai_request_duration_seconds', 'Request duration')
error_rate = Gauge('verifai_error_rate_percent', 'Error rate percentage')

@app.get("/metrics/prometheus")
async def prometheus_metrics():
    # Update gauges from PerformanceLogger
    metrics = PerformanceLogger.get_summary()
    error_rate.set(metrics.get("error_rate_percent", 0))
    
    return Response(content=generate_latest(), media_type="text/plain")
```

2. **Configure Grafana to scrape:**
```yaml
scrape_configs:
  - job_name: 'verifai'
    static_configs:
      - targets: ['verifai-production.up.railway.app']
    metrics_path: '/metrics/prometheus'
    scheme: 'https'
```

3. **Create Grafana dashboard with:**
   - Request rate (requests/sec)
   - Error rate (%)
   - P50/P95/P99 latency
   - Revenue vs Cost (economics)
   - Verdict distribution (pie chart)

---

## 💰 Wallet Balance Monitoring

**Critical:** Monitor merchant wallet balance to avoid running out of funds

### Option A: Manual Check (Simple)

**Check balance periodically:**
```bash
# Install cast (Foundry)
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Check USDC balance
cast call 0x036CbD53842c5426634e7929541eC2318f3dCF7e \
  "balanceOf(address)(uint256)" \
  0x3615af0cE7c8e525B9a9C6cE281e195442596559 \
  --rpc-url https://sepolia.base.org
```

### Option B: Automated Alerts (Recommended)

**Create wallet_monitor.py:**
```python
import requests
import os

RPC_URL = "https://sepolia.base.org"
USDC_CONTRACT = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
MERCHANT_WALLET = "0x3615af0cE7c8e525B9a9C6cE281e195442596559"
ALERT_THRESHOLD = 5.0  # Alert if balance < 5 USDC

def check_wallet_balance():
    # Call USDC balanceOf via RPC
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_call",
        "params": [{
            "to": USDC_CONTRACT,
            "data": f"0x70a08231000000000000000000000000{MERCHANT_WALLET[2:]}"
        }, "latest"],
        "id": 1
    }
    
    resp = requests.post(RPC_URL, json=payload)
    balance_hex = resp.json()["result"]
    balance_wei = int(balance_hex, 16)
    balance_usdc = balance_wei / 1e6  # USDC has 6 decimals
    
    print(f"Wallet balance: {balance_usdc:.2f} USDC")
    
    if balance_usdc < ALERT_THRESHOLD:
        send_alert(f"🚨 Low wallet balance: {balance_usdc:.2f} USDC")

def send_alert(message):
    # Send to Slack/Discord/Email
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    requests.post(webhook_url, json={"text": message})

if __name__ == "__main__":
    check_wallet_balance()
```

**Run daily:**
```bash
0 9 * * * python wallet_monitor.py  # Check balance every morning
```

---

## 🎯 Recommended Alert Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| **CPU Usage** | >70% | >90% | Scale up Railway instance |
| **Memory Usage** | >80% | >95% | Investigate memory leak |
| **Error Rate** | >5% | >10% | Check logs, rollback if needed |
| **Response Time** | >2s | >5s | Optimize slow endpoints |
| **Wallet Balance** | <10 USDC | <5 USDC | Deposit more USDC |
| **Request Failures** | >10/hour | >50/hour | Investigate API issues |

---

## 📋 Daily Monitoring Checklist

**Every Morning (5 minutes):**
1. ✅ Check Railway dashboard for errors
2. ✅ Review `/metrics` endpoint (total requests, profit margin)
3. ✅ Read `logs/feedback.jsonl` for user comments
4. ✅ Verify wallet balance >10 USDC
5. ✅ Scan logs for unusual patterns

**Weekly (30 minutes):**
1. ✅ Analyze verdict distribution (True/False/Inconclusive ratios)
2. ✅ Review cost trends (is profit margin stable?)
3. ✅ Check for repeated error patterns
4. ✅ Update documentation based on user feedback
5. ✅ Plan optimizations if needed

**Monthly (2 hours):**
1. ✅ Export performance logs to CSV for analysis
2. ✅ Calculate customer acquisition cost (if marketing)
3. ✅ Review stress test results (re-run if traffic increased)
4. ✅ Update x402 bazaar listing with new features
5. ✅ Backup logs and wallet keys

---

## 🚀 Next Steps

### Install psutil Dependency (Required for /health)

```bash
cd "c:\Users\Courtney Hamilton\verification-agent"
.\venv\Scripts\activate.ps1
pip install psutil
```

### Test New Endpoints Locally

```bash
# Start server
python run.py

# In another terminal:
curl http://localhost:8001/health
curl http://localhost:8001/metrics
curl -X POST http://localhost:8001/feedback -H "Content-Type: application/json" -d '{"rating": 5, "comment": "Test"}'
```

### Deploy to Railway

```bash
git add .
git commit -m "Add monitoring endpoints: /health, /metrics, /feedback"
git push railway main
```

### Verify Production Endpoints

```bash
curl https://verifai-production.up.railway.app/health
curl https://verifai-production.up.railway.app/metrics
```

---

## 📊 Sample Grafana Dashboard Config

If you set up Grafana, here's a starter dashboard JSON:

```json
{
  "dashboard": {
    "title": "VerifAI Production Monitoring",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [{"expr": "rate(verifai_requests_total[5m])"}],
        "type": "graph"
      },
      {
        "title": "Error Rate",
        "targets": [{"expr": "verifai_error_rate_percent"}],
        "type": "stat",
        "thresholds": {"mode": "absolute", "steps": [
          {"color": "green", "value": 0},
          {"color": "yellow", "value": 5},
          {"color": "red", "value": 10}
        ]}
      },
      {
        "title": "Profit Margin",
        "targets": [{"expr": "verifai_profit_margin_percent"}],
        "type": "gauge"
      }
    ]
  }
}
```

---

## ✅ Summary

**You now have:**
1. ✅ `/health` - System health monitoring
2. ✅ `/metrics` - Performance & economics tracking
3. ✅ `/feedback` - User feedback collection
4. ✅ Enhanced logging (already built-in)

**What's NOT included (optional add-ons):**
- ❌ PagerDuty integration (requires paid service)
- ❌ Automated wallet top-up (would need smart contract)
- ❌ Real-time alerting to phone (use UptimeRobot for this)
- ❌ Advanced anomaly detection (ML-based)

**Recommendation:** Start with UptimeRobot + Railway dashboard + daily manual checks. Upgrade to Grafana/Prometheus if you hit >100 DAU.
