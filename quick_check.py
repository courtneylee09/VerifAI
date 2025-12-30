import requests

try:
    r = requests.get('https://verifai-production.up.railway.app/verify?claim=test', timeout=10)
    print(f"Status: {r.status_code}")
    data = r.json()
    
    if 'accepts' in data and len(data['accepts']) > 0:
        resource = data['accepts'][0].get('resource', '')
        print(f"Resource URL: {resource}")
        
        if resource.startswith('https://'):
            print("\n✅ SUCCESS! HTTPS URLs are now being used!")
            print("\n🎉 Your payment link is ready:")
            print("https://verifai-production.up.railway.app/verify?claim=Is%20Jesus%20the%20son%20of%20God%3F")
            print("\nTry the payment again - both errors should be fixed!")
        elif resource.startswith('http://'):
            print("\n⏳ Still returning HTTP - Railway may still be deploying...")
        else:
            print(f"\n⚠️ Unexpected URL format: {resource}")
    else:
        print("No accepts field in response")
        
except Exception as e:
    print(f"Error: {e}")
