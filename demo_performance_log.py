"""
Demo: VerifAI Performance Logger Usage

This script shows how to view your profit/cost analytics.
"""

print("""
╔══════════════════════════════════════════════════════════════════════════╗
║              VerifAI Performance & Economics Logger                      ║
╚══════════════════════════════════════════════════════════════════════════╝

Your verification service automatically tracks:
  • Token usage per agent (Prover, Debunker, Judge)
  • LLM API costs (DeepInfra, Anthropic, Gemini)
  • USDC revenue earned ($0.05 per request)
  • Net profit and profit margin per request

USAGE EXAMPLES:
───────────────────────────────────────────────────────────────────────────

1. View recent requests and summary:
   py performance_log.py

2. Show only profit summary:
   py performance_log.py --summary

3. Show last 20 requests:
   py performance_log.py --recent 20

4. Export to CSV for spreadsheet analysis:
   py performance_log.py --export

───────────────────────────────────────────────────────────────────────────
SAMPLE OUTPUT:

📊 Total Requests: 100

💰 ECONOMICS:
   Revenue (USDC):        $5.0000
   Costs (LLM tokens):    $0.1234
   ─────────────────────────────────
   Net Profit:            $4.8766
   Profit Margin:         97.53%

📈 PER REQUEST:
   Avg Profit:            $0.048766

🔢 TOKEN USAGE:
   Total Input:           245,123
   Total Output:          12,456
   Avg per request:       2,451 in / 125 out

───────────────────────────────────────────────────────────────────────────

After deploying your updates to Railway, the performance log will
automatically populate with each paid verification request.

The log file is stored at: logs/performance.jsonl
""")

# Quick example of programmatic access
print("\nPROGRAMMATIC ACCESS EXAMPLE:")
print("─" * 75)
print("""
from performance_log import PerformanceLogger

# Get summary stats
summary = PerformanceLogger.get_summary()
print(f"Total profit: ${summary['total_profit_usd']:.4f}")
print(f"Profit margin: {summary['avg_margin_pct']:.2f}%")

# Read all logs for custom analysis
logs = PerformanceLogger.read_logs()
for log in logs:
    print(f"{log['timestamp']}: {log['economics']['profit_usd']}")
""")
