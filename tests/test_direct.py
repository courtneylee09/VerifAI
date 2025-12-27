import asyncio
from src.services import verify_claim_logic


async def test_direct():
    print("Testing verification logic directly (bypassing payment)...\\n")

    # Test 1: Rihanna and Fenty
    print("=" * 60)
    print("Test 1: Is Rihanna the founder of Fenty Beauty?")
    print("=" * 60)
    result = await verify_claim_logic("Is Rihanna the founder of Fenty Beauty?")
    print(f"Verdict: {result.get('verdict')}")
    print(f"Confidence: {result.get('confidence_score')}")
    print(f"Citations: {result.get('citations', [])[:3]}")  # Show first 3
    print(f"Audit Trail: {result.get('audit_trail')}\\n")

    # Test 2: A different claim
    print("=" * 60)
    print("Test 2: Who won the 2024 NBA Championship?")
    print("=" * 60)
    result2 = await verify_claim_logic("Who won the 2024 NBA Championship?")
    print(f"Verdict: {result2.get('verdict')}")
    print(f"Confidence: {result2.get('confidence_score')}")
    print(f"Citations: {result2.get('citations', [])[:3]}")
    print(f"Audit Trail: {result2.get('audit_trail')}\\n")


if __name__ == "__main__":
    asyncio.run(test_direct())
