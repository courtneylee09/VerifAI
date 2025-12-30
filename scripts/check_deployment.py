#!/usr/bin/env python3
"""
Quick deployment checker - run this after any Railway deployment
to verify the current status and identify issues.
"""
import requests
import sys
from datetime import datetime

RAILWAY_URL = "https://verifai-production.up.railway.app"
TEST_CLAIM = "test"

def check_deployment():
    """Check if deployment is working and identify issues"""
    print(f"\n{'='*60}")
    print(f"VerifAI Deployment Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Test 1: Root endpoint
    print("1. Testing root endpoint...")
    try:
        r = requests.get(f"{RAILWAY_URL}/", timeout=10)
        if r.status_code == 200:
            print(f"   ✅ Root endpoint OK ({r.status_code})")
            data = r.json()
            print(f"   Service: {data.get('service', 'Unknown')}")
            print(f"   Status: {data.get('status', 'Unknown')}")
        elif r.status_code == 402:
            print(f"   ⚠️  Root endpoint requires payment (402) - check if root handler exists")
        else:
            print(f"   ❌ Root endpoint returned {r.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Root endpoint failed: {e}")
        return False
    
    # Test 2: Verify endpoint (should return 402)
    print("\n2. Testing verify endpoint...")
    try:
        r = requests.get(f"{RAILWAY_URL}/verify?claim={TEST_CLAIM}", timeout=10)
        if r.status_code == 402:
            print(f"   ✅ Payment wall active (402)")
        else:
            print(f"   ⚠️  Unexpected status: {r.status_code}")
            print(f"   Response: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Verify endpoint failed: {e}")
        return False
    
    # Test 3: Check HTTPS in resource URL
    print("\n3. Testing HTTPS resource URL...")
    try:
        payment_data = r.json()
        
        # Handle both formats: array or single object
        if isinstance(payment_data.get('accepts'), list):
            accept = payment_data['accepts'][0]
        else:
            accept = payment_data
            
        resource = accept['resource']
        print(f"   Resource URL: {resource}")
        
        if resource.startswith('https://'):
            print(f"   ✅ Using HTTPS - Mixed content issue FIXED!")
            is_https = True
        else:
            print(f"   ❌ Using HTTP - Mixed content issue still present")
            is_https = False
        
        # Check other payment details
        print(f"\n   Payment Details:")
        if 'payTo' in accept:
            print(f"   - Merchant: {accept['payTo']['address']}")
            print(f"   - Network: {accept['payTo']['network']}")
        if 'amount' in accept:
            print(f"   - Amount: {accept['amount']} USDC")
        
    except Exception as e:
        print(f"   ❌ Failed to parse payment data: {e}")
        print(f"   Response: {r.text[:500]}")
        return False
    
    # Summary
    print(f"\n{'='*60}")
    if is_https:
        print("✅ DEPLOYMENT SUCCESSFUL - All checks passed")
        print("\nPayment link ready:")
        print(f"{RAILWAY_URL}/verify?claim=Is%20Jesus%20the%20son%20of%20God%3F")
        print("\nNext step: Test payment in Coinbase Wallet")
    else:
        print("❌ DEPLOYMENT HAS ISSUES - HTTPS fix needed")
        print("\nIssue: x402 still returning HTTP URLs")
        print("Impact: Coinbase Wallet will show mixed content error")
        print("\nNext step: Review DEPLOYMENT_LOG.md for previous attempts")
    print(f"{'='*60}\n")
    
    return is_https

if __name__ == "__main__":
    success = check_deployment()
    sys.exit(0 if success else 1)
