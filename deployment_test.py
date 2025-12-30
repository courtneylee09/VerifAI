import requests

print("Testing Railway deployment...")
print("=" * 60)

# Test root endpoint
try:
    r1 = requests.get('https://verifai-production.up.railway.app/', timeout=10)
    print(f"\n✅ Root endpoint: {r1.status_code}")
    print(f"   Service: {r1.json().get('service')}")
except Exception as e:
    print(f"\n❌ Root endpoint error: {e}")

# Test verify endpoint
try:
    r2 = requests.get('https://verifai-production.up.railway.app/verify?claim=test', timeout=10)
    print(f"\n✅ Verify endpoint: {r2.status_code}")
    
    resource = r2.json()['accepts'][0]['resource']
    print(f"   Resource: {resource}")
    
    if resource.startswith('https://'):
        print("\n🎉 All fixed! HTTPS URLs are being used.")
    else:
        print(f"\n⏳ Still using HTTP - needs proxy header fix")
        
except Exception as e:
    print(f"\n❌ Verify endpoint error: {e}")

print("\n" + "=" * 60)
print("\nReady to test payment in Coinbase Wallet!")
print("Link: https://verifai-production.up.railway.app/verify?claim=Is%20Jesus%20the%20son%20of%20God%3F")
