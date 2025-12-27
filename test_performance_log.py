"""
Test the performance logger with simulated data.
"""

from performance_log import PerformanceLogger

print("Creating test performance log entries...\n")

# Simulate a successful verification with typical token usage
PerformanceLogger.log_request(
    claim="Bitcoin was invented in 2009",
    verdict="Verified",
    confidence_score=0.95,
    prover_tokens={
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "input": 1200,
        "output": 150
    },
    debunker_tokens={
        "model": "deepseek-ai/DeepSeek-V3",
        "input": 1150,
        "output": 140
    },
    judge_tokens={
        "model": "claude-3-5-haiku-20241022",
        "input": 2500,
        "output": 80
    },
    search_count=10,
    execution_time=8.5
)

# Simulate a cheaper request (fewer tokens)
PerformanceLogger.log_request(
    claim="The sky is blue",
    verdict="Verified",
    confidence_score=0.98,
    prover_tokens={
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "input": 800,
        "output": 100
    },
    debunker_tokens={
        "model": "deepseek-ai/DeepSeek-V3",
        "input": 750,
        "output": 90
    },
    judge_tokens={
        "model": "claude-3-5-haiku-20241022",
        "input": 1800,
        "output": 60
    },
    search_count=8,
    execution_time=6.2
)

# Simulate a more expensive request (using Gemini fallback - free)
PerformanceLogger.log_request(
    claim="Will it rain tomorrow in New York?",
    verdict="Uncertain",
    confidence_score=0.65,
    prover_tokens={
        "model": "gemini-2.0-flash-exp",
        "input": 1500,
        "output": 200
    },
    debunker_tokens={
        "model": "gemini-2.0-flash-exp",
        "input": 1400,
        "output": 180
    },
    judge_tokens={
        "model": "claude-3-5-haiku-20241022",
        "input": 3200,
        "output": 100
    },
    search_count=12,
    execution_time=12.3
)

print("✅ Created 3 test log entries\n")

# Show the results
PerformanceLogger.print_summary()
PerformanceLogger.print_recent_logs(3)

print("NOTE: These are SIMULATED test entries to demonstrate the logger.")
print("Real entries will be created automatically when users pay to verify claims.\n")
