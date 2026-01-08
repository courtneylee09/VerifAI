"""
Test the new structured reasoning and batch verification features.
"""
import asyncio
import json
from src.services.verification import verify_claim_logic

async def test_structured_reasoning():
    """Test that judge provides structured evidence breakdown."""
    print("Testing structured reasoning...")
    print("=" * 60)
    
    result = await verify_claim_logic("Bitcoin was invented in 2009")
    
    print(f"Claim: Bitcoin was invented in 2009")
    print(f"Verdict: {result['verdict']}")
    print(f"Confidence: {result['confidence_score']:.0%}")
    print()
    print(f"Reasoning: {result.get('reasoning', result.get('summary', ''))}")
    print()
    
    if result.get('evidence_for'):
        print("✅ Supporting Evidence:")
        for e in result['evidence_for']:
            print(f"  • {e.get('source')} (weight: {e.get('weight')}x)")
            print(f"    {e.get('point')}")
    
    if result.get('evidence_against'):
        print()
        print("❌ Contradicting Evidence:")
        for e in result['evidence_against']:
            print(f"  • {e.get('source')} (weight: {e.get('weight')}x)")
            print(f"    {e.get('point')}")
    
    print()
    print("=" * 60)
    return result

async def test_batch_verification():
    """Test batch verification with multiple claims."""
    print("\nTesting batch verification...")
    print("=" * 60)
    
    claims = [
        "The Earth is round",
        "Water boils at 100°C",
        "The moon landing was faked"
    ]
    
    print(f"Processing {len(claims)} claims in parallel...")
    
    # Process all claims in parallel (simulating batch endpoint)
    tasks = [verify_claim_logic(claim) for claim in claims]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Calculate batch pricing
    base_cost = len(claims) * 0.05
    successful = sum(1 for r in results if not isinstance(r, Exception) and not r.get('payment_status', '').startswith('refunded'))
    
    # 10% discount for 3+ claims (would be 5+ in production)
    discount_percent = 10  # Normally only for 5+, but testing
    discount_amount = successful * 0.05 * discount_percent / 100
    final_cost = (successful * 0.05) - discount_amount
    
    print(f"\nBatch Summary:")
    print(f"Total Claims: {len(claims)}")
    print(f"Successful: {successful}")
    print(f"Base Cost: ${base_cost:.2f}")
    print(f"Discount: ${discount_amount:.4f} ({discount_percent}%)")
    print(f"Final Cost: ${final_cost:.4f}")
    print()
    
    for i, (claim, result) in enumerate(zip(claims, results), 1):
        if isinstance(result, Exception):
            print(f"{i}. {claim}")
            print(f"   ERROR: {result}")
        else:
            print(f"{i}. {claim}")
            print(f"   Verdict: {result['verdict']} (Confidence: {result['confidence_score']:.0%})")
            print(f"   Evidence For: {len(result.get('evidence_for', []))} points")
            print(f"   Evidence Against: {len(result.get('evidence_against', []))} points")
    
    print("=" * 60)
    return results

if __name__ == "__main__":
    print("VerifAI Feature Test: Structured Reasoning + Batch Verification\n")
    
    # Test 1: Structured reasoning
    asyncio.run(test_structured_reasoning())
    
    # Test 2: Batch verification
    asyncio.run(test_batch_verification())
    
    print("\n✅ All tests complete!")
