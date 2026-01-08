"""
Conservative 1000-Request Stress Test for Exa Pay-As-You-Go ($9 balance)

Exa Pricing (Pay-As-You-Go):
- Search: $0.50 per 1,000 searches
- Contents (autoprompt): $3.00 per 1,000 requests

Per VerifAI request:
- 1 search call = $0.0005
- 5 contents calls (NUM_SOURCES_TO_RETRIEVE) = $0.015
- Total Exa cost per request: ~$0.0155

For 1000 requests:
- Estimated Exa cost: $15.50
- Your balance: $9.00
- Maximum safe requests: ~580 requests

STRATEGY: Run in batches of 100 to monitor costs and stop if needed.
"""

import asyncio
import csv
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List

from src.services.verification import verify_claim_logic

# Same test claims as stress_test_verifai.py
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

class ConservativeStressTester:
    def __init__(self, total_requests: int = 1000, batch_size: int = 100):
        self.total_requests = total_requests
        self.batch_size = batch_size
        self.results = []
        self.start_time = None
        self.exa_cost_estimate = 0.0
        self.pre_filtered_count = 0
        
    def generate_claims(self, count: int) -> List[dict]:
        """Generate rotating claims across all buckets"""
        claims = []
        buckets = [
            ("Slang", SLANG_CLAIMS),
            ("Ambiguous", AMBIGUOUS_CLAIMS),
            ("Adversarial", ADVERSARIAL_CLAIMS),
            ("Technical", TECHNICAL_CLAIMS)
        ]
        
        for i in range(count):
            bucket_name, bucket_claims = buckets[i % len(buckets)]
            claim = bucket_claims[i % len(bucket_claims)]
            
            claims.append({
                "id": i + 1,
                "bucket": bucket_name,
                "claim": claim
            })
        
        return claims
    
    async def execute_request(self, claim_data: dict, request_num: int) -> dict:
        """Execute single verification request"""
        start_time = time.time()
        
        try:
            result = await verify_claim_logic(claim_data["claim"])
            latency = time.time() - start_time
            
            # Track if pre-filtered (no Exa cost)
            pre_filtered = result.get("pre_filtered", False)
            if pre_filtered:
                self.pre_filtered_count += 1
                exa_cost = 0.0
            else:
                # Estimate Exa cost: 1 search ($0.0005) + 5 contents ($0.015)
                exa_cost = 0.0155
            
            self.exa_cost_estimate += exa_cost
            
            verdict = result.get("verdict")
            confidence = result.get("confidence_score", 0)
            payment_status = result.get("payment_status", "settled")
            was_refunded = payment_status == "refunded_due_to_uncertainty"
            
            return {
                "claim_id": claim_data["id"],
                "bucket": claim_data["bucket"],
                "claim": claim_data["claim"][:100],
                "verdict": verdict,
                "confidence": confidence,
                "payment_status": payment_status,
                "was_refunded": was_refunded,
                "pre_filtered": pre_filtered,
                "latency_sec": round(latency, 2),
                "exa_cost_estimate": round(exa_cost, 4),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "claim_id": claim_data["id"],
                "bucket": claim_data["bucket"],
                "claim": claim_data["claim"][:100],
                "verdict": "Error",
                "confidence": 0.0,
                "payment_status": "refunded_due_to_system_error",
                "was_refunded": True,
                "pre_filtered": False,
                "latency_sec": time.time() - start_time,
                "exa_cost_estimate": 0.0,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def run_batch(self, claims: List[dict], batch_num: int):
        """Run batch sequentially to respect Exa limits"""
        print(f"\n{'='*80}")
        print(f"BATCH #{batch_num} | Requests {claims[0]['id']}-{claims[-1]['id']}")
        print(f"{'='*80}")
        
        batch_start = time.time()
        
        for claim in claims:
            result = await self.execute_request(claim, claim['id'])
            self.results.append(result)
            
            # Progress indicator
            pre = "[PRE-FILTERED]" if result.get("pre_filtered") else ""
            refund = "REFUND" if result["was_refunded"] else "CHARGE"
            print(f"  [{claim['id']}/{self.total_requests}] {pre} {refund} | "
                  f"{result['verdict']} @ {result['confidence']:.2f} | "
                  f"{result['latency_sec']:.1f}s | Exa: ${result['exa_cost_estimate']:.4f}")
            
            # Respect Exa 5 req/sec limit (200ms between requests)
            await asyncio.sleep(0.2)
        
        batch_duration = time.time() - batch_start
        
        print(f"\nBatch Complete: {len(claims)} requests in {batch_duration:.1f}s")
        print(f"Running Exa Cost: ${self.exa_cost_estimate:.2f} / $9.00 balance")
        print(f"Pre-Filtered (zero cost): {self.pre_filtered_count}")
        
        # Safety check
        if self.exa_cost_estimate >= 8.50:
            print(f"\n*** WARNING: Approaching $9 Exa balance limit! ***")
            print(f"*** Recommend stopping after this batch ***")
        
    async def run_test(self):
        """Run full test with batch checkpoints"""
        self.start_time = time.time()
        
        print("\n" + "="*80)
        print("CONSERVATIVE 1000-REQUEST STRESS TEST")
        print("="*80)
        print(f"\nTotal Requests: {self.total_requests}")
        print(f"Batch Size: {self.batch_size}")
        print(f"Exa Balance: $9.00")
        print(f"Estimated Max Requests: ~580 (before hitting balance limit)")
        print(f"Strategy: Sequential processing, 200ms delays (5 req/sec)")
        print("\n" + "="*80)
        
        # Generate all claims
        all_claims = self.generate_claims(self.total_requests)
        
        # Process in batches
        for batch_start in range(0, len(all_claims), self.batch_size):
            batch = all_claims[batch_start:batch_start + self.batch_size]
            batch_num = (batch_start // self.batch_size) + 1
            
            await self.run_batch(batch, batch_num)
            
            # Check if we should continue
            if self.exa_cost_estimate >= 8.50:
                print(f"\n*** STOPPING: Exa cost ${self.exa_cost_estimate:.2f} too close to $9 limit ***")
                break
            
            # Export checkpoint after each batch
            self.export_csv(f"_batch_{batch_num}")
        
        # Final summary
        self.print_summary()
        self.export_csv()
    
    def print_summary(self):
        """Print comprehensive summary"""
        duration = time.time() - self.start_time
        
        print("\n" + "="*80)
        print("STRESS TEST SUMMARY")
        print("="*80)
        
        print(f"\nCompleted Requests: {len(self.results)}")
        print(f"Duration: {duration/60:.1f} minutes")
        print(f"Throughput: {len(self.results)/duration:.2f} req/sec")
        
        # Exa cost analysis
        print(f"\n>> EXA API COSTS:")
        print(f"   Total Estimated Cost: ${self.exa_cost_estimate:.2f}")
        print(f"   Remaining Balance: ${9.00 - self.exa_cost_estimate:.2f}")
        print(f"   Pre-Filtered (zero cost): {self.pre_filtered_count} ({self.pre_filtered_count/len(self.results)*100:.1f}%)")
        print(f"   Exa Searches Used: {len(self.results) - self.pre_filtered_count}")
        
        # Refund analysis
        refunded = [r for r in self.results if r["was_refunded"]]
        print(f"\n>> REFUND ECONOMICS:")
        print(f"   Refunded: {len(refunded)} ({len(refunded)/len(self.results)*100:.1f}%)")
        print(f"   Charged: {len(self.results)-len(refunded)} ({(1-len(refunded)/len(self.results))*100:.1f}%)")
        
        # Verdict distribution
        verdicts = {}
        for r in self.results:
            verdicts[r["verdict"]] = verdicts.get(r["verdict"], 0) + 1
        
        print(f"\n>> VERDICT DISTRIBUTION:")
        for verdict, count in sorted(verdicts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {verdict}: {count} ({count/len(self.results)*100:.1f}%)")
        
        # Bucket analysis
        buckets = {}
        for r in self.results:
            bucket = r["bucket"]
            if bucket not in buckets:
                buckets[bucket] = []
            buckets[bucket].append(r)
        
        print(f"\n>> BUCKET PERFORMANCE:")
        for bucket, results in sorted(buckets.items()):
            avg_conf = sum(r["confidence"] for r in results) / len(results)
            refund_pct = len([r for r in results if r["was_refunded"]]) / len(results) * 100
            pre_filtered_pct = len([r for r in results if r["pre_filtered"]]) / len(results) * 100
            
            print(f"   {bucket}:")
            print(f"      Requests: {len(results)}")
            print(f"      Avg Confidence: {avg_conf:.2f}")
            print(f"      Refund Rate: {refund_pct:.1f}%")
            print(f"      Pre-Filtered: {pre_filtered_pct:.1f}%")
        
        print("\n" + "="*80)
    
    def export_csv(self, suffix=""):
        """Export results to CSV"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = Path("logs") / f"conservative_stress{suffix}_{timestamp}.csv"
        
        if not self.results:
            return
        
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.results[0].keys())
            writer.writeheader()
            writer.writerows(self.results)
        
        print(f"\n>> CSV exported: {filepath}")

async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Conservative 1000-request stress test")
    parser.add_argument("--requests", type=int, default=1000, help="Total requests (default: 1000)")
    parser.add_argument("--batch-size", type=int, default=100, help="Batch size (default: 100)")
    parser.add_argument("--max-cost", type=float, default=8.50, help="Stop if Exa cost exceeds this (default: $8.50)")
    
    args = parser.parse_args()
    
    tester = ConservativeStressTester(
        total_requests=args.requests,
        batch_size=args.batch_size
    )
    
    await tester.run_test()

if __name__ == "__main__":
    asyncio.run(main())
