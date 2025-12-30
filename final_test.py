import requests
import json

try:
    r = requests.get('https://verifai-production.up.railway.app/verify?claim=Is%20Jesus%20the%20son%20of%20God%3F', timeout=10)
    print(f"Status: {r.status_code}")
    
    data = r.json()
    if 'accepts' in data and len(data['accepts']) > 0:
        resource = data['accepts'][0].get('resource', '')
        print(f"\nResource URL:\n{resource}")
        
        # Check if it has the full path
        if '/verify' in resource and 'claim=' in resource:
            print("\n✅ SUCCESS! Full URL with path and query parameters!")
            print("\n🎉 Payment should work now - try it in Coinbase Wallet!")
        elif resource.startswith('https://'):
            print("\n⚠️ HTTPS but missing path - may still have issues")
        else:
            print("\n⚠️ Still has issues")
            
        print(f"\nFull response:\n{json.dumps(data['accepts'][0], indent=2)}")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
