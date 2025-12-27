import asyncio
from src.services import verify_claim_logic

async def test_goat():
    print("Testing GOAT debate...")
    print("=" * 60)
    
    result = await verify_claim_logic("Is Michael Jordan or LeBron James the greatest basketball player of all time?")
    
    print(f"\nVerdict: {result['verdict']}")
    print(f"Confidence: {result['confidence_score']}")
    print(f"\nCitations:")
    for url in result['citations']:
        print(f"  - {url}")
    
    print(f"\n{'='*60}")
    print("PROVER'S ARGUMENT:")
    print(result['debate']['prover'])
    
    print(f"\n{'='*60}")
    print("DEBUNKER'S ARGUMENT:")
    print(result['debate']['debunker'])
    
    print(f"\n{'='*60}")
    print("JUDGE'S SUMMARY:")
    print(result['summary'])
    
    print(f"\n{'='*60}")
    print("FULL AUDIT TRAIL:")
    print(result['audit_trail'])

asyncio.run(test_goat())
