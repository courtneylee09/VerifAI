"""
Synchronous 1000-Request Stress Test - No Async Issues

Uses synchronous approach to avoid asyncio.CancelledError problems.
Safe for Exa $9 balance with cost tracking and checkpoints.
"""

import time
import csv
import json
from datetime import datetime
from pathlib import Path
import sys

# Run verification synchronously
def run_verification_sync(claim: str) -> dict:
    """Run verification in new event loop to avoid cancellation issues"""
    import asyncio
    from src.services.verification import verify_claim_logic
    
    # Create fresh event loop for each request
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(verify_claim_logic(claim))
        return result
    finally:
        loop.close()

# Test claims
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

def generate_claims(count: int):
    """Generate rotating claims"""
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

def run_stress_test(total_requests=1000, batch_size=100, max_cost=8.50):
    """Run synchronous stress test"""
    
    print("\n" + "="*80)
    print("SYNCHRONOUS 1000-REQUEST STRESS TEST")
    print("="*80)
    print(f"\nTotal Requests: {total_requests}")
    print(f"Batch Size: {batch_size}")
    print(f"Exa Balance: $9.00")
    print(f"Max Spend: ${max_cost}")
    print(f"Strategy: One-at-a-time, 200ms delays (5 req/sec)")
    print("\n" + "="*80 + "\n")
    
    # Generate claims
    all_claims = generate_claims(total_requests)
    results = []
    exa_cost = 0.0
    pre_filtered_count = 0
    start_time = time.time()
    
    # Process sequentially
    for claim_data in all_claims:
        claim_id = claim_data["id"]
        
        try:
            # Run verification
            req_start = time.time()
            result = run_verification_sync(claim_data["claim"])
            latency = time.time() - req_start
            
            # Track costs
            pre_filtered = result.get("pre_filtered", False)
            if pre_filtered:
                pre_filtered_count += 1
                req_exa_cost = 0.0
            else:
                # 1 search + 5 contents = $0.0155
                req_exa_cost = 0.0155
            
            exa_cost += req_exa_cost
            
            # Extract result info
            verdict = result.get("verdict")
            confidence = result.get("confidence_score", 0)
            payment_status = result.get("payment_status", "settled")
            was_refunded = payment_status == "refunded_due_to_uncertainty"
            
            # Save result
            result_data = {
                "claim_id": claim_id,
                "bucket": claim_data["bucket"],
                "claim": claim_data["claim"][:100],
                "verdict": verdict,
                "confidence": confidence,
                "payment_status": payment_status,
                "was_refunded": was_refunded,
                "pre_filtered": pre_filtered,
                "latency_sec": round(latency, 2),
                "exa_cost": round(req_exa_cost, 4),
                "timestamp": datetime.utcnow().isoformat()
            }
            results.append(result_data)
            
            # Progress
            pre = "[PRE-FILTER]" if pre_filtered else ""
            refund = "REFUND" if was_refunded else "CHARGE"
            print(f"[{claim_id}/{total_requests}] {pre} {refund} | {verdict} @ {confidence:.2f} | "
                  f"{latency:.1f}s | Exa: ${req_exa_cost:.4f} | Total: ${exa_cost:.2f}")
            
        except KeyboardInterrupt:
            print(f"\n*** USER STOPPED AT REQUEST {claim_id} ***")
            break
        except Exception as e:
            print(f"[{claim_id}/{total_requests}] ERROR: {e}")
            results.append({
                "claim_id": claim_id,
                "bucket": claim_data["bucket"],
                "claim": claim_data["claim"][:100],
                "verdict": "Error",
                "confidence": 0.0,
                "payment_status": "refunded_due_to_system_error",
                "was_refunded": True,
                "pre_filtered": False,
                "latency_sec": 0,
                "exa_cost": 0.0,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Safety checks
        if exa_cost >= max_cost:
            print(f"\n*** STOPPING: Exa cost ${exa_cost:.2f} >= ${max_cost} limit ***")
            break
        
        # Batch checkpoint
        if claim_id % batch_size == 0:
            export_checkpoint(results, claim_id, exa_cost, pre_filtered_count)
        
        # Respect Exa 5 req/sec limit
        time.sleep(0.2)
    
    # Final summary
    duration = time.time() - start_time
    print_summary(results, duration, exa_cost, pre_filtered_count)
    export_final(results)
    
    return results

def export_checkpoint(results, up_to_id, exa_cost, pre_filtered):
    """Export batch checkpoint"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = Path("logs") / f"sync_stress_checkpoint_{up_to_id}_{timestamp}.csv"
    
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    
    print(f"\n*** CHECKPOINT: {up_to_id} requests | Exa: ${exa_cost:.2f} | Pre-filtered: {pre_filtered} ***\n")

def export_final(results):
    """Export final results"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = Path("logs") / f"sync_stress_final_{timestamp}.csv"
    
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    
    print(f"\nFinal CSV: {filepath}")

def print_summary(results, duration, exa_cost, pre_filtered):
    """Print summary"""
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    if not results:
        print("\nNo results to summarize.")
        return
    
    print(f"\nCompleted: {len(results)} requests")
    print(f"Duration: {duration/60:.1f} minutes ({duration:.0f}s)")
    print(f"Throughput: {len(results)/duration:.2f} req/sec")
    
    print(f"\n>> EXA COSTS:")
    print(f"   Total Cost: ${exa_cost:.2f}")
    print(f"   Remaining Balance: ${9.00-exa_cost:.2f}")
    print(f"   Pre-Filtered (zero cost): {pre_filtered} ({pre_filtered/len(results)*100:.1f}%)")
    
    refunded = [r for r in results if r["was_refunded"]]
    print(f"\n>> REFUNDS:")
    print(f"   Refunded: {len(refunded)} ({len(refunded)/len(results)*100:.1f}%)")
    print(f"   Charged: {len(results)-len(refunded)}")
    
    verdicts = {}
    for r in results:
        verdicts[r["verdict"]] = verdicts.get(r["verdict"], 0) + 1
    
    print(f"\n>> VERDICTS:")
    for v, c in sorted(verdicts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {v}: {c} ({c/len(results)*100:.1f}%)")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--requests", type=int, default=1000)
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--max-cost", type=float, default=8.50)
    args = parser.parse_args()
    
    run_stress_test(args.requests, args.batch_size, args.max_cost)
