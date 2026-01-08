"""
Simple Sequential Stress Test - Avoids Rate Limiting

Runs requests one at a time to:
1. Avoid Exa API rate limits
2. Get clean results for refund analysis
3. Test philosophical claim detection
"""

import asyncio
import csv
import json
from datetime import datetime
from pathlib import Path

from src.services.verification import verify_claim_logic

# Test claims focusing on philosophical detection
TEST_CLAIMS = [
    ("Is capitalism inherently evil?", "Adversarial"),
    ("Are all politicians corrupt?", "Adversarial"),
    ("Does religion cause more harm than good?", "Adversarial"),
    ("Is democracy a failed system?", "Adversarial"),
    ("Are all billionaires exploiting workers?", "Adversarial"),
    ("Is water wet?", "Ambiguous"),
    ("Does pineapple belong on pizza?", "Ambiguous"),
    ("Is a hot dog a sandwich?", "Ambiguous"),
    ("Will quantum computers break Bitcoin's encryption within 5 years?", "Technical"),
    ("Is Rust memory-safe without garbage collection?", "Technical"),
]

async def run_sequential_test():
    print("\n" + "="*80)
    print("SEQUENTIAL STRESS TEST - REFUND SYSTEM VALIDATION")
    print("="*80)
    print(f"\nTotal Claims: {len(TEST_CLAIMS)}")
    print("Strategy: One request at a time to avoid rate limits\n")
    print("="*80 + "\n")
    
    results = []
    
    for i, (claim, bucket) in enumerate(TEST_CLAIMS, 1):
        print(f"\n[{i}/{len(TEST_CLAIMS)}] Testing: {claim[:60]}...")
        
        try:
            result = await verify_claim_logic(claim)
            
            verdict = result.get("verdict")
            confidence = result.get("confidence_score", 0)
            payment_status = result.get("payment_status", "settled")
            was_refunded = payment_status == "refunded_due_to_uncertainty"
            
            results.append({
                "claim_id": i,
                "bucket": bucket,
                "claim": claim,
                "verdict": verdict,
                "confidence": confidence,
                "payment_status": payment_status,
                "was_refunded": was_refunded,
                "manual_review": result.get("manual_review", False)
            })
            
            refund_icon = "💸 REFUNDED" if was_refunded else "💰 CHARGED"
            print(f"    {refund_icon} | Verdict: {verdict} | Confidence: {confidence:.2f}")
            
        except Exception as e:
            print(f"    ❌ ERROR: {e}")
            results.append({
                "claim_id": i,
                "bucket": bucket,
                "claim": claim,
                "verdict": "Error",
                "confidence": 0.0,
                "payment_status": "refunded_due_to_system_error",
                "was_refunded": True,
                "error": str(e)
            })
        
        # Small delay between requests
        await asyncio.sleep(1.5)
    
    # Generate summary
    print("\n" + "="*80)
    print("TEST RESULTS SUMMARY")
    print("="*80)
    
    total = len(results)
    refunded = [r for r in results if r["was_refunded"]]
    refund_rate = len(refunded) / total * 100
    
    print(f"\nTotal Requests: {total}")
    print(f"Refunded: {len(refunded)} ({refund_rate:.1f}%)")
    print(f"Charged: {total - len(refunded)} ({100-refund_rate:.1f}%)")
    
    # Philosophical claim analysis
    philosophical_claims = [
        r for r in results 
        if any(word in r["claim"].lower() for word in ["inherently evil", "corrupt", "failed system", "exploiting"])
    ]
    
    if philosophical_claims:
        print(f"\n>> PHILOSOPHICAL CLAIMS:")
        for r in philosophical_claims:
            status = "✓ REFUNDED" if r["was_refunded"] else "✗ CHARGED (SHOULD BE REFUNDED!)"
            print(f"   {status} | {r['claim'][:50]}... | Confidence: {r['confidence']:.2f}")
    
    # Bucket breakdown
    print(f"\n>> BY BUCKET:")
    buckets = {}
    for r in results:
        bucket = r["bucket"]
        if bucket not in buckets:
            buckets[bucket] = []
        buckets[bucket].append(r)
    
    for bucket, bucket_results in buckets.items():
        avg_conf = sum(r["confidence"] for r in bucket_results) / len(bucket_results)
        refund_pct = len([r for r in bucket_results if r["was_refunded"]]) / len(bucket_results) * 100
        print(f"   {bucket}: Avg Confidence={avg_conf:.2f}, Refund Rate={refund_pct:.0f}%")
    
    # Export CSV
    filepath = Path("logs") / f"sequential_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n>> CSV exported to: {filepath}")
    print("\n" + "="*80 + "\n")
    
    return results

if __name__ == "__main__":
    asyncio.run(run_sequential_test())
