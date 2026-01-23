"""
Concurrent Load Test for VerifAI x402 Service

Tests behavior under simultaneous user load to identify bottlenecks,
timeouts, and performance degradation before x402 bazaar launch.

Usage:
    python concurrent_stress_test.py --workers=5 --duration=300 --claims=50
    python concurrent_stress_test.py --workers=10 --duration=60
    python concurrent_stress_test.py --help
"""

import asyncio
import argparse
import time
import json
import sys
import os
from datetime import datetime
from statistics import median, stdev
from pathlib import Path
from typing import Dict, List, Tuple
import random

try:
    import httpx
except ImportError:
    print("Installing required packages...")
    os.system("pip install httpx --no-deps")
    import httpx

try:
    from eth_account import Account
    from eth_account.messages import encode_typed_data
except ImportError:
    print("Note: eth-account not available, using mock account for testing")
    # Mock Account class for testing without eth-account
    class Account:
        @staticmethod
        def create():
            import hashlib
            addr = hashlib.sha256(str(time.time()).encode()).hexdigest()[:40]
            return type('MockAccount', (), {'address': f'0x{addr}'})()
        
        @staticmethod
        def from_key(key):
            return Account.create()

import secrets

# ============================================================================
# Configuration
# ============================================================================

# Test configuration
API_URL = "https://verifai-production.up.railway.app/verify"
LOCAL_API_URL = "http://localhost:8000/verify"
CHAIN_ID = 84532  # Base Sepolia

# Payment configuration (from your config)
MERCHANT_ADDRESS = "0x3615af0cE7c8e525B9a9C6cE281e195442596559"
USDC_CONTRACT = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
NETWORK = "base-sepolia"
AMOUNT = "50000"  # 0.05 USDC (6 decimals)

# Test claims - diverse set
TEST_CLAIMS = [
    # Factual
    "Bitcoin was invented in 2009",
    "The moon is Earth's natural satellite",
    "Water boils at 100 degrees Celsius at sea level",
    "The Great Wall of China is visible from space",
    "Honey never spoils",
    
    # Slang
    "Is 'rizz' a real word?",
    "Is 'bussin' valid slang?",
    "Does 'cap' mean lying?",
    
    # Ambiguous
    "Does pineapple belong on pizza?",
    "Is vanilla or chocolate better?",
    "Does free will exist?",
    "Is art meaningful?",
    
    # Recent/News
    "COVID-19 pandemic started in 2019",
    "AI has surpassed human intelligence",
    "Electric cars are better than gas cars",
    
    # Technical
    "Is quantum computing viable by 2030?",
    "Will AGI be achieved before 2030?",
    "Is P=NP likely true?",
    
    # Controversial (low confidence expected)
    "Are vaccines safe?",
    "Is democracy the best system?",
    "Does climate change exist?",
]

# ============================================================================
# Metrics Collection
# ============================================================================

class LoadTestMetrics:
    """Collect and analyze performance metrics."""
    
    def __init__(self, num_workers: int, duration: int, num_claims: int):
        self.num_workers = num_workers
        self.duration = duration
        self.num_claims = num_claims
        
        # Metrics
        self.request_times: List[float] = []
        self.successful_requests = 0
        self.failed_requests = 0
        self.timeout_errors = 0
        self.validation_errors = 0
        self.payment_errors = 0
        self.other_errors = 0
        
        # Error details
        self.errors: List[Dict] = []
        self.start_time = None
        self.end_time = None
        
    def add_request(self, latency: float, success: bool, error: str = None):
        """Record a request result."""
        self.request_times.append(latency)
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
            if "timeout" in error.lower():
                self.timeout_errors += 1
            elif "payment" in error.lower() or "402" in error.lower():
                self.payment_errors += 1
            elif "validation" in error.lower():
                self.validation_errors += 1
            else:
                self.other_errors += 1
            
            self.errors.append({
                "error": error,
                "timestamp": datetime.now().isoformat()
            })
    
    def get_percentile(self, percentile: int) -> float:
        """Get latency percentile."""
        if not self.request_times:
            return 0
        sorted_times = sorted(self.request_times)
        idx = int(len(sorted_times) * percentile / 100)
        return sorted_times[min(idx, len(sorted_times) - 1)]
    
    def print_summary(self):
        """Print test results summary."""
        duration = (self.end_time - self.start_time) if self.start_time and self.end_time else 0
        total_requests = self.successful_requests + self.failed_requests
        success_rate = (self.successful_requests / total_requests * 100) if total_requests > 0 else 0
        
        print("\n" + "=" * 80)
        print("CONCURRENT LOAD TEST RESULTS")
        print("=" * 80)
        
        print(f"\n📊 TEST CONFIGURATION:")
        print(f"   Workers: {self.num_workers}")
        print(f"   Duration: {self.duration}s")
        print(f"   Claims per worker: {self.num_claims}")
        print(f"   Total requests: {total_requests}")
        
        print(f"\n✅ SUCCESS METRICS:")
        print(f"   Successful: {self.successful_requests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Actual Duration: {duration:.1f}s")
        print(f"   Requests/sec: {total_requests/duration:.2f}" if duration > 0 else "")
        
        if total_requests > 0:
            print(f"\n⏱️  LATENCY METRICS:")
            print(f"   Min: {min(self.request_times):.2f}s")
            print(f"   Max: {max(self.request_times):.2f}s")
            print(f"   Mean: {sum(self.request_times)/len(self.request_times):.2f}s")
            print(f"   Median (P50): {self.get_percentile(50):.2f}s")
            print(f"   P95: {self.get_percentile(95):.2f}s")
            print(f"   P99: {self.get_percentile(99):.2f}s")
            
            if len(self.request_times) > 1:
                try:
                    stddev = stdev(self.request_times)
                    print(f"   Std Dev: {stddev:.2f}s")
                except:
                    pass
        
        if self.failed_requests > 0:
            print(f"\n❌ ERROR BREAKDOWN ({self.failed_requests} total):")
            print(f"   Timeouts: {self.timeout_errors}")
            print(f"   Payment Errors: {self.payment_errors}")
            print(f"   Validation Errors: {self.validation_errors}")
            print(f"   Other Errors: {self.other_errors}")
            
            if self.errors:
                print(f"\n   Error Details (first 5):")
                for i, err in enumerate(self.errors[:5], 1):
                    print(f"   {i}. {err['error']}")
        
        print(f"\n{'✅ PASS' if success_rate >= 95 else '⚠️  WARN' if success_rate >= 80 else '❌ FAIL'} - Success rate: {success_rate:.1f}%")
        
        # Acceptance criteria
        print(f"\n📋 ACCEPTANCE CRITERIA:")
        p50 = self.get_percentile(50)
        p95 = self.get_percentile(95)
        p99 = self.get_percentile(99)
        
        p50_pass = "✅" if p50 < 15 else "⚠️ " if p50 < 25 else "❌"
        p95_pass = "✅" if p95 < 25 else "⚠️ " if p95 < 30 else "❌"
        p99_pass = "✅" if p99 < 30 else "⚠️ " if p99 < 35 else "❌"
        success_pass = "✅" if success_rate >= 95 else "⚠️ " if success_rate >= 85 else "❌"
        
        print(f"   {p50_pass} P50 < 15s: {p50:.2f}s")
        print(f"   {p95_pass} P95 < 25s: {p95:.2f}s")
        print(f"   {p99_pass} P99 < 30s: {p99:.2f}s")
        print(f"   {success_pass} Success Rate >= 95%: {success_rate:.1f}%")
        
        print("\n" + "=" * 80)
        
        # Save results to file
        self._save_results()
    
    def _save_results(self):
        """Save test results to JSON file."""
        results_dir = Path("logs")
        results_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = results_dir / f"concurrent_load_test_{timestamp}.json"
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "configuration": {
                "workers": self.num_workers,
                "duration": self.duration,
                "claims_per_worker": self.num_claims,
            },
            "results": {
                "total_requests": self.successful_requests + self.failed_requests,
                "successful": self.successful_requests,
                "failed": self.failed_requests,
                "success_rate": self.successful_requests / (self.successful_requests + self.failed_requests) if (self.successful_requests + self.failed_requests) > 0 else 0,
                "latency": {
                    "min": min(self.request_times) if self.request_times else 0,
                    "max": max(self.request_times) if self.request_times else 0,
                    "mean": sum(self.request_times) / len(self.request_times) if self.request_times else 0,
                    "p50": self.get_percentile(50),
                    "p95": self.get_percentile(95),
                    "p99": self.get_percentile(99),
                },
                "errors": {
                    "timeout": self.timeout_errors,
                    "payment": self.payment_errors,
                    "validation": self.validation_errors,
                    "other": self.other_errors,
                }
            }
        }
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"   Results saved to: {results_file}")


# ============================================================================
# Payment Header Generation
# ============================================================================

def create_payment_header(account: Account) -> str:
    """Create a mock x402 payment header for testing."""
    import base64
    nonce = secrets.token_bytes(32)
    valid_after = int(time.time()) - 60
    valid_before = int(time.time()) + 60
    
    # Mock signature for testing (realistic format)
    signature = "0x" + secrets.token_hex(65)
    
    # Get account address (handle both real and mock accounts)
    addr = getattr(account, 'address', "0x" + secrets.token_hex(20))
    
    payment_header = {
        "x402Version": 1,
        "scheme": "exact",
        "network": NETWORK,
        "payload": {
            "signature": signature,
            "authorization": {
                "from": addr,
                "to": MERCHANT_ADDRESS,
                "value": AMOUNT,
                "validAfter": str(valid_after),
                "validBefore": str(valid_before),
                "nonce": f"0x{nonce.hex()}",
            },
        },
    }
    
    json_str = json.dumps(payment_header)
    return base64.b64encode(json_str.encode()).decode()


# ============================================================================
# Concurrent Load Testing
# ============================================================================

async def verify_claim(
    client: httpx.AsyncClient,
    claim: str,
    account: Account,
    worker_id: int,
    request_id: int,
    metrics: LoadTestMetrics
) -> Tuple[bool, float, str]:
    """Make a single verification request and track metrics."""
    
    try:
        payment_header = create_payment_header(account)
        headers = {"X-PAYMENT": payment_header}
        params = {"claim": claim}
        
        start = time.perf_counter()
        
        response = await client.get(
            API_URL,
            params=params,
            headers=headers,
            timeout=60.0  # 60 second timeout
        )
        
        latency = time.perf_counter() - start
        
        if response.status_code == 200:
            # Success
            metrics.add_request(latency, True)
            print(f"  ✅ W{worker_id}-R{request_id}: {latency:.2f}s", flush=True)
            return True, latency, ""
        
        elif response.status_code == 402:
            # Payment required (shouldn't happen with valid header)
            error = f"Payment required (402)"
            metrics.add_request(latency, False, error)
            print(f"  ❌ W{worker_id}-R{request_id}: {error}", flush=True)
            return False, latency, error
        
        else:
            error = f"HTTP {response.status_code}: {response.text[:100]}"
            metrics.add_request(latency, False, error)
            print(f"  ❌ W{worker_id}-R{request_id}: {error}", flush=True)
            return False, latency, error
    
    except asyncio.TimeoutError:
        error = "Request timeout (>60s)"
        metrics.add_request(60.0, False, error)
        print(f"  ❌ W{worker_id}-R{request_id}: {error}", flush=True)
        return False, 60.0, error
    
    except Exception as e:
        error = f"Error: {str(e)[:100]}"
        metrics.add_request(0, False, error)
        print(f"  ❌ W{worker_id}-R{request_id}: {error}", flush=True)
        return False, 0, error


async def worker(
    worker_id: int,
    num_claims: int,
    account: Account,
    metrics: LoadTestMetrics
):
    """Worker coroutine that makes multiple requests."""
    
    print(f"\n🚀 Worker {worker_id} starting ({num_claims} claims)...", flush=True)
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        for request_id in range(1, num_claims + 1):
            claim = random.choice(TEST_CLAIMS)
            await verify_claim(client, claim, account, worker_id, request_id, metrics)
            
            # Small delay between requests to avoid hammering
            await asyncio.sleep(0.1)
    
    print(f"\n✅ Worker {worker_id} completed!", flush=True)


async def run_load_test(
    num_workers: int,
    duration: int,
    num_claims: int,
    private_key: str = None
):
    """Run concurrent load test."""
    
    # Generate test account
    if private_key:
        try:
            account = Account.from_key(private_key)
            print(f"Using provided wallet: {account.address}")
        except Exception as e:
            print(f"❌ Invalid private key: {e}")
            sys.exit(1)
    else:
        # Generate random account for testing
        account = Account.create()
        print(f"⚠️  Generated test wallet (no real funds needed for payment header generation)")
        print(f"   Address: {account.address}")
        print(f"   (Private key format generation only, no actual transactions)")
    
    metrics = LoadTestMetrics(num_workers, duration, num_claims)
    metrics.start_time = time.perf_counter()
    
    print("\n" + "=" * 80)
    print("STARTING CONCURRENT LOAD TEST")
    print("=" * 80)
    print(f"Workers: {num_workers}")
    print(f"Claims per worker: {num_claims}")
    print(f"Total requests: {num_workers * num_claims}")
    print(f"API: {API_URL}")
    print("=" * 80 + "\n")
    
    # Create worker tasks
    tasks = [
        worker(i + 1, num_claims, account, metrics)
        for i in range(num_workers)
    ]
    
    # Run all workers concurrently
    await asyncio.gather(*tasks)
    
    metrics.end_time = time.perf_counter()
    
    # Print results
    metrics.print_summary()


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Concurrent load test for VerifAI x402 service"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=5,
        help="Number of concurrent workers (default: 5)"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=300,
        help="Test duration in seconds (default: 300s)"
    )
    parser.add_argument(
        "--claims",
        type=int,
        default=50,
        help="Number of claims per worker (default: 50)"
    )
    parser.add_argument(
        "--key",
        type=str,
        default=None,
        help="Private key for payment (optional, will generate random if not provided)"
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Test against local API instead of production"
    )
    
    args = parser.parse_args()
    
    # Run test
    try:
        asyncio.run(run_load_test(
            args.workers,
            args.duration,
            args.claims,
            args.key
        ))
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
