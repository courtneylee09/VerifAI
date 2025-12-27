"""
Test VerifAI x402 payment flow end-to-end.

This uses x402's EIP-712 signature-based payment (USDC transferWithAuthorization).
You need your private key to sign the authorization.

Before running:
1. Set your private key: $env:BUYER_PRIVATE_KEY = "0x..."
2. Run the test with a claim

Usage:
    $env:BUYER_PRIVATE_KEY = "0x..."  # Your test wallet private key
    python test_paid_verify.py "Your claim to verify"
"""

import asyncio
import base64
import json
import os
import sys
import time
import secrets

try:
    import httpx
    from eth_account import Account
    from eth_account.messages import encode_typed_data
except ImportError:
    print("Installing required packages...")
    os.system("pip install httpx eth-account")
    import httpx
    from eth_account import Account
    from eth_account.messages import encode_typed_data

# Payment configuration
MERCHANT_ADDRESS = "0x3615af0cE7c8e525B9a9C6cE281e195442596559"
USDC_CONTRACT = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
NETWORK = "base-sepolia"
AMOUNT = "50000"  # 0.05 USDC (6 decimals)
API_URL = "https://verifai-production.up.railway.app/verify"
CHAIN_ID = 84532  # Base Sepolia


def create_payment_header(account: Account) -> str:
    """Create the EIP-712 signed X-PAYMENT header."""
    nonce = secrets.token_bytes(32)
    valid_after = int(time.time()) - 60
    valid_before = int(time.time()) + 60
    
    # EIP-712 domain and message types for USDC transferWithAuthorization
    domain_data = {
        "name": "USDC",
        "version": "2",
        "chainId": CHAIN_ID,
        "verifyingContract": USDC_CONTRACT,
    }
    
    message_types = {
        "TransferWithAuthorization": [
            {"name": "from", "type": "address"},
            {"name": "to", "type": "address"},
            {"name": "value", "type": "uint256"},
            {"name": "validAfter", "type": "uint256"},
            {"name": "validBefore", "type": "uint256"},
            {"name": "nonce", "type": "bytes32"},
        ]
    }
    
    message_data = {
        "from": account.address,
        "to": MERCHANT_ADDRESS,
        "value": int(AMOUNT),
        "validAfter": valid_after,
        "validBefore": valid_before,
        "nonce": nonce,  # bytes, not hex string
    }
    
    # Sign the typed data using the proper eth_account method
    signed_message = account.sign_typed_data(
        domain_data=domain_data,
        message_types=message_types,
        message_data=message_data,
    )
    
    signature = signed_message.signature.hex()
    if not signature.startswith("0x"):
        signature = f"0x{signature}"

    # Construct the payment header
    payment_header = {
        "x402Version": 1,
        "scheme": "exact",
        "network": NETWORK,
        "payload": {
            "signature": signature,
            "authorization": {
                "from": account.address,
                "to": MERCHANT_ADDRESS,
                "value": AMOUNT,
                "validAfter": str(valid_after),
                "validBefore": str(valid_before),
                "nonce": f"0x{nonce.hex()}",
            },
        },
    }
    
    # Encode as JSON then base64
    json_str = json.dumps(payment_header)
    b64_encoded = base64.b64encode(json_str.encode()).decode()
    return b64_encoded


async def test_verify(claim: str, account: Account):
    """Test the verification endpoint with a paid request."""
    print(f"Testing verification for claim: {claim}")
    print(f"Buyer wallet: {account.address}\n")
    
    payment_header = create_payment_header(account)
    
    headers = {
        "X-PAYMENT": payment_header,
    }
    
    # The endpoint is GET with query parameter
    params = {"claim": claim}
    
    print("Sending request...")
    print(f"URL: {API_URL}")
    print(f"Params: {params}\n")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.get(API_URL, params=params, headers=headers)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("\n✅ SUCCESS! Paid verification complete:")
                print(json.dumps(result, indent=2))
            elif response.status_code == 402:
                print("\n❌ Payment required (402):")
                print(response.text)
            else:
                print(f"\nResponse ({response.status_code}):")
                print(response.text)
                
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    # Get private key from env or argument
    private_key = os.getenv("BUYER_PRIVATE_KEY")
    claim = "The sky is blue"
    
    if len(sys.argv) > 1:
        claim = sys.argv[1]
    if len(sys.argv) > 2:
        private_key = sys.argv[2]
    
    if not private_key:
        print("❌ Error: No private key provided")
        print("\nSteps to test:")
        print("1. Export your test wallet's private key from Coinbase Wallet")
        print("   (Settings → Show Private Key)")
        print("\n2. Make sure you have at least 0.05 USDC on Base Sepolia")
        print(f"   USDC contract: {USDC_CONTRACT}")
        print("\n3. Run:")
        print('   $env:BUYER_PRIVATE_KEY = "0x..."')
        print(f'   python {sys.argv[0]} "Your claim to verify"')
        print("\nOr:")
        print(f'   python {sys.argv[0]} "Your claim" "0xYourPrivateKey"')
        sys.exit(1)
    
    # Create account from private key
    try:
        account = Account.from_key(private_key)
        print(f"Loaded wallet: {account.address}\n")
    except Exception as e:
        print(f"❌ Invalid private key: {e}")
        sys.exit(1)
    
    asyncio.run(test_verify(claim, account))


if __name__ == "__main__":
    main()
