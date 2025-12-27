import requests

print("Testing x402 paywall...")
print("=" * 60)

response = requests.get("http://127.0.0.1:8001/verify?claim=Is+Rihanna+the+founder+of+Fenty+Beauty")

print(f"Status Code: {response.status_code}")
print(f"Headers: {dict(response.headers)}")
print(f"Body: {response.text}")
