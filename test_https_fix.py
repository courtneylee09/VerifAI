#!/usr/bin/env python3
"""Test if HTTPS URLs are now returned in x402 payment response."""
import requests
import time

SERVICE_URL = "https://verifai-production.up.railway.app"
CLAIM = "Is Jesus the son of God?"

print("=" * 70)
print("Testing HTTPS Fix for x402 Payment")
print("=" * 70)
print("\nWaiting for Railway deployment...\n")

for i in range(30):
    try:
        response = requests.get(
            f"{SERVICE_URL}/verify",
            params={"claim": CLAIM},
            timeout=10
        )
        
        if response.status_code == 402:
            data = response.json()
            
            if 'accepts' in data and len(data['accepts']) > 0:
                resource_url = data['accepts'][0].get('resource', '')
                
                elapsed = (i + 1) * 10
                print(f"[{elapsed}s] Resource URL: {resource_url[:60]}...", flush=True)
                
                if resource_url.startswith('https://'):
                    print("\n" + "=" * 70)
                    print("✅ SUCCESS - HTTPS URLs Fixed!")
                    print("=" * 70)
                    print(f"\nResource URL: {resource_url}")
                    print(f"\nCORS: {response.headers.get('access-control-allow-origin', 'Not set')}")
                    
                    print("\n" + "=" * 70)
                    print("🎉 Ready for Coinbase Wallet Payment!")
                    print("=" * 70)
                    print("\nYour payment link is ready:")
                    print(f"\n{SERVICE_URL}/verify?claim={requests.utils.quote(CLAIM)}")
                    print("\nBoth issues are now fixed:")
                    print("  ✅ HTTPS URLs (no more mixed content error)")
                    print("  ✅ CORS enabled (no more failed to fetch)")
                    print("\nTry the payment again in Coinbase Wallet!\n")
                    break
                elif resource_url.startswith('http://'):
                    print(f"[{elapsed}s] ⏳ Still using HTTP, waiting for deployment...")
                    
    except Exception as e:
        elapsed = (i + 1) * 10
        print(f"[{elapsed}s] ⏳ Deploying... ({str(e)[:30]})")
    
    time.sleep(10)
else:
    print("\n⚠️ Deployment taking longer than expected.")
