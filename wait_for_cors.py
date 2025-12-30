#!/usr/bin/env python3
"""Wait for Railway deployment and test CORS headers."""

import requests
import time
import sys

SERVICE_URL = "https://verifai-production.up.railway.app"

print("Waiting for Railway to redeploy with CORS fix...")
print("This usually takes 1-2 minutes.\n")

for i in range(30):  # Wait up to 5 minutes
    try:
        print(f"[{i+1}/30] Checking deployment...", end=" ")
        
        # Make an OPTIONS request to check CORS headers
        response = requests.options(
            f"{SERVICE_URL}/verify",
            headers={
                "Origin": "https://wallet.coinbase.com",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "x-payment"
            },
            timeout=5
        )
        
        # Check if CORS headers are present
        cors_headers = {
            'access-control-allow-origin': response.headers.get('access-control-allow-origin'),
            'access-control-allow-methods': response.headers.get('access-control-allow-methods'),
            'access-control-allow-headers': response.headers.get('access-control-allow-headers'),
        }
        
        if cors_headers['access-control-allow-origin']:
            print("✅ CORS ENABLED!")
            print("\n" + "=" * 70)
            print("CORS Headers:")
            print("=" * 70)
            for header, value in cors_headers.items():
                if value:
                    print(f"  {header}: {value}")
            
            print("\n" + "=" * 70)
            print("✅ Deployment Complete - Coinbase Wallet Should Work Now!")
            print("=" * 70)
            print(f"\nTry the payment link again:")
            print(f"https://verifai-production.up.railway.app/verify?claim=Is%20Jesus%20the%20son%20of%20God%3F")
            print("\nThe 'failed to fetch' error should be resolved.\n")
            sys.exit(0)
        else:
            print("⏳ Still deploying...")
            
    except Exception as e:
        print(f"⏳ Waiting... ({str(e)[:30]})")
    
    time.sleep(10)

print("\n❌ Timeout waiting for deployment. Check Railway dashboard manually.")
