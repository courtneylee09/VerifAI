import requests

print("Checking deployment status...\n")

response = requests.get('https://verifai-production.up.railway.app/verify?claim=test')
data = response.json()

print("Status:", response.status_code)
print("Resource URL:", data['accepts'][0]['resource'])
print("CORS Allow-Origin:", response.headers.get('access-control-allow-origin', 'NOT SET'))

if data['accepts'][0]['resource'].startswith('https://'):
    print("\n✅ HTTPS is WORKING!")
    print("✅ Ready to test payment with Coinbase Wallet!")
    print("\nYour payment link:")
    print("https://verifai-production.up.railway.app/verify?claim=Is%20Jesus%20the%20son%20of%20God%3F")
else:
    print("\n⏳ Still deploying, HTTPS not ready yet")
