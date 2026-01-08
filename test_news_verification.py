"""
Test the new /verify/news endpoint with real-time news verification.

Usage:
    $env:BUYER_PRIVATE_KEY = "0x..."
    $env:NEWSAPI_KEY = "your_newsapi_key"  # Optional, falls back to Exa
    python test_news_verification.py
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


async def test_news_verification(account: Account):
    """Test the /verify/news endpoint with breaking news claims."""
    print("\n" + "="*70)
    print("NEWS VERIFICATION TEST")
    print("="*70)
    
    # Test claims (mix of recent news and evergreen topics)
    test_claims = [
        "OpenAI released GPT-5 this week",  # Recent tech news (may be false)
        "Bitcoin price reached new all-time high today",  # Financial news
        "NASA announced new Mars mission",  # Space news
    ]
    
    print(f"\nTesting {len(test_claims)} news claims...\n")
    
    for i, claim in enumerate(test_claims, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}/{len(test_claims)}: {claim}")
        print(f"{'='*70}")
        
        payment_header = create_payment_header(account)
        headers = {"X-PAYMENT": payment_header}
        params = {"claim": claim}
        
        async with httpx.AsyncClient(timeout=180.0) as client:
            try:
                start_time = time.time()
                response = await client.get(
                    f"{API_URL}/verify/news",
                    params=params,
                    headers=headers
                )
                elapsed = time.time() - start_time
                
                print(f"\nStatus: {response.status_code}")
                print(f"Time: {elapsed:.2f}s")
                
                if response.status_code == 200:
                    result = response.json()
                    
                    print(f"\n✅ Verdict: {result.get('verdict')}")
                    print(f"   Confidence: {result.get('confidence_score', 0):.0%}")
                    print(f"   Claim Type: {result.get('claim_type')}")
                    
                    # News-specific fields
                    if result.get('newest_source_age_hours') is not None:
                        print(f"   🔴 Newest Source: {result['newest_source_age_hours']}h ago")
                    
                    # Show sources with timestamps
                    if result.get('sources'):
                        print(f"\n   📰 Sources ({len(result['sources'])}):")
                        for s in result['sources'][:3]:  # Show first 3
                            age = f"{s['age_hours']}h ago" if s.get('age_hours') else "Unknown age"
                            weight = s.get('weight', 1.0)
                            print(f"      • {age} (weight: {weight:.1f}x)")
                            print(f"        {s['url'][:60]}...")
                    
                    # Show evidence
                    if result.get('evidence_for'):
                        print(f"\n   ✅ Supporting: {len(result['evidence_for'])} points")
                    if result.get('evidence_against'):
                        print(f"   ❌ Contradicting: {len(result['evidence_against'])} points")
                    
                    # Payment status
                    print(f"\n   💰 Payment: {result.get('payment_status', 'N/A')}")
                    
                else:
                    print(f"\n❌ Request failed: {response.status_code}")
                    print(response.text[:500])
                
            except Exception as e:
                print(f"\n❌ Error: {e}")
        
        # Wait between tests
        if i < len(test_claims):
            await asyncio.sleep(2)
    
    print(f"\n{'='*70}")
    print("All news verification tests complete!")
    print(f"{'='*70}\n")


def main():
    print("🔴 VerifAI News Verification Test")
    print("="*70)
    
    # Check for NewsAPI key (optional)
    newsapi_key = os.getenv("NEWSAPI_KEY")
    if newsapi_key:
        print("✅ NEWSAPI_KEY found - will use real-time news sources")
    else:
        print("⚠️ NEWSAPI_KEY not set - will fall back to Exa search")
        print("   Get free key at: https://newsapi.org/\n")
    
    # Get private key
    private_key = os.getenv("BUYER_PRIVATE_KEY")
    if len(sys.argv) > 1:
        private_key = sys.argv[1]
    
    if not private_key:
        print("\n❌ Error: No private key provided")
        print('Run: $env:BUYER_PRIVATE_KEY = "0x..."; python test_news_verification.py')
        sys.exit(1)
    
    try:
        account = Account.from_key(private_key)
        print(f"Wallet: {account.address}\n")
    except Exception as e:
        print(f"❌ Invalid private key: {e}")
        sys.exit(1)
    
    asyncio.run(test_news_verification(account))


if __name__ == "__main__":
    main()
