#!/usr/bin/env python3
"""Monitor Railway CORS deployment."""
import requests
import time
import sys

SERVICE_URL = "https://verifai-production.up.railway.app"

print("🚀 Monitoring Railway Deployment for CORS Fix")
print("=" * 70)
print("\nWaiting for Railway to rebuild and deploy...")
print("(This typically takes 1-2 minutes)\n")

for i in range(40):  # 10 minutes max
    try:
        # Test CORS headers
        response = requests.get(
            f"{SERVICE_URL}/health",
            headers={"Origin": "https://wallet.coinbase.com"},
            timeout=5
        )
        
        cors_origin = response.headers.get('access-control-allow-origin')
        
        elapsed = (i + 1) * 15
        print(f"[{elapsed}s] ", end="", flush=True)
        
        if cors_origin:
            print(f"✅ CORS DEPLOYED!")
            print("\n" + "=" * 70)
            print("SUCCESS - CORS Headers Active")
            print("=" * 70)
            print(f"\nAllow-Origin: {cors_origin}")
            print(f"Allow-Methods: {response.headers.get('access-control-allow-methods', 'Not set')}")
            print(f"Allow-Headers: {response.headers.get('access-control-allow-headers', 'Not set')}")
            
            print("\n" + "=" * 70)
            print("🎉 Coinbase Wallet Payment Should Work Now!")
            print("=" * 70)
            print("\nTry your payment link again:")
            print("https://verifai-production.up.railway.app/verify?claim=Is%20Jesus%20the%20son%20of%20God%3F")
            print("\nThe 'failed to fetch' error should be RESOLVED.\n")
            sys.exit(0)
        else:
            print("⏳ Building...")
            
    except requests.exceptions.RequestException:
        print(f"[{elapsed}s] ⏳ Deploying...")
    except Exception as e:
        print(f"[{elapsed}s] ⚠️ Error: {str(e)[:40]}")
    
    time.sleep(15)

print("\n⚠️ Deployment taking longer than expected.")
print("Check Railway dashboard: https://railway.app/")
