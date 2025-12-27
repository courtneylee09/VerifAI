"""
VerifAI Performance & Economics Logger

Tracks token usage, LLM costs, USDC revenue, and profit per verification request.

Usage:
    python performance_log.py                    # View all logs
    python performance_log.py --summary          # Show profit summary
    python performance_log.py --export           # Export to CSV
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# ============================================================================
# Pricing Configuration (as of December 2024)
# ============================================================================

# DeepInfra pricing per 1M tokens
DEEPINFRA_PRICES = {
    "meta-llama/Llama-3.3-70B-Instruct-Turbo": {
        "input": 0.59,   # per 1M input tokens
        "output": 0.79   # per 1M output tokens
    },
    "deepseek-ai/DeepSeek-V3": {
        "input": 0.27,
        "output": 1.10
    }
}

# Anthropic pricing per 1M tokens
ANTHROPIC_PRICES = {
    "claude-3-5-haiku-20241022": {
        "input": 1.00,
        "output": 5.00
    }
}

# Google Gemini pricing per 1M tokens
GEMINI_PRICES = {
    "gemini-2.0-flash-exp": {
        "input": 0.00,   # Free during preview
        "output": 0.00
    }
}

# Revenue per request
USDC_REVENUE_PER_REQUEST = 0.05  # $0.05 USDC

# ============================================================================
# Performance Log Storage
# ============================================================================

LOG_DIR = Path("logs")
PERFORMANCE_LOG_FILE = LOG_DIR / "performance.jsonl"

LOG_DIR.mkdir(exist_ok=True)


class PerformanceLogger:
    """Track and analyze verification request economics."""
    
    @staticmethod
    def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for a model call."""
        # Check DeepInfra models
        if model in DEEPINFRA_PRICES:
            pricing = DEEPINFRA_PRICES[model]
            input_cost = (input_tokens / 1_000_000) * pricing["input"]
            output_cost = (output_tokens / 1_000_000) * pricing["output"]
            return input_cost + output_cost
        
        # Check Anthropic models
        if model in ANTHROPIC_PRICES:
            pricing = ANTHROPIC_PRICES[model]
            input_cost = (input_tokens / 1_000_000) * pricing["input"]
            output_cost = (output_tokens / 1_000_000) * pricing["output"]
            return input_cost + output_cost
        
        # Check Gemini models
        if model in GEMINI_PRICES:
            pricing = GEMINI_PRICES[model]
            input_cost = (input_tokens / 1_000_000) * pricing["input"]
            output_cost = (output_tokens / 1_000_000) * pricing["output"]
            return input_cost + output_cost
        
        # Unknown model - return 0 and log warning
        print(f"Warning: Unknown model pricing for {model}")
        return 0.0
    
    @staticmethod
    def log_request(
        claim: str,
        verdict: str,
        confidence_score: float,
        prover_tokens: Optional[Dict[str, int]] = None,
        debunker_tokens: Optional[Dict[str, int]] = None,
        judge_tokens: Optional[Dict[str, int]] = None,
        search_count: int = 0,
        execution_time: float = 0.0
    ):
        """Log a verification request with costs and revenue."""
        
        # Calculate individual costs
        costs = {
            "prover": 0.0,
            "debunker": 0.0,
            "judge": 0.0
        }
        
        total_tokens = {
            "input": 0,
            "output": 0
        }
        
        if prover_tokens:
            costs["prover"] = PerformanceLogger.calculate_cost(
                prover_tokens.get("model", "meta-llama/Llama-3.3-70B-Instruct-Turbo"),
                prover_tokens.get("input", 0),
                prover_tokens.get("output", 0)
            )
            total_tokens["input"] += prover_tokens.get("input", 0)
            total_tokens["output"] += prover_tokens.get("output", 0)
        
        if debunker_tokens:
            costs["debunker"] = PerformanceLogger.calculate_cost(
                debunker_tokens.get("model", "deepseek-ai/DeepSeek-V3"),
                debunker_tokens.get("input", 0),
                debunker_tokens.get("output", 0)
            )
            total_tokens["input"] += debunker_tokens.get("input", 0)
            total_tokens["output"] += debunker_tokens.get("output", 0)
        
        if judge_tokens:
            costs["judge"] = PerformanceLogger.calculate_cost(
                judge_tokens.get("model", "claude-3-5-haiku-20241022"),
                judge_tokens.get("input", 0),
                judge_tokens.get("output", 0)
            )
            total_tokens["input"] += judge_tokens.get("input", 0)
            total_tokens["output"] += judge_tokens.get("output", 0)
        
        total_cost = sum(costs.values())
        revenue = USDC_REVENUE_PER_REQUEST
        profit = revenue - total_cost
        margin = (profit / revenue * 100) if revenue > 0 else 0
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "claim": claim[:100],  # Truncate for readability
            "verdict": verdict,
            "confidence_score": confidence_score,
            "tokens": {
                "total_input": total_tokens["input"],
                "total_output": total_tokens["output"],
                "prover": prover_tokens,
                "debunker": debunker_tokens,
                "judge": judge_tokens
            },
            "costs": {
                "prover_cost": round(costs["prover"], 6),
                "debunker_cost": round(costs["debunker"], 6),
                "judge_cost": round(costs["judge"], 6),
                "total_cost": round(total_cost, 6)
            },
            "economics": {
                "revenue_usdc": revenue,
                "total_cost_usd": round(total_cost, 6),
                "profit_usd": round(profit, 6),
                "profit_margin_pct": round(margin, 2)
            },
            "metadata": {
                "search_count": search_count,
                "execution_time_sec": round(execution_time, 2)
            }
        }
        
        # Append to log file
        with open(PERFORMANCE_LOG_FILE, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        
        return log_entry
    
    @staticmethod
    def read_logs() -> List[Dict]:
        """Read all performance logs."""
        if not PERFORMANCE_LOG_FILE.exists():
            return []
        
        logs = []
        with open(PERFORMANCE_LOG_FILE, "r") as f:
            for line in f:
                if line.strip():
                    logs.append(json.loads(line))
        return logs
    
    @staticmethod
    def get_summary() -> Dict:
        """Calculate aggregate statistics."""
        logs = PerformanceLogger.read_logs()
        
        if not logs:
            return {
                "total_requests": 0,
                "total_revenue": 0.0,
                "total_cost": 0.0,
                "total_profit": 0.0,
                "avg_profit_per_request": 0.0,
                "avg_margin_pct": 0.0
            }
        
        total_revenue = sum(log["economics"]["revenue_usdc"] for log in logs)
        total_cost = sum(log["economics"]["total_cost_usd"] for log in logs)
        total_profit = total_revenue - total_cost
        
        avg_profit = total_profit / len(logs)
        avg_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        total_tokens_input = sum(log["tokens"]["total_input"] for log in logs)
        total_tokens_output = sum(log["tokens"]["total_output"] for log in logs)
        
        return {
            "total_requests": len(logs),
            "total_revenue_usd": round(total_revenue, 4),
            "total_cost_usd": round(total_cost, 4),
            "total_profit_usd": round(total_profit, 4),
            "avg_profit_per_request": round(avg_profit, 6),
            "avg_margin_pct": round(avg_margin, 2),
            "total_tokens": {
                "input": total_tokens_input,
                "output": total_tokens_output,
                "total": total_tokens_input + total_tokens_output
            },
            "avg_tokens_per_request": {
                "input": round(total_tokens_input / len(logs)),
                "output": round(total_tokens_output / len(logs))
            }
        }
    
    @staticmethod
    def print_summary():
        """Print a formatted summary."""
        summary = PerformanceLogger.get_summary()
        
        print("\n" + "="*70)
        print("VerifAI PERFORMANCE SUMMARY")
        print("="*70)
        print(f"\n📊 Total Requests: {summary['total_requests']}")
        print(f"\n💰 ECONOMICS:")
        print(f"   Revenue (USDC):        ${summary['total_revenue_usd']:.4f}")
        print(f"   Costs (LLM tokens):    ${summary['total_cost_usd']:.4f}")
        print(f"   ─────────────────────────────────")
        print(f"   Net Profit:            ${summary['total_profit_usd']:.4f}")
        print(f"   Profit Margin:         {summary['avg_margin_pct']:.2f}%")
        print(f"\n📈 PER REQUEST:")
        print(f"   Avg Profit:            ${summary['avg_profit_per_request']:.6f}")
        print(f"\n🔢 TOKEN USAGE:")
        print(f"   Total Input:           {summary['total_tokens']['input']:,}")
        print(f"   Total Output:          {summary['total_tokens']['output']:,}")
        print(f"   Avg per request:       {summary['avg_tokens_per_request']['input']:,} in / {summary['avg_tokens_per_request']['output']:,} out")
        print("\n" + "="*70 + "\n")
    
    @staticmethod
    def print_recent_logs(n: int = 10):
        """Print the most recent N logs."""
        logs = PerformanceLogger.read_logs()
        recent = logs[-n:] if len(logs) > n else logs
        
        print(f"\n{'='*100}")
        print(f"RECENT VERIFICATION REQUESTS (last {len(recent)})")
        print("="*100)
        
        for i, log in enumerate(reversed(recent), 1):
            timestamp = datetime.fromisoformat(log["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            claim = log["claim"][:60] + "..." if len(log["claim"]) > 60 else log["claim"]
            verdict = log["verdict"]
            confidence = log["confidence_score"]
            cost = log["economics"]["total_cost_usd"]
            profit = log["economics"]["profit_usd"]
            margin = log["economics"]["profit_margin_pct"]
            
            print(f"\n#{len(logs) - i + 1} | {timestamp}")
            print(f"   Claim: \"{claim}\"")
            print(f"   Verdict: {verdict} (confidence: {confidence:.2f})")
            print(f"   Cost: ${cost:.6f} | Profit: ${profit:.6f} | Margin: {margin:.1f}%")
        
        print("\n" + "="*100 + "\n")
    
    @staticmethod
    def export_to_csv(filename: str = "performance_export.csv"):
        """Export logs to CSV format."""
        logs = PerformanceLogger.read_logs()
        
        if not logs:
            print("No logs to export.")
            return
        
        import csv
        
        filepath = LOG_DIR / filename
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                "Timestamp", "Claim", "Verdict", "Confidence",
                "Total Input Tokens", "Total Output Tokens",
                "Prover Cost", "Debunker Cost", "Judge Cost", "Total Cost",
                "Revenue", "Profit", "Margin %",
                "Execution Time (s)"
            ])
            
            # Data
            for log in logs:
                writer.writerow([
                    log["timestamp"],
                    log["claim"],
                    log["verdict"],
                    log["confidence_score"],
                    log["tokens"]["total_input"],
                    log["tokens"]["total_output"],
                    log["costs"]["prover_cost"],
                    log["costs"]["debunker_cost"],
                    log["costs"]["judge_cost"],
                    log["costs"]["total_cost"],
                    log["economics"]["revenue_usdc"],
                    log["economics"]["profit_usd"],
                    log["economics"]["profit_margin_pct"],
                    log["metadata"]["execution_time_sec"]
                ])
        
        print(f"✅ Exported {len(logs)} logs to {filepath}")


def main():
    """CLI interface."""
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--summary":
            PerformanceLogger.print_summary()
        elif sys.argv[1] == "--export":
            PerformanceLogger.export_to_csv()
        elif sys.argv[1] == "--recent":
            n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            PerformanceLogger.print_recent_logs(n)
        else:
            print("Usage:")
            print("  python performance_log.py                # Show recent logs")
            print("  python performance_log.py --summary      # Show profit summary")
            print("  python performance_log.py --recent 20    # Show last 20 logs")
            print("  python performance_log.py --export       # Export to CSV")
    else:
        # Default: show recent logs and summary
        PerformanceLogger.print_recent_logs(10)
        PerformanceLogger.print_summary()


if __name__ == "__main__":
    main()
