"""
Test: Philosophical/Normative Claim Detection

Tests whether the Judge correctly identifies "Is capitalism inherently evil?" 
as a philosophical claim and triggers automatic refund logic.

Expected Outcome:
- Verdict: "Inconclusive"
- Confidence: < 0.40 (triggers automatic refund)
- payment_status: "refunded_due_to_uncertainty"
"""

import asyncio
import json
from src.services.verification import verify_claim_logic

async def test_philosophical_claim():
    print("\n" + "="*80)
    print("PHILOSOPHICAL CLAIM DETECTION TEST")
    print("="*80)
    
    claim = "Is capitalism inherently evil?"
    
    print(f"\nClaim: {claim}")
    print("\nExpected Behavior:")
    print("  - Verdict: Inconclusive")
    print("  - Confidence: < 0.40")
    print("  - payment_status: refunded_due_to_uncertainty")
    print("\nProcessing...\n")
    
    result = await verify_claim_logic(claim)
    
    print("="*80)
    print("RESULT:")
    print("="*80)
    print(json.dumps(result, indent=2))
    
    # Validate refund logic
    print("\n" + "="*80)
    print("VALIDATION:")
    print("="*80)
    
    verdict = result.get("verdict")
    confidence = result.get("confidence_score", 0)
    payment_status = result.get("payment_status")
    
    checks = {
        "Is verdict 'Inconclusive'?": verdict == "Inconclusive",
        "Is confidence < 0.40 (refund threshold)?": confidence < 0.40,
        "Is payment_status 'refunded_due_to_uncertainty'?": payment_status == "refunded_due_to_uncertainty",
        "Would customer be charged?": payment_status == "settled"
    }
    
    for check, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {check}")
    
    # Business impact
    print("\n" + "="*80)
    print("BUSINESS IMPACT:")
    print("="*80)
    
    if payment_status == "refunded_due_to_uncertainty":
        print("✅ Customer NOT charged for philosophical debate")
        print("✅ Brand integrity protected (not taking sides on moral questions)")
        print("✅ LLM cost absorbed (~$0.004) as insurance for trust")
        print("✅ Customer Lifetime Value preserved")
    else:
        print("❌ CRITICAL: Customer would be charged $0.05 for subjective opinion!")
        print("❌ This damages VerifAI's 'Truth Settlement Layer' positioning")
        print("❌ Risk: Customer perceives service as biased/unreliable")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(test_philosophical_claim())
