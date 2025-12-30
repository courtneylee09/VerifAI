import asyncio
from src.services import verify_claim_logic


async def test_claim():
    claim = "Is Jesus the son of God?"
    
    print("\n" + "=" * 70)
    print("VerifAI - Direct Test (No Payment)")
    print("=" * 70)
    print(f"\n🔍 Claim: {claim}")
    print("\n⏳ Running multi-agent verification...")
    print("   • Searching web sources...")
    print("   • Prover agent finding supporting evidence...")
    print("   • Debunker agent finding counter-arguments...")
    print("   • Judge agent weighing both sides...")
    print()
    
    result = await verify_claim_logic(claim)
    
    print("=" * 70)
    print("✅ VERIFICATION COMPLETE")
    print("=" * 70)
    
    print(f"\n📊 VERDICT: {result.get('verdict')}")
    print(f"📈 CONFIDENCE: {result.get('confidence_score')}")
    print(f"🏷️  CLAIM TYPE: {result.get('claim_type', 'factual')}")
    
    print(f"\n💡 SUMMARY:")
    print(f"   {result.get('summary', 'No summary available')}")
    
    if result.get('reason'):
        print(f"\n📝 REASONING:")
        print(f"   {result.get('reason')}")
    
    citations = result.get('citations', [])
    if citations:
        print(f"\n📚 SOURCES CONSULTED ({len(citations)}):")
        for i, cite in enumerate(citations[:5], 1):
            print(f"   {i}. {cite.get('title', 'Unknown')}")
            print(f"      {cite.get('url', 'N/A')}")
    
    print(f"\n🔍 AUDIT TRAIL:")
    print(f"   {result.get('audit_trail', 'N/A')}")
    
    if 'token_summary' in result:
        print(f"\n💰 TOKEN USAGE & COST:")
        total_cost = 0
        for agent, data in result['token_summary'].items():
            if data.get('tokens_used', 0) > 0:
                cost = data.get('cost_usd', 0)
                total_cost += cost
                print(f"   {agent}: {data.get('tokens_used')} tokens (${cost:.4f})")
        print(f"   TOTAL COST: ${total_cost:.4f}")
    
    print("\n" + "=" * 70)
    print()


if __name__ == "__main__":
    asyncio.run(test_claim())
