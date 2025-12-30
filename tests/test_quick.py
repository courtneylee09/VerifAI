import asyncio
from src.services import verify_claim_logic


async def test_quick():
    """Quick test with a single simple claim."""
    print("Testing VerifAI verification service...\n")
    print("=" * 60)
    print("Claim: The Earth orbits the Sun")
    print("=" * 60)
    
    result = await verify_claim_logic("The Earth orbits the Sun")
    
    print(f"\n✅ RESULTS:")
    print(f"  Verdict: {result.get('verdict')}")
    print(f"  Confidence: {result.get('confidence_score')}")
    print(f"  Claim Type: {result.get('claim_type')}")
    print(f"  Summary: {result.get('summary')}")
    print(f"\n📊 Citations ({len(result.get('citations', []))}):")
    for i, citation in enumerate(result.get('citations', [])[:3], 1):
        print(f"  {i}. {citation.get('title', 'Unknown')}")
        print(f"     {citation.get('url', 'N/A')}")
    
    print(f"\n🔍 Audit Trail:")
    print(f"  {result.get('audit_trail')}")
    
    # Token usage
    if 'token_summary' in result:
        print(f"\n💰 Token Usage:")
        for agent, data in result['token_summary'].items():
            if data.get('tokens_used', 0) > 0:
                print(f"  {agent}: {data.get('tokens_used')} tokens")


if __name__ == "__main__":
    asyncio.run(test_quick())
