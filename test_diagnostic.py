"""
Diagnostic test to check what's causing Error verdicts in batch processing.
This will test single claims one at a time to isolate the issue.
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
except ImportError:
    print("Installing required packages...")
    os.system("pip install httpx eth-account")
    import httpx
    from eth_account import Account

# Payment configuration
MERCHANT_ADDRESS = "0x3615af0cE7c8e525B9a9C6cE281e195442596559"
USDC_CONTRACT = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
NETWORK = "base-sepolia"
AMOUNT = "50000"  # 0.05 USDC
API_URL = "https://verifai-production.up.railway.app"
CHAIN_ID = 84532


def create_payment_header(account: Account) -> str:
    """Create the EIP-712 signed X-PAYMENT header."""
    nonce = secrets.token_bytes(32)
    valid_after = int(time.time()) - 60
    valid_before = int(time.time()) + 60
    
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
        "value": int(AMOUNT),
        "validAfter": valid_after,
        "validBefore": valid_before,
        "nonce": nonce,
    }
    
    signed_message = account.sign_typed_data(
        domain_data=domain_data,
        message_types=message_types,
        message_data=message_data,
    )
    
    signature = signed_message.signature.hex()
    if not signature.startswith("0x"):
        signature = f"0x{signature}"

    payment_header = {
        "x402Version": 1,
        "scheme": "exact",
        "network": NETWORK,
        "payload": {
            "signature": signature,
            "authorization": {
                "from": account.address,
                "to": MERCHANT_ADDRESS,
                "value": AMOUNT,
                "validAfter": str(valid_after),
                "validBefore": str(valid_before),
                "nonce": f"0x{nonce.hex()}",
            },
        },
    }
    
    json_str = json.dumps(payment_header)
    b64_encoded = base64.b64encode(json_str.encode()).decode()
    return b64_encoded


async def test_single_claim(account: Account, claim: str):
    """Test a single claim and return detailed diagnostics."""
    print(f"\n{'='*70}")
    print(f"Testing: {claim}")
    print(f"{'='*70}")
    
    payment_header = create_payment_header(account)
    headers = {"X-PAYMENT": payment_header}
    params = {"claim": claim}
    
    async with httpx.AsyncClient(timeout=180.0) as client:
        try:
            start_time = time.time()
            response = await client.get(f"{API_URL}/verify", params=params, headers=headers)
            elapsed = time.time() - start_time
            
            print(f"Status: {response.status_code}")
            print(f"Time: {elapsed:.2f}s")
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"\n✅ Response received:")
                print(f"   Verdict: {result.get('verdict')}")
                print(f"   Confidence: {result.get('confidence_score', 0):.2%}")
                print(f"   Payment Status: {result.get('payment_status', 'N/A')}")
                
                # Check for error verdict
                if result.get('verdict') == 'Error':
                    print(f"\n⚠️ ERROR VERDICT DETECTED!")
                    print(f"   Reason: {result.get('reason', 'No reason provided')}")
                    print(f"   Summary: {result.get('summary', 'No summary')}")
                    print(f"   Audit Trail: {result.get('audit_trail', 'No audit trail')}")
                
                # Check for new structured fields
                print(f"\n📊 Structured Evidence Check:")
                print(f"   Has evidence_for: {bool(result.get('evidence_for'))}")
                print(f"   Has evidence_against: {bool(result.get('evidence_against'))}")
                print(f"   Has reasoning: {bool(result.get('reasoning'))}")
                
                if result.get('evidence_for'):
                    print(f"   Evidence For Count: {len(result['evidence_for'])}")
                if result.get('evidence_against'):
                    print(f"   Evidence Against Count: {len(result['evidence_against'])}")
                
                # Show full JSON for debugging
                print(f"\n📄 Full Response:")
                print(json.dumps(result, indent=2)[:1000] + "...")
                
                return result
                
            else:
                print(f"\n❌ Request failed: {response.status_code}")
                print(response.text[:500])
                return None
                
        except Exception as e:
            print(f"\n❌ Exception: {e}")
            import traceback
            traceback.print_exc()
            return None


async def main():
    print("🔍 VerifAI Diagnostic Test")
    print("="*70)
    
    # Get private key
    private_key = os.getenv("BUYER_PRIVATE_KEY")
    if len(sys.argv) > 1:
        private_key = sys.argv[1]
    
    if not private_key:
        print("\n❌ Error: No private key provided")
        print('Run: $env:BUYER_PRIVATE_KEY = "0x..."; python test_diagnostic.py')
        sys.exit(1)
    
    try:
        account = Account.from_key(private_key)
        print(f"Wallet: {account.address}\n")
    except Exception as e:
        print(f"❌ Invalid private key: {e}")
        sys.exit(1)
    
    # Test just one simple claim first
    test_claims = [
        "The Earth is round",
    ]
    
    results = []
    for claim in test_claims:
        result = await test_single_claim(account, claim)
        results.append(result)
        await asyncio.sleep(2)  # Wait between tests
    
    # Summary
    print(f"\n{'='*70}")
    print("DIAGNOSTIC SUMMARY")
    print(f"{'='*70}")
    
    error_count = sum(1 for r in results if r and r.get('verdict') == 'Error')
    success_count = sum(1 for r in results if r and r.get('verdict') != 'Error')
    
    print(f"Total Tests: {len(results)}")
    print(f"Success: {success_count}")
    print(f"Errors: {error_count}")
    
    if error_count > 0:
        print(f"\n⚠️ ERRORS DETECTED - Checking common causes:")
        for i, result in enumerate(results):
            if result and result.get('verdict') == 'Error':
                print(f"\nClaim {i+1}: {test_claims[i]}")
                print(f"  Error: {result.get('reason', 'Unknown')}")
                print(f"  Details: {result.get('audit_trail', 'No details')}")


if __name__ == "__main__":
    asyncio.run(main())
