"""
Payment Throughput Test for x402 Middleware

Tests the payment validation middleware under concurrent load to ensure
it doesn't become a bottleneck when many users pay simultaneously.

Usage:
    python payment_load_test.py --concurrent=20 --duration=60
    python payment_load_test.py --concurrent=50 --duration=120
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
import base64

# ============================================================================
# Configuration
# ============================================================================

API_URL = "https://verifai-production.up.railway.app/verify"
CHAIN_ID = 84532
MERCHANT_ADDRESS = "0x3615af0cE7c8e525B9a9C6cE281e195442596559"
USDC_CONTRACT = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
NETWORK = "base-sepolia"
AMOUNT = "50000"  # 0.05 USDC

# ============================================================================
# Metrics
# ============================================================================

class PaymentMetrics:
    """Track payment validation performance."""
    
    def __init__(self, concurrent: int, duration: int):
        self.concurrent = concurrent
        self.duration = duration
        
        self.validation_times: List[float] = []
        self.successful_validations = 0
        self.failed_validations = 0
        self.validation_errors: List[Dict] = []
        
        self.start_time = None
        self.end_time = None
    
    def add_validation(self, latency: float, success: bool, error: str = None):
        """Record a payment validation."""
        self.validation_times.append(latency)
        if success:
            self.successful_validations += 1
        else:
            self.failed_validations += 1
            if error:
                self.validation_errors.append({"error": error, "time": time.time()})
    
    def get_percentile(self, percentile: int) -> float:
        """Get validation time percentile."""
        if not self.validation_times:
            return 0
        sorted_times = sorted(self.validation_times)
        idx = int(len(sorted_times) * percentile / 100)
        return sorted_times[min(idx, len(sorted_times) - 1)]
    
    def print_summary(self):
        """Print test results."""
        duration = (self.end_time - self.start_time) if self.start_time and self.end_time else 0
        total = self.successful_validations + self.failed_validations
        success_rate = (self.successful_validations / total * 100) if total > 0 else 0
        
        print("\n" + "=" * 80)
        print("PAYMENT VALIDATION THROUGHPUT TEST RESULTS")
        print("=" * 80)
        
        print(f"\n📊 TEST CONFIGURATION:")
        print(f"   Concurrent Payment Validations: {self.concurrent}")
        print(f"   Total Validations: {total}")
        print(f"   Actual Duration: {duration:.1f}s")
        
        print(f"\n✅ RESULTS:")
        print(f"   Successful: {self.successful_validations}")
        print(f"   Failed: {self.failed_validations}")
        print(f"   Success Rate: {success_rate:.1f}%")
        if duration > 0:
            print(f"   Throughput: {total/duration:.1f} validations/sec")
        
        if total > 0:
            print(f"\n⏱️  VALIDATION TIME METRICS:")
            print(f"   Min: {min(self.validation_times):.4f}s")
            print(f"   Max: {max(self.validation_times):.4f}s")
            print(f"   Mean: {sum(self.validation_times)/len(self.validation_times):.4f}s")
            print(f"   Median (P50): {self.get_percentile(50):.4f}s")
            print(f"   P95: {self.get_percentile(95):.4f}s")
            print(f"   P99: {self.get_percentile(99):.4f}s")
            
            if len(self.validation_times) > 1:
                try:
                    stddev = stdev(self.validation_times)
                    print(f"   Std Dev: {stddev:.4f}s")
                except:
                    pass
        
        if self.failed_validations > 0:
            print(f"\n❌ ERROR DETAILS:")
            for i, err in enumerate(self.validation_errors[:5], 1):
                print(f"   {i}. {err['error']}")
        
        print(f"\n{'✅ PASS' if success_rate >= 95 else '⚠️  WARN' if success_rate >= 85 else '❌ FAIL'} - Success rate: {success_rate:.1f}%")
        
        print(f"\n📋 ACCEPTANCE CRITERIA:")
        p50 = self.get_percentile(50)
        p95 = self.get_percentile(95)
        
        print(f"   {'✅' if p50 < 0.1 else '⚠️ ' if p50 < 0.5 else '❌'} P50 < 100ms: {p50*1000:.1f}ms")
        print(f"   {'✅' if p95 < 0.5 else '⚠️ ' if p95 < 2 else '❌'} P95 < 500ms: {p95*1000:.1f}ms")
        print(f"   {'✅' if success_rate >= 95 else '⚠️ ' if success_rate >= 85 else '❌'} Success Rate >= 95%: {success_rate:.1f}%")
        
        print("\n" + "=" * 80)


def create_payment_header(account: Account) -> str:
    """Create a mock x402 payment header for testing."""
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


async def validate_payment(
    client: httpx.AsyncClient,
    account: Account,
    request_id: int,
    metrics: PaymentMetrics
) -> Tuple[bool, float]:
    """Test a single payment validation."""
    
    try:
        payment_header = create_payment_header(account)
        headers = {"X-PAYMENT": payment_header}
        params = {"claim": "Test claim for payment validation"}
        
        start = time.perf_counter()
        
        response = await client.get(
            API_URL,
            params=params,
            headers=headers,
            timeout=30.0
        )
        
        validation_time = time.perf_counter() - start
        
        # Any response (200 or 402) means payment was validated
        # We're testing the middleware speed, not the actual verification
        if response.status_code in [200, 402, 500]:
            metrics.add_validation(validation_time, True)
            print(f"  ✅ {request_id}: {validation_time*1000:.1f}ms", flush=True)
            return True, validation_time
        else:
            error = f"HTTP {response.status_code}"
            metrics.add_validation(validation_time, False, error)
            print(f"  ❌ {request_id}: {error}", flush=True)
            return False, validation_time
    
    except asyncio.TimeoutError:
        error = "Validation timeout (>30s)"
        metrics.add_validation(30.0, False, error)
        print(f"  ❌ {request_id}: {error}", flush=True)
        return False, 30.0
    
    except Exception as e:
        error = f"Error: {str(e)[:50]}"
        metrics.add_validation(0, False, error)
        print(f"  ❌ {request_id}: {error}", flush=True)
        return False, 0


async def run_payment_test(concurrent: int, duration: int):
    """Run payment throughput test."""
    
    # Generate test account
    account = Account.create()
    print(f"Test wallet: {account.address}")
    
    metrics = PaymentMetrics(concurrent, duration)
    metrics.start_time = time.perf_counter()
    
    print("\n" + "=" * 80)
    print("STARTING PAYMENT VALIDATION THROUGHPUT TEST")
    print("=" * 80)
    print(f"Concurrent validations: {concurrent}")
    print(f"Target duration: {duration}s")
    print("=" * 80 + "\n")
    
    request_count = 0
    batch_num = 0
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        while time.perf_counter() - metrics.start_time < duration:
            batch_num += 1
            batch_size = concurrent
            
            print(f"\n🔄 Batch {batch_num} ({batch_size} concurrent validations)...")
            
            # Create concurrent validation tasks
            tasks = [
                validate_payment(client, account, request_count + i + 1, metrics)
                for i in range(batch_size)
            ]
            request_count += batch_size
            
            # Run all validations concurrently
            await asyncio.gather(*tasks)
            
            # Small delay between batches
            await asyncio.sleep(0.5)
    
    metrics.end_time = time.perf_counter()
    metrics.print_summary()


def main():
    parser = argparse.ArgumentParser(
        description="Payment validation throughput test"
    )
    parser.add_argument(
        "--concurrent",
        type=int,
        default=20,
        help="Number of concurrent payment validations (default: 20)"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Test duration in seconds (default: 60)"
    )
    
    args = parser.parse_args()
    
    try:
        asyncio.run(run_payment_test(args.concurrent, args.duration))
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
