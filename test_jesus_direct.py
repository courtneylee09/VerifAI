import asyncio
from src.services import verify_claim_logic


async def test_jesus_claim():
    """Test the Jesus claim directly without payment."""
    print("=" * 70)
    print("VerifAI Direct Test (No Payment Required)")
    print("=" * 70)
    print("\nClaim: Is Jesus the son of God?\n")
    print("Running multi-agent verification...\n")
    
    result = await verify_claim_logic("Is Jesus the son of God?")
    
    print("=" * 70)
    print("✅ VERIFICATION RESULTS")
    print("=" * 70)
    print(f"\nVerdict: {result.get('verdict')}")
    print(f"Confidence: {result.get('confidence_score')}")
    print(f"Claim Type: {result.get('claim_type')}")
    print(f"\nSummary: {result.get('summary')}")
    
    print(f"\n📚 Citations ({len(result.get('citations', []))}):")
    for i, citation in enumerate(result.get('citations', [])[:5], 1):
        print(f"  {i}. {citation.get('title', 'Unknown')}")
        print(f"     {citation.get('url', 'N/A')}")
    
    print(f"\n🔍 Audit Trail:")
    print(f"  {result.get('audit_trail')}")
    
    if 'token_summary' in result:
        print(f"\n💰 Token Usage & Cost:")
        for agent, data in result['token_summary'].items():
            if data.get('tokens_used', 0) > 0:
                cost = data.get('cost_usd', 0)
                print(f"  {agent}: {data.get('tokens_used')} tokens (${cost:.4f})")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(test_jesus_claim())
