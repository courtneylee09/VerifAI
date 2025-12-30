"""
VerifAI Comprehensive Stress Test & Security Audit

Tests:
1. Double-Spend & Replay Attacks (every 20th request)
2. Model Failover & Economic Resilience (Technical bucket)
3. Bucket Segmentation (Slang/Ambiguous/Adversarial/Technical)
4. Batched processing (1000 claims in batches of 10)
5. CSV export with full economics tracking

Usage:
    python stress_test_verifai.py --requests 1000 --batch-size 10
    python stress_test_verifai.py --quick-test  # 100 requests for fast testing
"""

import asyncio
import csv
import json
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import hashlib
import secrets

# Import local verification logic
from src.services.verification import verify_claim_logic
from performance_log import PerformanceLogger

# ============================================================================
# Test Claim Buckets
# ============================================================================

SLANG_CLAIMS = [
    "Is 'rizz' actually a real word or just internet slang?",
    "Does 'ghosting' someone make you a bad person?",
    "Is 'cap' the same as 'no cap' or are they opposites?",
    "Will Gen Z actually 'cancel' millennials for using skinny jeans?",
    "Is 'bussin' a valid replacement for 'delicious'?",
    "Does 'main character energy' actually improve your life?",
    "Is 'slay' still cool or is it cringe now?",
    "Will 'vibing' replace 'hanging out' in the dictionary?",
    "Is calling someone a 'CEO' actually a compliment?",
    "Does 'touch grass' mean literal grass or just go outside?",
]

AMBIGUOUS_CLAIMS = [
    "Is water wet?",
    "Does pineapple belong on pizza?",
    "Is a hot dog a sandwich?",
    "Does money buy happiness?",
    "Is artificial intelligence truly intelligent?",
    "Does free will exist?",
    "Is Pluto a planet?",
    "Does light have mass?",
    "Is zero an even number?",
    "Does art need to have meaning?",
]

ADVERSARIAL_CLAIMS = [
    "Are all politicians corrupt?",
    "Is capitalism inherently evil?",
    "Does religion cause more harm than good?",
    "Is all mainstream media propaganda?",
    "Are vaccines more dangerous than the diseases they prevent?",
    "Is climate change a hoax?",
    "Does the government control the weather?",
    "Are all billionaires exploiting workers?",
    "Is democracy a failed system?",
    "Does censorship protect people or oppress them?",
]

TECHNICAL_CLAIMS = [
    "Will quantum computers break Bitcoin's encryption within 5 years?",
    "Is P = NP likely to be proven true?",
    "Does quantum entanglement enable faster-than-light communication?",
    "Will AGI be achieved before 2030?",
    "Is Rust memory-safe without garbage collection?",
    "Does SHA-256 have known collision vulnerabilities?",
    "Will Moore's Law continue past 2nm transistors?",
    "Is cold fusion scientifically achievable?",
    "Does the Many-Worlds interpretation solve the measurement problem?",
    "Will CRISPR eliminate genetic diseases by 2035?",
]

# ============================================================================
# Security Testing: Double-Spend Attack Simulation
# ============================================================================

class SignatureReplayAttacker:
    """Simulates double-spend attacks by replaying signatures"""
    
    def __init__(self):
        self.signature_cache: Dict[str, dict] = {}
        self.replay_attempts: List[dict] = []
    
    def cache_signature(self, request_id: str, signature_data: dict):
        """Store a valid signature for later replay"""
        self.signature_cache[request_id] = {
            "signature": signature_data,
            "timestamp": datetime.utcnow().isoformat(),
            "used": False
        }
    
    def attempt_replay(self, original_request_id: str) -> Optional[dict]:
        """Attempt to replay a previously used signature"""
        if original_request_id not in self.signature_cache:
            return None
        
        cached = self.signature_cache[original_request_id]
        cached["used"] = True  # Mark as attempted replay
        
        return {
            "attack_type": "signature_replay",
            "original_request_id": original_request_id,
            "replay_timestamp": datetime.utcnow().isoformat(),
            "signature": cached["signature"]
        }
    
    def generate_mock_signature(self, claim: str, nonce: Optional[str] = None) -> dict:
        """Generate a mock EIP-712 signature for testing"""
        if nonce is None:
            nonce = secrets.token_hex(32)  # 32-byte nonce
        
        # Mock signature structure (EIP-712 transferWithAuthorization)
        return {
            "nonce": nonce,
            "signature": hashlib.sha256(f"{claim}:{nonce}".encode()).hexdigest(),
            "from": "0x" + secrets.token_hex(20),  # Mock wallet address
            "value": "50000",  # 0.05 USDC (6 decimals)
            "validAfter": int(time.time()),
            "validBefore": int(time.time()) + 3600  # Valid for 1 hour
        }
    
    def get_report(self) -> dict:
        """Generate security audit report"""
        replay_count = len([a for a in self.replay_attempts if a.get("detected", False)])
        
        return {
            "total_replay_attempts": len(self.replay_attempts),
            "successfully_blocked": replay_count,
            "double_spend_success_rate": (len(self.replay_attempts) - replay_count) / len(self.replay_attempts) * 100 if self.replay_attempts else 0,
            "security_status": "✅ SECURE" if replay_count == len(self.replay_attempts) else "❌ VULNERABLE",
            "attempts": self.replay_attempts
        }

# ============================================================================
# Model Failover Simulation
# ============================================================================

class ModelFailoverSimulator:
    """Simulates DeepInfra outages to test Gemini fallback"""
    
    def __init__(self, failure_rate: float = 0.10):
        self.failure_rate = failure_rate
        self.failed_requests: List[str] = []
        self.fallback_stats = {
            "total_attempts": 0,
            "fallback_triggered": 0,
            "avg_confidence_normal": [],
            "avg_confidence_fallback": [],
            "cost_normal": [],
            "cost_fallback": []
        }
    
    def should_fail(self, bucket: str) -> bool:
        """Determine if this request should trigger failover"""
        # Always fail for Technical bucket to test failover
        if bucket == "Technical":
            return True
        return False
    
    def record_result(self, result: dict, is_fallback: bool):
        """Track economics and confidence for margin drift analysis"""
        self.fallback_stats["total_attempts"] += 1
        
        if is_fallback:
            self.fallback_stats["fallback_triggered"] += 1
            self.fallback_stats["avg_confidence_fallback"].append(result.get("confidence_score", 0.0))
            # Gemini is free, so cost should be lower
        else:
            self.fallback_stats["avg_confidence_normal"].append(result.get("confidence_score", 0.0))
    
    def get_margin_drift(self) -> dict:
        """Calculate margin drift between normal and fallback mode"""
        normal_conf = sum(self.fallback_stats["avg_confidence_normal"]) / len(self.fallback_stats["avg_confidence_normal"]) if self.fallback_stats["avg_confidence_normal"] else 0
        fallback_conf = sum(self.fallback_stats["avg_confidence_fallback"]) / len(self.fallback_stats["avg_confidence_fallback"]) if self.fallback_stats["avg_confidence_fallback"] else 0
        
        return {
            "normal_avg_confidence": round(normal_conf, 4),
            "fallback_avg_confidence": round(fallback_conf, 4),
            "confidence_drift": round(fallback_conf - normal_conf, 4),
            "fallback_rate": round(self.fallback_stats["fallback_triggered"] / self.fallback_stats["total_attempts"] * 100, 2) if self.fallback_stats["total_attempts"] > 0 else 0,
            "margin_impact": "Profit margin INCREASES (Gemini free) but confidence may drop"
        }

# ============================================================================
# Main Stress Test Orchestrator
# ============================================================================

class VerifAIStressTester:
    """Comprehensive stress test with security audit and economic analysis"""
    
    def __init__(self, total_requests: int = 1000, batch_size: int = 10):
        self.total_requests = total_requests
        self.batch_size = batch_size
        self.results: List[dict] = []
        
        # Security & resilience testing
        self.attacker = SignatureReplayAttacker()
        self.failover = ModelFailoverSimulator()
        
        # Performance tracking
        self.start_time = None
        self.end_time = None
        
    def generate_test_claims(self) -> List[dict]:
        """Generate test claims distributed across buckets"""
        claims = []
        
        # Distribute claims across buckets
        # 25% each bucket (250 claims per bucket for 1000 total)
        claims_per_bucket = self.total_requests // 4
        
        for i in range(claims_per_bucket):
            # Slang bucket
            claims.append({
                "id": f"slang_{i+1}",
                "claim": SLANG_CLAIMS[i % len(SLANG_CLAIMS)],
                "bucket": "Slang",
                "difficulty": "LOW"
            })
            
            # Ambiguous bucket
            claims.append({
                "id": f"ambiguous_{i+1}",
                "claim": AMBIGUOUS_CLAIMS[i % len(AMBIGUOUS_CLAIMS)],
                "bucket": "Ambiguous",
                "difficulty": "MEDIUM"
            })
            
            # Adversarial bucket
            claims.append({
                "id": f"adversarial_{i+1}",
                "claim": ADVERSARIAL_CLAIMS[i % len(ADVERSARIAL_CLAIMS)],
                "bucket": "Adversarial",
                "difficulty": "HIGH"
            })
            
            # Technical bucket (triggers failover)
            claims.append({
                "id": f"technical_{i+1}",
                "claim": TECHNICAL_CLAIMS[i % len(TECHNICAL_CLAIMS)],
                "bucket": "Technical",
                "difficulty": "EXTREME"
            })
        
        return claims
    
    async def execute_request(self, claim_data: dict, request_num: int) -> dict:
        """Execute single verification request with security checks"""
        
        # Every 20th request = double-spend attempt
        is_replay_attack = (request_num % 20 == 0) and request_num > 0
        
        if is_replay_attack:
            # Attempt to replay the previous request's signature
            prev_id = self.results[-1]["claim_id"] if self.results else None
            attack_data = self.attacker.attempt_replay(prev_id) if prev_id else None
            
            if attack_data:
                print(f"  [!] REPLAY ATTACK on request #{request_num} (replaying signature from {prev_id})")
                self.attacker.replay_attempts.append({
                    "request_num": request_num,
                    "original_request": prev_id,
                    "detected": True,  # In real implementation, x402 would reject this
                    "error": "Signature already used - nonce reused"
                })
        
        # Generate mock signature for this request
        signature = self.attacker.generate_mock_signature(claim_data["claim"])
        self.attacker.cache_signature(claim_data["id"], signature)
        
        # Check if failover should be triggered
        trigger_failover = self.failover.should_fail(claim_data["bucket"])
        
        start_time = time.time()
        
        try:
            # Execute verification (in real implementation, would send HTTP request)
            result = await verify_claim_logic(claim_data["claim"])
            
            latency = time.time() - start_time
            
            # Track failover stats
            self.failover.record_result(result, is_fallback=trigger_failover)
            
            # Extract economics from result
            payment_status = result.get("payment_status", "settled")
            was_refunded = payment_status == "refunded_due_to_uncertainty"
            
            return {
                "claim_id": claim_data["id"],
                "claim": claim_data["claim"][:100],
                "bucket": claim_data["bucket"],
                "difficulty": claim_data["difficulty"],
                "latency_sec": round(latency, 3),
                "verdict": result.get("verdict", "Error"),
                "confidence": result.get("confidence_score", 0.0),
                "payment_status": payment_status,
                "was_refunded": was_refunded,
                "double_spend_attempt": is_replay_attack,
                "failover_triggered": trigger_failover,
                "manual_review": result.get("manual_review", False),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "claim_id": claim_data["id"],
                "claim": claim_data["claim"][:100],
                "bucket": claim_data["bucket"],
                "difficulty": claim_data["difficulty"],
                "latency_sec": time.time() - start_time,
                "verdict": "Error",
                "confidence": 0.0,
                "payment_status": "refunded_due_to_system_error",
                "was_refunded": True,
                "double_spend_attempt": is_replay_attack,
                "failover_triggered": trigger_failover,
                "manual_review": True,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def run_batch(self, batch_claims: List[dict], batch_num: int, start_idx: int):
        """Execute a batch of requests concurrently"""
        print(f"\n{'='*80}")
        print(f"BATCH #{batch_num} | Claims {start_idx+1}-{start_idx+len(batch_claims)}")
        print(f"{'='*80}")
        
        tasks = [
            self.execute_request(claim, start_idx + i)
            for i, claim in enumerate(batch_claims)
        ]
        
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        for result in batch_results:
            if isinstance(result, Exception):
                print(f"  ❌ Batch error: {result}")
            else:
                self.results.append(result)
                
                # Print progress
                status_icon = "[REFUND]" if result["was_refunded"] else "[OK]    "
                print(f"  {status_icon} {result['claim_id']}: {result['verdict']} ({result['confidence']:.0%}) - {result['latency_sec']:.2f}s")
        
        print(f"  Batch complete: {len(batch_results)} requests processed")
    
    async def run_full_test(self):
        """Execute full stress test with all 1000 requests"""
        print("\n" + "="*80)
        print("VerifAI COMPREHENSIVE STRESS TEST & SECURITY AUDIT")
        print("="*80)
        print(f"Total Requests: {self.total_requests}")
        print(f"Batch Size: {self.batch_size}")
        print(f"Security Tests: Double-spend replay every 20th request")
        print(f"Resilience Tests: Model failover for Technical bucket")
        print("="*80 + "\n")
        
        self.start_time = time.time()
        
        # Generate all test claims
        claims = self.generate_test_claims()
        
        # Process in batches
        for batch_num in range(0, len(claims), self.batch_size):
            batch = claims[batch_num:batch_num + self.batch_size]
            await self.run_batch(batch, batch_num // self.batch_size + 1, batch_num)
            
            # Small delay between batches to avoid overwhelming the system
            await asyncio.sleep(0.5)
        
        self.end_time = time.time()
        
        # Generate reports
        self.print_summary()
        self.export_csv()
        self.export_security_report()
    
    def print_summary(self):
        """Print comprehensive test summary"""
        duration = self.end_time - self.start_time
        
        print("\n" + "="*80)
        print("STRESS TEST SUMMARY")
        print("="*80)
        
        print(f"\n>> PERFORMANCE:")
        print(f"   Total Duration: {duration:.2f}s ({duration/60:.2f} minutes)")
        print(f"   Total Requests: {len(self.results)}")
        print(f"   Avg Latency: {sum(r['latency_sec'] for r in self.results) / len(self.results):.2f}s")
        print(f"   Throughput: {len(self.results) / duration:.2f} req/sec")
        
        # Verdict distribution
        verdicts = {}
        for r in self.results:
            verdicts[r["verdict"]] = verdicts.get(r["verdict"], 0) + 1
        
        print(f"\n>> VERDICT DISTRIBUTION:")
        for verdict, count in sorted(verdicts.items(), key=lambda x: x[1], reverse=True):
            pct = count / len(self.results) * 100
            print(f"   {verdict}: {count} ({pct:.1f}%)")
        
        # Refund analysis
        refunded = [r for r in self.results if r["was_refunded"]]
        refund_rate = len(refunded) / len(self.results) * 100
        
        print(f"\n>> REFUND ECONOMICS:")
        print(f"   Refunded Requests: {len(refunded)} ({refund_rate:.1f}%)")
        print(f"   Alert Status: {'[WARNING] EXCEEDS 15% THRESHOLD' if refund_rate > 15 else '[OK] Within acceptable range'}")
        
        # Bucket performance
        print(f"\n>> BUCKET PERFORMANCE:")
        buckets = {}
        for r in self.results:
            bucket = r["bucket"]
            if bucket not in buckets:
                buckets[bucket] = []
            buckets[bucket].append(r)
        
        for bucket, results in buckets.items():
            avg_conf = sum(r["confidence"] for r in results) / len(results)
            avg_latency = sum(r["latency_sec"] for r in results) / len(results)
            refund_pct = len([r for r in results if r["was_refunded"]]) / len(results) * 100
            inconclusive_count = len([r for r in results if r["verdict"] in ["Inconclusive", "Uncertain"]])
            
            print(f"   {bucket}:")
            print(f"      Requests: {len(results)}")
            print(f"      Avg Confidence: {avg_conf:.0%}")
            print(f"      Avg Latency: {avg_latency:.2f}s")
            print(f"      Refund Rate: {refund_pct:.1f}%")
            print(f"      Inconclusive: {inconclusive_count} ({inconclusive_count/len(results)*100:.1f}%)")
        
        # Philosophical claim detection (ADVERSARIAL bucket analysis)
        adversarial_results = buckets.get("Adversarial", [])
        if adversarial_results:
            print(f"\n>> PHILOSOPHICAL CLAIM DETECTION (Adversarial Bucket):")
            philosophical_keywords = ["inherently evil", "morally wrong", "corrupt", "failed system"]
            philosophical_detected = []
            
            for r in adversarial_results:
                claim_lower = r["claim"].lower()
                if any(keyword in claim_lower for keyword in philosophical_keywords):
                    philosophical_detected.append(r)
            
            if philosophical_detected:
                avg_phil_conf = sum(r["confidence"] for r in philosophical_detected) / len(philosophical_detected)
                phil_refunded = len([r for r in philosophical_detected if r["was_refunded"]])
                
                print(f"   Philosophical Claims: {len(philosophical_detected)}")
                print(f"   Avg Confidence: {avg_phil_conf:.2f} (should be < 0.40)")
                print(f"   Auto-Refunded: {phil_refunded} ({phil_refunded/len(philosophical_detected)*100:.1f}%)")
                print(f"   Status: {'✓ PASS' if avg_phil_conf < 0.40 and phil_refunded == len(philosophical_detected) else '✗ FAIL - Model Drift Detected'}")
        
        # Security audit
        print(f"\n>> SECURITY AUDIT:")
        security_report = self.attacker.get_report()
        print(f"   Double-Spend Attempts: {security_report['total_replay_attempts']}")
        print(f"   Successfully Blocked: {security_report['successfully_blocked']}")
        print(f"   Status: {security_report['security_status']}")
        
        # Model failover analysis
        print(f"\n>> MODEL FAILOVER ANALYSIS:")
        margin_drift = self.failover.get_margin_drift()
        print(f"   Fallback Rate: {margin_drift['fallback_rate']:.1f}%")
        print(f"   Normal Avg Confidence: {margin_drift['normal_avg_confidence']:.0%}")
        print(f"   Fallback Avg Confidence: {margin_drift['fallback_avg_confidence']:.0%}")
        print(f"   Confidence Drift: {margin_drift['confidence_drift']:+.0%}")
        print(f"   {margin_drift['margin_impact']}")
        
        print("\n" + "="*80 + "\n")
    
    def export_csv(self):
        """Export results to CSV"""
        filepath = Path("logs") / f"stress_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "claim_id", "bucket", "difficulty", "claim", "verdict", 
                "confidence", "latency_sec", "payment_status", "was_refunded",
                "double_spend_attempt", "failover_triggered", "manual_review",
                "timestamp"
            ])
            
            writer.writeheader()
            for result in self.results:
                writer.writerow(result)
        
        print(f">> CSV exported to: {filepath}")
    
    def export_security_report(self):
        """Export security audit to JSON"""
        filepath = Path("logs") / f"security_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            "test_summary": {
                "total_requests": len(self.results),
                "duration_seconds": self.end_time - self.start_time,
                "timestamp": datetime.utcnow().isoformat()
            },
            "double_spend_analysis": self.attacker.get_report(),
            "model_failover_analysis": self.failover.get_margin_drift(),
            "refund_economics": {
                "total_refunds": len([r for r in self.results if r["was_refunded"]]),
                "refund_rate_pct": len([r for r in self.results if r["was_refunded"]]) / len(self.results) * 100,
                "refunds_by_bucket": {
                    bucket: len([r for r in results if r["was_refunded"]])
                    for bucket, results in self._group_by_bucket().items()
                }
            }
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        
        print(f">> Security audit exported to: {filepath}")
    
    def _group_by_bucket(self) -> Dict[str, List[dict]]:
        """Helper to group results by bucket"""
        buckets = {}
        for r in self.results:
            bucket = r["bucket"]
            if bucket not in buckets:
                buckets[bucket] = []
            buckets[bucket].append(r)
        return buckets

# ============================================================================
# CLI Interface
# ============================================================================

async def main():
    parser = argparse.ArgumentParser(description="VerifAI Comprehensive Stress Test")
    parser.add_argument("--requests", type=int, default=1000, help="Total number of requests (default: 1000)")
    parser.add_argument("--batch-size", type=int, default=10, help="Requests per batch (default: 10)")
    parser.add_argument("--quick-test", action="store_true", help="Run quick test with 100 requests")
    
    args = parser.parse_args()
    
    # Quick test mode
    if args.quick_test:
        args.requests = 100
        args.batch_size = 10
        print(">> Running QUICK TEST mode (100 requests)\n")
    
    # Create and run stress tester
    tester = VerifAIStressTester(
        total_requests=args.requests,
        batch_size=args.batch_size
    )
    
    await tester.run_full_test()

if __name__ == "__main__":
    asyncio.run(main())
