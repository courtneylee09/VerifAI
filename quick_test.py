import asyncio
import sys
from src.services import verify_claim_logic


async def test_claim():
    claim = "Is Jesus the son of God?"
    
    print("\n" + "=" * 70, flush=True)
    print("VerifAI - Testing Your Claim", flush=True)
    print("=" * 70, flush=True)
    print(f"\nClaim: {claim}\n", flush=True)
    
    try:
        result = await verify_claim_logic(claim)
        
        print("\n" + "=" * 70, flush=True)
        print("RESULTS", flush=True)
        print("=" * 70, flush=True)
        
        print(f"\nVerdict: {result.get('verdict')}", flush=True)
        print(f"Confidence: {result.get('confidence_score')}", flush=True)
        print(f"\nSummary:\n{result.get('summary', 'No summary')}", flush=True)
        
        citations = result.get('citations', [])
        print(f"\nSources ({len(citations)}):", flush=True)
        for i, cite in enumerate(citations[:3], 1):
            print(f"  {i}. {cite.get('title')}", flush=True)
        
        print("\n" + "=" * 70, flush=True)
        
    except Exception as e:
        print(f"\nError: {e}", flush=True)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_claim())
