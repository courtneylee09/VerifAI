"""Simple stress test - will actually complete"""
import asyncio
from src.services.verification import verify_claim_logic

async def quick_stress_test():
    # Moderately challenging but will complete
    claim = "Does intermittent fasting lead to better weight loss than calorie restriction?"
    
    print(f"\nTesting: {claim}\n")
    
    try:
        result = await verify_claim_logic(claim)
        
        print(f"\n✅ COMPLETE!")
        print(f"Verdict: {result['verdict']}")
        print(f"Confidence: {result['confidence']:.0%}")
        print(f"Time: {result['execution_time_seconds']:.2f}s")
        print(f"Cost: ${result['total_cost_usd']:.4f}")
        print(f"\nReasoning: {result['reasoning'][:300]}...")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(quick_stress_test())
