import os
import sys
import asyncio

try:
    import cdp
except Exception as e:
    print(f"Error importing cdp-sdk: {e}")
    sys.exit(1)

REQUIRED_VARS = ["CDP_API_KEY_ID", "CDP_API_KEY_SECRET", "CDP_WALLET_SECRET"]
missing = [k for k in REQUIRED_VARS if not os.getenv(k)]
if missing:
    print("Missing required environment variables:", ", ".join(missing))
    print("Set them in your shell before running, e.g.:")
    print("  $env:CDP_API_KEY_ID = \"<your-api-key-id>\"")
    print("  $env:CDP_API_KEY_SECRET = \"<your-api-key-secret>\"")
    print("  $env:CDP_WALLET_SECRET = \"<your-wallet-secret>\"")
    sys.exit(2)

async def main():
    try:
        async with cdp.CdpClient() as client:
            account = await client.evm.get_or_create_account(name="verifai-buyer")
            print("Server wallet address:", account.address)
            print("Server wallet name:", account.name or "verifai-buyer")
    except Exception as e:
        print("Wallet creation/lookup failed:", e)
        sys.exit(3)

if __name__ == "__main__":
    asyncio.run(main())
