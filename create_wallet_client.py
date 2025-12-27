"""Create or fetch a server-managed EVM wallet via CDP SDK (cdp-sdk).

Usage (PowerShell):
  $env:CDP_API_KEY_ID = "<api-key-id>"
  $env:CDP_API_KEY_SECRET = "<api-key-secret>"
  $env:CDP_WALLET_SECRET = "<wallet-secret-base64>"  # from CDP Portal
  # optional overrides
  $env:CDP_WALLET_NAME = "verifai-buyer"             # default
  $env:REQUEST_FAUCET = "1"                          # request base-sepolia ETH faucet
  $env:EXPORT_SEED = "0"                             # set to 1 to export private key (sensitive)

  py create_wallet_client.py
"""

import asyncio
import os
import sys

from dotenv import load_dotenv

try:
    import cdp
except Exception as exc:  # pragma: no cover
    print(f"Missing cdp-sdk or import failed: {exc}")
    sys.exit(1)

load_dotenv()

REQUIRED = ["CDP_API_KEY_ID", "CDP_API_KEY_SECRET", "CDP_WALLET_SECRET"]
missing = [var for var in REQUIRED if not os.getenv(var)]
if missing:
    print("Missing required environment variables:", ", ".join(missing))
    sys.exit(2)

WALLET_NAME = os.getenv("CDP_WALLET_NAME", "verifai-buyer")
REQUEST_FAUCET = os.getenv("REQUEST_FAUCET", "0") == "1"
EXPORT_SEED = os.getenv("EXPORT_SEED", "0") == "1"


async def main() -> None:
    try:
        async with cdp.CdpClient() as client:
            account = await client.evm.get_or_create_account(name=WALLET_NAME)
            print(f"Server wallet name: {account.name}")
            print(f"Server wallet address: {account.address}")

            if REQUEST_FAUCET:
                try:
                    tx_hash = await client.evm.request_faucet(
                        address=account.address, network="base-sepolia", token="eth"
                    )
                    print(f"Requested Base Sepolia ETH faucet: {tx_hash}")
                except Exception as faucet_exc:  # pragma: no cover
                    print(f"Faucet request failed: {faucet_exc}")

            if EXPORT_SEED:
                try:
                    private_key = await client.evm.export_account(name=account.name)
                    print("WARNING: Private key export below; handle securely.")
                    print(private_key)
                except Exception as export_exc:  # pragma: no cover
                    print(f"Export failed: {export_exc}")
    except Exception as exc:
        print(f"Wallet creation/lookup failed: {exc}")
        sys.exit(3)


if __name__ == "__main__":
    asyncio.run(main())
