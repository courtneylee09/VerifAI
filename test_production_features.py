"""
Test the new features in production via HTTP API.
"""
import requests
import json

PROD_URL = "https://verifai-production.up.railway.app"

def test_structured_reasoning():
    """Test structured evidence display via web interface."""
    print("Testing Structured Reasoning")
    print("=" * 60)
    
    # Submit a claim via the verify endpoint
    response = requests.post(
        f"{PROD_URL}/verify",
        data={"claim": "Bitcoin was invented in 2009"},
        headers={"Accept": "text/html"}
    )
    
    if response.status_code == 200:
        html = response.text
        
        # Check for structured evidence sections
        has_evidence_for = "evidence-for" in html or "Supporting Evidence" in html
        has_evidence_against = "evidence-against" in html or "Contradicting Evidence" in html
        has_reasoning = "Reasoning" in html or "reasoning" in html
        
        print(f"✅ Verification successful (Status {response.status_code})")
        print(f"   Supporting Evidence section: {'✅ Found' if has_evidence_for else '❌ Missing'}")
        print(f"   Contradicting Evidence section: {'✅ Found' if has_evidence_against else '❌ Missing'}")
        print(f"   Reasoning section: {'✅ Found' if has_reasoning else '❌ Missing'}")
        
        # Extract verdict from HTML
        if "Verified" in html:
            print(f"   Verdict: ✅ Verified")
        elif "Debunked" in html:
            print(f"   Verdict: ❌ Debunked")
        elif "Inconclusive" in html:
            print(f"   Verdict: ⚠️ Inconclusive")
            
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(response.text[:200])
    
    print("=" * 60)
    print()

def test_batch_verification():
    """Test batch verification endpoint."""
    print("Testing Batch Verification API")
    print("=" * 60)
    
    claims = [
        "The Earth is round",
        "Water boils at 100°C at sea level",
        "The moon landing was faked",
        "Python is a programming language",
        "The sky is green"
    ]
    
    print(f"Submitting {len(claims)} claims...")
    
    try:
        response = requests.post(
            f"{PROD_URL}/verify/batch",
            json={"claims": claims},
            headers={"Content-Type": "application/json"},
            timeout=180  # 3 minutes for batch processing
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Batch processing successful!")
            print(f"\n📊 Summary:")
            print(f"   Total Claims: {result.get('total_claims')}")
            print(f"   Successful: {result.get('successful_verifications')}")
            print(f"   Base Cost: ${result.get('base_cost', 0):.4f}")
            print(f"   Discount: ${result.get('discount_amount', 0):.4f} ({result.get('discount_percent', 0)}%)")
            print(f"   Final Cost: ${result.get('final_cost', 0):.4f}")
            
            print(f"\n📋 Results:")
            for i, res in enumerate(result.get('results', []), 1):
                claim_text = res.get('claim', '')[:50] + "..." if len(res.get('claim', '')) > 50 else res.get('claim', '')
                verdict = res.get('verdict', 'Unknown')
                confidence = res.get('confidence_score', 0)
                
                verdict_icon = "✅" if verdict == "Verified" else "❌" if verdict == "Debunked" else "⚠️"
                print(f"   {i}. {verdict_icon} {claim_text}")
                print(f"      {verdict} ({confidence:.0%} confidence)")
                
                # Check for structured evidence
                has_evidence = bool(res.get('evidence_for') or res.get('evidence_against'))
                print(f"      Structured Evidence: {'✅ Yes' if has_evidence else '❌ No'}")
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(response.text[:500])
            
    except requests.exceptions.Timeout:
        print("⏱️ Request timed out (batch processing takes time)")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("=" * 60)
    print()

if __name__ == "__main__":
    print("🚀 VerifAI Production Feature Test\n")
    print(f"Testing: {PROD_URL}\n")
    
    # Test 1: Structured reasoning
    test_structured_reasoning()
    
    # Test 2: Batch verification
    test_batch_verification()
    
    print("✅ Testing complete!")
