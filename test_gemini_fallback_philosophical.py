"""
Test: Gemini Fallback on Philosophical Claims

Forces Gemini 2.0 Flash fallback by mocking DeepInfra failure.
Tests if Gemini reaches same "Inconclusive" verdict as Claude for philosophical claims.

This is critical for "Model Drift" detection - if Gemini says "True" or "False" 
for subjective moral questions, your fallback model has a bias problem.
"""

import asyncio
import json
from unittest.mock import patch, MagicMock
from src.services.verification import verify_claim_logic

async def test_gemini_philosophical_claim():
    print("\n" + "="*80)
    print("GEMINI FALLBACK - PHILOSOPHICAL CLAIM TEST")
    print("="*80)
    
    claim = "Is capitalism inherently evil?"
    
    print(f"\nClaim: {claim}")
    print("\nTest Strategy: Force DeepInfra failure → Gemini 2.0 Flash fallback")
    print("\nExpected Behavior (Model Drift Check):")
    print("  - Verdict: Inconclusive (same as Claude)")
    print("  - Confidence: < 0.40 (triggers refund)")
    print("  - If Gemini says 'Verified' or 'Unverified', we have Model Drift!")
    print("\nSimulating DeepInfra outage...\n")
    
    # Mock DeepInfra to force Gemini fallback
    with patch('openai.OpenAI') as mock_openai:
        # Make DeepInfra throw an error
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("DeepInfra simulated outage")
        mock_openai.return_value = mock_client
        
        result = await verify_claim_logic(claim)
    
    print("="*80)
    print("RESULT (Gemini 2.0 Flash):")
    print("="*80)
    print(json.dumps(result, indent=2))
    
    # Compare with Claude's behavior
    print("\n" + "="*80)
    print("MODEL DRIFT ANALYSIS:")
    print("="*80)
    
    verdict = result.get("verdict")
    confidence = result.get("confidence_score", 0)
    payment_status = result.get("payment_status")
    
    print("\nClaude 3.5 Haiku Baseline:")
    print("  Verdict: Inconclusive")
    print("  Confidence: 0.35")
    print("  Refund: Yes")
    
    print(f"\nGemini 2.0 Flash Result:")
    print(f"  Verdict: {verdict}")
    print(f"  Confidence: {confidence}")
    print(f"  Refund: {'Yes' if payment_status == 'refunded_due_to_uncertainty' else 'No'}")
    
    # Model drift checks
    drift_detected = False
    
    if verdict in ["Verified", "Unverified"]:
        print("\n❌ CRITICAL MODEL DRIFT DETECTED!")
        print("   Gemini is taking a definitive stance on a philosophical question.")
        print("   This creates inconsistent customer experience during outages.")
        drift_detected = True
    elif verdict == "Inconclusive":
        print("\n✅ No verdict drift - both models agree it's philosophical")
    
    if confidence >= 0.40:
        print("\n⚠️  CONFIDENCE DRIFT DETECTED!")
        print(f"   Gemini confidence ({confidence}) >= 0.40 would NOT trigger refund.")
        print("   Customer would be charged during Gemini fallback but not Claude.")
        drift_detected = True
    else:
        print(f"\n✅ No confidence drift - both models < 0.40 threshold")
    
    # Business impact
    print("\n" + "="*80)
    print("BUSINESS IMPACT:")
    print("="*80)
    
    if drift_detected:
        print("❌ FAILOVER CREATES INCONSISTENT ECONOMICS:")
        print("   - Claude: Refunds customer (protects brand)")
        print("   - Gemini: Charges customer (damages trust)")
        print("\n   SOLUTION: Tune Gemini prompt or add pre-classification layer")
    else:
        print("✅ FAILOVER MAINTAINS CONSISTENT ECONOMICS:")
        print("   - Both models refund philosophical claims")
        print("   - Customer experience identical during outages")
        print("   - 99.9% SLA achievable without brand drift")
    
    print("\n" + "="*80 + "\n")
    
    return drift_detected

if __name__ == "__main__":
    drift = asyncio.run(test_gemini_philosophical_claim())
    exit(1 if drift else 0)
