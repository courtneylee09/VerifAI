"""
Test the new structured reasoning and batch verification features with x402 payment.

Usage:
    $env:BUYER_PRIVATE_KEY = "0x..."
    python test_new_features_paid.py
"""

import asyncio
import base64
import json
import os
import sys
import time
import secrets

try:
    import httpx
    from eth_account import Account
    from eth_account.messages import encode_typed_data
except ImportError:
    print("Installing required packages...")
    os.system("pip install httpx eth-account")
    import httpx
    from eth_account import Account
    from eth_account.messages import encode_typed_data

# Payment configuration
MERCHANT_ADDRESS = "0x3615af0cE7c8e525B9a9C6cE281e195442596559"
USDC_CONTRACT = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
NETWORK = "base-sepolia"
SINGLE_AMOUNT = "50000"  # 0.05 USDC (6 decimals)
API_URL = "https://verifai-production.up.railway.app"
CHAIN_ID = 84532  # Base Sepolia


def create_payment_header(account: Account, amount: str = SINGLE_AMOUNT) -> str:
    """Create the EIP-712 signed X-PAYMENT header."""
    nonce = secrets.token_bytes(32)
    valid_after = int(time.time()) - 60
    valid_before = int(time.time()) + 60
    
    # EIP-712 domain and message types for USDC transferWithAuthorization
    domain_data = {
        "name": "USDC",
        "version": "2",
        "chainId": CHAIN_ID,
        "verifyingContract": USDC_CONTRACT,
    }
    
    message_types = {
        "TransferWithAuthorization": [
            {"name": "from", "type": "address"},
            {"name": "to", "type": "address"},
            {"name": "value", "type": "uint256"},
            {"name": "validAfter", "type": "uint256"},
            {"name": "validBefore", "type": "uint256"},
            {"name": "nonce", "type": "bytes32"},
        ]
    }
    
    message_data = {
        "from": account.address,
        "to": MERCHANT_ADDRESS,
        "value": int(amount),
        "validAfter": valid_after,
        "validBefore": valid_before,
        "nonce": nonce,
    }
    
    # Sign the typed data
    signed_message = account.sign_typed_data(
        domain_data=domain_data,
        message_types=message_types,
        message_data=message_data,
    )
    
    signature = signed_message.signature.hex()
    if not signature.startswith("0x"):
        signature = f"0x{signature}"

    # Construct the payment header
    payment_header = {
        "x402Version": 1,
        "scheme": "exact",
        "network": NETWORK,
        "payload": {
            "signature": signature,
            "authorization": {
                "from": account.address,
                "to": MERCHANT_ADDRESS,
                "value": amount,
                "validAfter": str(valid_after),
                "validBefore": str(valid_before),
                "nonce": f"0x{nonce.hex()}",
            },
        },
    }
    
    json_str = json.dumps(payment_header)
    b64_encoded = base64.b64encode(json_str.encode()).decode()
    return b64_encoded


async def test_structured_reasoning(account: Account):
    """Test the structured reasoning feature with payment."""
    print("\n" + "="*70)
    print("TEST 1: Structured Judge Reasoning")
    print("="*70)
    
    claim = "Bitcoin was invented in 2009"
    print(f"\nClaim: {claim}")
    print(f"Wallet: {account.address}")
    print(f"Cost: $0.05 USDC\n")
    
    payment_header = create_payment_header(account)
    headers = {"X-PAYMENT": payment_header}
    params = {"claim": claim}
    
    async with httpx.AsyncClient(timeout=180.0) as client:
        try:
            print("Sending request...")
            response = await client.get(f"{API_URL}/verify", params=params, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                
                print("\n✅ SUCCESS! Structured evidence received:\n")
                print(f"Verdict: {result['verdict']}")
                print(f"Confidence: {result['confidence_score']:.0%}")
                print(f"\n📊 Judge's Reasoning:")
                print(f"{result.get('reasoning', result.get('summary', ''))[:300]}...")
                
                # Check for new structured fields
                if result.get('evidence_for'):
                    print(f"\n✅ Supporting Evidence ({len(result['evidence_for'])} points):")
                    total_weight = sum(e.get('weight', 1.0) for e in result['evidence_for'])
                    print(f"   Total Weight: {total_weight:.1f}")
                    for i, e in enumerate(result['evidence_for'][:3], 1):
                        print(f"   {i}. [{e.get('source', 'Unknown')}] (weight: {e.get('weight', 1.0)}x)")
                        print(f"      {e.get('point', '')[:100]}...")
                else:
                    print("\n⚠️ No evidence_for field found")
                
                if result.get('evidence_against'):
                    print(f"\n❌ Contradicting Evidence ({len(result['evidence_against'])} points):")
                    total_weight = sum(e.get('weight', 1.0) for e in result['evidence_against'])
                    print(f"   Total Weight: {total_weight:.1f}")
                    for i, e in enumerate(result['evidence_against'][:3], 1):
                        print(f"   {i}. [{e.get('source', 'Unknown')}] (weight: {e.get('weight', 1.0)}x)")
                        print(f"      {e.get('point', '')[:100]}...")
                else:
                    print("\n✅ No contradicting evidence found")
                
                print(f"\n📈 Performance:")
                print(f"   Execution time: {result.get('execution_time_seconds', 0):.2f}s")
                print(f"   Total cost: ${result.get('total_cost_usd', 0):.4f}")
                
                return True
                
            else:
                print(f"\n❌ Request failed: {response.status_code}")
                print(response.text[:500])
                return False
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            return False


async def test_batch_verification(account: Account):
    """Test the batch verification feature with payment."""
    print("\n" + "="*70)
    print("TEST 2: Batch Verification with Bulk Discount")
    print("="*70)
    
    claims = [
        "The Earth is round",
        "Water boils at 100°C at sea level",
        "The moon landing was faked",
        "Python is a programming language",
        "The Great Wall of China is visible from space"
    ]
    
    print(f"\nClaims to verify: {len(claims)}")
    for i, claim in enumerate(claims, 1):
        print(f"   {i}. {claim}")
    
    # Calculate expected cost (5 claims = 10% discount)
    expected_base = len(claims) * 0.05
    expected_discount = 10  # 10% for 5+ claims
    expected_final = expected_base * (1 - expected_discount/100)
    
    print(f"\nExpected pricing:")
    print(f"   Base cost: ${expected_base:.2f}")
    print(f"   Discount: {expected_discount}%")
    print(f"   Final cost: ${expected_final:.4f}")
    
    # For batch, we need to calculate the total amount for payment
    # 5 claims with 10% discount = $0.225
    batch_amount = str(int(expected_final * 1_000_000))  # Convert to USDC units (6 decimals)
    
    payment_header = create_payment_header(account, batch_amount)
    headers = {
        "X-PAYMENT": payment_header,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            print(f"\nSending batch request...")
            response = await client.post(
                f"{API_URL}/verify/batch",
                json={"claims": claims},
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print("\n✅ SUCCESS! Batch verification complete:\n")
                print(f"📊 Summary:")
                print(f"   Total claims: {result.get('total_claims')}")
                print(f"   Successful: {result.get('successful_verifications')}")
                print(f"   Base cost: ${result.get('base_cost', 0):.4f}")
                print(f"   Discount: {result.get('discount_percent', 0)}% (${result.get('discount_amount', 0):.4f})")
                print(f"   Final cost: ${result.get('final_cost', 0):.4f}")
                
                print(f"\n📋 Results:")
                for i, res in enumerate(result.get('results', []), 1):
                    verdict_icon = "✅" if res['verdict'] == "Verified" else "❌" if res['verdict'] == "Debunked" else "⚠️"
                    print(f"\n   {i}. {verdict_icon} {res['claim'][:50]}...")
                    print(f"      Verdict: {res['verdict']} ({res['confidence_score']:.0%})")
                    
                    # Check for structured evidence in batch results
                    if res.get('evidence_for'):
                        print(f"      Supporting: {len(res['evidence_for'])} points (weight: {sum(e.get('weight', 1) for e in res['evidence_for']):.1f})")
                    if res.get('evidence_against'):
                        print(f"      Contradicting: {len(res['evidence_against'])} points (weight: {sum(e.get('weight', 1) for e in res['evidence_against']):.1f})")
                
                # Verify savings
                savings = result.get('discount_amount', 0)
                if savings > 0:
                    print(f"\n💰 You saved ${savings:.4f} with bulk pricing!")
                
                return True
                
            else:
                print(f"\n❌ Request failed: {response.status_code}")
                print(response.text[:500])
                return False
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    print("🚀 VerifAI New Features Test (with x402 Payment)")
    print("="*70)
    
    # Get private key
    private_key = os.getenv("BUYER_PRIVATE_KEY")
    if len(sys.argv) > 1:
        private_key = sys.argv[1]
    
    if not private_key:
        print("\n❌ Error: No private key provided")
        print("\nSteps to test:")
        print("1. Export your test wallet's private key from Coinbase Wallet")
        print("2. Make sure you have at least 0.30 USDC on Base Sepolia")
        print(f"   USDC contract: {USDC_CONTRACT}")
        print("\n3. Run:")
        print('   $env:BUYER_PRIVATE_KEY = "0x..."')
        print(f'   python {sys.argv[0]}')
        sys.exit(1)
    
    # Create account
    try:
        account = Account.from_key(private_key)
        print(f"\nWallet loaded: {account.address}")
        print(f"Network: Base Sepolia")
        print(f"Merchant: {MERCHANT_ADDRESS}")
    except Exception as e:
        print(f"\n❌ Invalid private key: {e}")
        sys.exit(1)
    
    # Run tests
    async def run_tests():
        test1_passed = await test_structured_reasoning(account)
        test2_passed = await test_batch_verification(account)
        
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Structured Reasoning: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
        print(f"Batch Verification:   {'✅ PASSED' if test2_passed else '❌ FAILED'}")
        print("="*70)
        
        if test1_passed and test2_passed:
            print("\n🎉 All tests passed! New features are working perfectly.")
        else:
            print("\n⚠️ Some tests failed. Check the output above for details.")
    
    asyncio.run(run_tests())


if __name__ == "__main__":
    main()
