import asyncio
from src.services import verify_claim_logic

async def test_weather_prediction():
    print("Testing Weather Prediction...")
    print("=" * 60)
    
    result = await verify_claim_logic("Will it rain in New Orleans this week?")
    
    print(f"\nClaim Type: {result['claim_type']}")
    print(f"Verdict: {result['verdict']}")
    print(f"Confidence: {result['confidence_score']}")
    print(f"\nCitations:")
    for url in result['citations']:
        print(f"  - {url}")
    
    print(f"\n{'='*60}")
    print("OPTIMIST'S ARGUMENT (Why prediction is LIKELY):")
    print(result['debate']['prover'])
    
    print(f"\n{'='*60}")
    print("SKEPTIC'S ARGUMENT (Why prediction is UNCERTAIN):")
    print(result['debate']['debunker'])
    
    print(f"\n{'='*60}")
    print("ANALYST'S ASSESSMENT:")
    print(result['summary'])

asyncio.run(test_weather_prediction())
