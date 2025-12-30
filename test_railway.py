#!/usr/bin/env python3
"""Quick test of Railway deployment."""

import requests
import json
import time

SERVICE_URL = "https://verifai-production.up.railway.app"

print("Testing VerifAI on Railway...")
print(f"URL: {SERVICE_URL}\n")

# Test 1: Health endpoint
print("1️⃣ Testing /health endpoint...")
try:
    response = requests.get(f"{SERVICE_URL}/health", timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}\n")
except Exception as e:
    print(f"   ❌ Failed: {e}\n")

# Test 2: Metrics endpoint
print("2️⃣ Testing /metrics/economics endpoint...")
try:
    response = requests.get(f"{SERVICE_URL}/metrics/economics", timeout=10)
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Total Verifications: {data.get('total_verifications', 0)}")
    print(f"   Total Revenue: ${data.get('total_revenue_usd', 0):.4f}\n")
except Exception as e:
    print(f"   ❌ Failed: {e}\n")

# Test 3: x402 manifest
print("3️⃣ Testing /.well-known/x402.json endpoint...")
try:
    response = requests.get(f"{SERVICE_URL}/.well-known/x402.json", timeout=10)
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Service Name: {data.get('name')}")
    print(f"   Price: {data.get('price')} {data.get('currency')}\n")
except Exception as e:
    print(f"   ❌ Failed: {e}\n")

print("✅ Railway deployment test complete!")
