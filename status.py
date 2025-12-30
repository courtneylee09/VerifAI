import requests
import time

print("=" * 70)
print("Railway Deployment Status Check")
print("=" * 70)
print("\nChecking service availability...\n")

for attempt in range(10):
    try:
        response = requests.get(
            'https://verifai-production.up.railway.app/verify?claim=test',
            timeout=5
        )
        
        if response.status_code == 402:
            data = response.json()
            resource = data.get('accepts', [{}])[0].get('resource', '')
            cors = response.headers.get('access-control-allow-origin', 'NOT SET')
            
            print("✅ Service is UP!")
            print(f"   Status: {response.status_code}")
            print(f"   Resource URL: {resource[:70]}...")
            print(f"   CORS: {cors}")
            
            if resource.startswith('https://') and cors != 'NOT SET':
                print("\n" + "=" * 70)
                print("🎉 ALL FIXES DEPLOYED - READY FOR PAYMENT!")
                print("=" * 70)
                print("\n✅ HTTPS URLs: Working")
                print("✅ CORS Headers: Enabled")
                print("\n📱 Try your payment link in Coinbase Wallet:")
                print("\nhttps://verifai-production.up.railway.app/verify?claim=Is%20Jesus%20the%20son%20of%20God%3F")
                print("\nBoth errors should be fixed now!\n")
                break
            elif resource.startswith('https://'):
                print("\n✅ HTTPS working, but CORS still deploying...")
            else:
                print("\n⏳ Service up but still deploying fixes...")
        else:
            print(f"[Attempt {attempt+1}] Status {response.status_code}, waiting...")
            
    except Exception as e:
        print(f"[Attempt {attempt+1}] Service restarting: {str(e)[:40]}...")
    
    if attempt < 9:
        time.sleep(5)

print("\n" + "=" * 70)
