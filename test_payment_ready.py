#!/usr/bin/env python3
"""Simple CORS and payment test for Railway."""

import requests

SERVICE_URL = "https://verifai-production.up.railway.app"
CLAIM = "Is Jesus the son of God?"

print("=" * 70)
print("VerifAI Payment Test")
print("=" * 70)

# Test 1: Check CORS with OPTIONS request
print("\n1️⃣ Testing CORS Configuration...")
try:
    response = requests.options(
        f"{SERVICE_URL}/verify",
        headers={
            "Origin": "https://wallet.coinbase.com",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "x-payment"
        },
        timeout=10
    )
    
    cors_origin = response.headers.get('Access-Control-Allow-Origin', 'Not Set')
    cors_methods = response.headers.get('Access-Control-Allow-Methods', 'Not Set')
    cors_headers = response.headers.get('Access-Control-Allow-Headers', 'Not Set')
    
    print(f"   Status: {response.status_code}")
    print(f"   Allow-Origin: {cors_origin}")
    print(f"   Allow-Methods: {cors_methods}")
    print(f"   Allow-Headers: {cors_headers}")
    
    if cors_origin != 'Not Set':
        print("\n   ✅ CORS is ENABLED - Coinbase Wallet should work!")
    else:
        print("\n   ⏳ CORS not ready yet - Railway may still be deploying")
        
except Exception as e:
    print(f"   ⚠️ Could not test CORS: {e}")

# Test 2: Get payment details
print("\n2️⃣ Getting Payment Information...")
try:
    response = requests.get(
        f"{SERVICE_URL}/verify",
        params={"claim": CLAIM},
        timeout=10
    )
    
    if response.status_code == 402:
        print("   Status: 402 Payment Required ✅")
        data = response.json()
        
        if 'accepts' in data and len(data['accepts']) > 0:
            payment = data['accepts'][0]
            
            print("\n" + "=" * 70)
            print("💳 PAYMENT DETAILS")
            print("=" * 70)
            print(f"\n   Amount: {int(payment.get('maxAmountRequired', 0))/1e6} USDC")
            print(f"   Network: {payment.get('network')}")
            print(f"   Pay To: {payment.get('payTo')}")
            print(f"   Asset: {payment.get('asset')}")
            
            print("\n" + "=" * 70)
            print("🌐 PAYMENT LINK FOR COINBASE WALLET")
            print("=" * 70)
            
            encoded_claim = requests.utils.quote(CLAIM)
            payment_url = f"{SERVICE_URL}/verify?claim={encoded_claim}"
            
            print(f"\n   {payment_url}")
            
            print("\n" + "=" * 70)
            print("📱 HOW TO PAY WITH COINBASE WALLET")
            print("=" * 70)
            print("""
   1. Open Coinbase Wallet browser or app
   2. Navigate to the payment URL above
   3. Wallet will detect the x402 payment request
   4. Approve the 0.05 USDC transaction
   5. View your verification results!
            """)
            
            print("=" * 70)
            print("🔧 TROUBLESHOOTING")
            print("=" * 70)
            print("""
   If you still see "failed to fetch":
   - Wait 1-2 more minutes for Railway to fully deploy
   - Clear browser cache and try again
   - Make sure you're on Base Sepolia testnet
   - Check that you have testnet USDC
            """)
            
    else:
        print(f"   Unexpected status: {response.status_code}")
        
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 70)
