# VerifAI Performance & Economics Logger

Automatically tracks LLM token costs vs USDC revenue to calculate exact profit per verification request.

## 📊 What Gets Tracked

Every paid verification request logs:
- **Token Usage**: Input/output tokens for each agent (Prover, Debunker, Judge)
- **LLM Costs**: Real-time API pricing for DeepInfra, Anthropic, and Gemini models
- **USDC Revenue**: $0.05 per request via x402 payment
- **Net Profit**: Revenue minus LLM costs
- **Profit Margin**: Percentage profit per request
- **Performance**: Search count and execution time

## 💰 Current Pricing (Dec 2024)

### DeepInfra Models
| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| Llama 3.3 70B Turbo (Prover) | $0.59 | $0.79 |
| DeepSeek-V3 (Debunker) | $0.27 | $1.10 |

### Anthropic Models
| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| Claude 3.5 Haiku (Judge) | $1.00 | $5.00 |

### Google Gemini
| Model | Cost |
|-------|------|
| Gemini 2.0 Flash (Fallback) | **FREE** during preview |

### Revenue
- **Per Request**: $0.05 USDC (via x402 payment protocol)

## 🚀 Quick Start

### 1. View Performance Summary
```bash
python performance_log.py --summary
```

Output:
```
📊 Total Requests: 100

💰 ECONOMICS:
   Revenue (USDC):        $5.0000
   Costs (LLM tokens):    $0.4123
   ─────────────────────────────────
   Net Profit:            $4.5877
   Profit Margin:         91.75%

📈 PER REQUEST:
   Avg Profit:            $0.045877
```

### 2. View Recent Requests
```bash
python performance_log.py --recent 20
```

Shows last 20 verification requests with individual costs/profits.

### 3. Export to CSV
```bash
python performance_log.py --export
```

Creates `logs/performance_export.csv` for spreadsheet analysis.

### 4. View Everything
```bash
python performance_log.py
```

Shows recent requests + summary in one command.

## 📁 Log Storage

Performance data is stored in:
```
logs/performance.jsonl
```

Each line is a JSON object with complete request details:
```json
{
  "timestamp": "2025-12-27T05:30:00.000000",
  "claim": "Bitcoin was invented in 2009",
  "verdict": "Verified",
  "confidence_score": 0.95,
  "tokens": {
    "total_input": 4850,
    "total_output": 370,
    "prover": {"model": "meta-llama/Llama-3.3-70B-Instruct-Turbo", "input": 1200, "output": 150},
    "debunker": {"model": "deepseek-ai/DeepSeek-V3", "input": 1150, "output": 140},
    "judge": {"model": "claude-3-5-haiku-20241022", "input": 2500, "output": 80}
  },
  "costs": {
    "prover_cost": 0.000826,
    "debunker_cost": 0.000465,
    "judge_cost": 0.0029,
    "total_cost": 0.004191
  },
  "economics": {
    "revenue_usdc": 0.05,
    "total_cost_usd": 0.004191,
    "profit_usd": 0.045809,
    "profit_margin_pct": 91.62
  },
  "metadata": {
    "search_count": 10,
    "execution_time_sec": 8.5
  }
}
```

## 🔧 Programmatic Access

```python
from performance_log import PerformanceLogger

# Get aggregate statistics
summary = PerformanceLogger.get_summary()
print(f"Total profit: ${summary['total_profit_usd']:.4f}")
print(f"Profit margin: {summary['avg_margin_pct']:.2f}%")
print(f"Total requests: {summary['total_requests']}")

# Read all logs for custom analysis
logs = PerformanceLogger.read_logs()
for log in logs:
    cost = log['economics']['total_cost_usd']
    profit = log['economics']['profit_usd']
    print(f"{log['timestamp']}: ${profit:.6f} profit")

# Manual logging (usually automatic via service)
PerformanceLogger.log_request(
    claim="Test claim",
    verdict="Verified",
    confidence_score=0.95,
    prover_tokens={"model": "meta-llama/Llama-3.3-70B-Instruct-Turbo", "input": 1200, "output": 150},
    debunker_tokens={"model": "deepseek-ai/DeepSeek-V3", "input": 1150, "output": 140},
    judge_tokens={"model": "claude-3-5-haiku-20241022", "input": 2500, "output": 80},
    search_count=10,
    execution_time=8.5
)
```

## 🎯 Typical Economics

Based on average token usage:

| Component | Avg Tokens (in/out) | Avg Cost |
|-----------|---------------------|----------|
| Prover (Llama 3.3 70B) | 1,000 / 120 | $0.00071 |
| Debunker (DeepSeek-V3) | 1,000 / 120 | $0.00040 |
| Judge (Claude Haiku) | 2,200 / 75 | $0.00260 |
| **Total LLM Cost** | ~4,200 / 315 | **$0.00371** |
| **Revenue** | - | **$0.05000** |
| **Net Profit** | - | **$0.04629** |
| **Margin** | - | **92.6%** |

## 📈 Optimization Insights

The logger helps you:

1. **Track profitability per request** - Know exactly how much you earn
2. **Identify expensive requests** - Find claims that use more tokens
3. **Monitor model costs** - See which agent costs the most
4. **Optimize pricing** - Adjust $0.05 price based on actual costs
5. **Validate fallback usage** - Track when free Gemini is used vs paid models

## 🔄 Automatic Integration

Performance logging is **automatically enabled** in your verification service:

1. Every paid `/verify` request triggers logging
2. Token usage is tracked from each LLM API response
3. Costs are calculated using current API pricing
4. Data is appended to `logs/performance.jsonl`

No manual intervention required after deployment!

## 🧪 Testing

Test the logger with simulated data:
```bash
python test_performance_log.py
```

View demo and usage examples:
```bash
python demo_performance_log.py
```

## 📊 Sample Analysis Queries

### Find most profitable requests
```python
logs = PerformanceLogger.read_logs()
sorted_logs = sorted(logs, key=lambda x: x['economics']['profit_usd'], reverse=True)
print(f"Most profitable: {sorted_logs[0]['claim']} - ${sorted_logs[0]['economics']['profit_usd']:.6f}")
```

### Calculate daily profit
```python
from datetime import datetime
logs = PerformanceLogger.read_logs()
today = datetime.utcnow().date()
today_logs = [log for log in logs if datetime.fromisoformat(log['timestamp']).date() == today]
daily_profit = sum(log['economics']['profit_usd'] for log in today_logs)
print(f"Today's profit: ${daily_profit:.4f}")
```

### Find token-heavy claims
```python
logs = PerformanceLogger.read_logs()
for log in logs:
    total_tokens = log['tokens']['total_input'] + log['tokens']['total_output']
    if total_tokens > 6000:
        print(f"Heavy: {log['claim']} ({total_tokens:,} tokens, ${log['economics']['total_cost_usd']:.6f})")
```

## 📦 What's Next?

After deployment to Railway, you can:
- Monitor real request economics in production
- Set up alerts for low-margin requests
- Export monthly reports for accounting
- Optimize agent prompts to reduce token usage
- Adjust pricing if margins drop below target

---

**Built for VerifAI** - Track every cent of your AI verification service 💰
