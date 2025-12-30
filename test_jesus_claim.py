#!/usr/bin/env python3
"""
Test VerifAI with x402 payment on Railway.
Claim: "Is Jesus the son of God?"
"""

import requests
import json

# Railway service URL
SERVICE_URL = "https://verifai-production.up.railway.app"

# Your claim
CLAIM = "Is Jesus the son of God?"

print("=" * 70)
print("VerifAI x402 Payment Test")
print("=" * 70)
print(f"\nClaim: {CLAIM}")
print(f"Service: {SERVICE_URL}")
print(f"Price: 0.05 USDC on Base Sepolia\n")

# Step 1: Make initial request (will get 402 Payment Required)
print("Step 1: Making request to verify endpoint...")
print("-" * 70)

try:
    response = requests.get(
        f"{SERVICE_URL}/verify",
        params={"claim": CLAIM},
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 402:
        print("\n✅ Payment Required (as expected)")
        print("\n📋 Payment Details:")
        data = response.json()
        
        # Extract payment info
        if 'accepts' in data and len(data['accepts']) > 0:
            payment_info = data['accepts'][0]
            
            print(f"   Pay To Address: {payment_info.get('payTo')}")
            print(f"   Amount Required: {int(payment_info.get('maxAmountRequired', 0))/1e6} USDC")
            print(f"   Network: {payment_info.get('network')}")
            print(f"   Asset: {payment_info.get('asset')}")
            
            print("\n" + "=" * 70)
            print("🔗 PAYMENT LINK")
            print("=" * 70)
            
            # Create payment URL
            payment_url = f"{SERVICE_URL}/verify?claim={requests.utils.quote(CLAIM)}"
            
            print(f"\n1. Visit this URL in a browser with x402 wallet extension:")
            print(f"\n   {payment_url}")
            
            print(f"\n2. Or use Base Sepolia testnet to send:")
            print(f"   • Amount: 0.05 USDC")
            print(f"   • To Address: {payment_info.get('payTo')}")
            print(f"   • Network: Base Sepolia")
            print(f"   • USDC Contract: {payment_info.get('asset')}")
            
            print("\n" + "=" * 70)
            print("💡 HOW TO PAY")
            print("=" * 70)
            print("""
Option 1 - Use x402 Browser Extension (Recommended):
   1. Install an x402-compatible wallet extension
   2. Open the payment URL above in your browser
   3. Approve the payment in the wallet popup
   4. View your verification results

Option 2 - Manual Payment via Base Sepolia:
   1. Get Base Sepolia testnet USDC from faucet
   2. Send 0.05 USDC to the payment address
   3. Include the transaction hash in X-PAYMENT header
   4. Make the API request with the payment proof

Option 3 - Test Locally Without Payment:
   1. Clone the repository
   2. Run: python tests/test_direct.py
   3. This bypasses the payment wall for testing
            """)
            
            print("=" * 70)
            print("🌐 ALTERNATIVE: Test Without Payment")
            print("=" * 70)
            print(f"\nTo test the verification logic without payment:")
            print(f"   python tests/test_direct.py")
            print(f"\nThis will verify the claim: '{CLAIM}'")
            print(f"directly without requiring payment.\n")
            
    elif response.status_code == 200:
        print("✅ SUCCESS! Result received:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Unexpected status: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")

print("=" * 70)
