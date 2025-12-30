"""
VerifAI Stress Test - Challenging Claims
Tests the app with complex, controversial, and multi-faceted claims
"""
import asyncio
import time
import requests
from src.services.verification import verify_claim_logic

# Challenging claims that will stress-test the system
STRESS_TEST_CLAIMS = [
    # 1. Controversial with conflicting evidence
    {
        "claim": "Are mRNA COVID-19 vaccines safe for long-term use?",
        "difficulty": "HIGH - Medical controversy, recent tech, political polarization",
        "challenges": "Conflicting sources, recent data, requires nuanced medical analysis"
    },
    
    # 2. Predictive/speculative with limited data
    {
        "claim": "Will artificial intelligence cause mass unemployment by 2030?",
        "difficulty": "EXTREME - Future prediction, economic complexity, AI pace unknown",
        "challenges": "No definitive sources, requires reasoning about future trends"
    },
    
    # 3. Correlation vs causation trap
    {
        "claim": "Does social media use cause depression in teenagers?",
        "difficulty": "HIGH - Correlation/causation confusion, psychology complexity",
        "challenges": "Mixed research results, confounding variables, definition ambiguity"
    },
    
    # 4. Financial/volatile topic
    {
        "claim": "Is Bitcoin a better store of value than gold?",
        "difficulty": "EXTREME - Highly polarized, volatile market, ideological divide",
        "challenges": "Rapidly changing data, strong partisan sources, short history"
    },
    
    # 5. Technical with emerging research
    {
        "claim": "Will quantum computers break Bitcoin's encryption within 5 years?",
        "difficulty": "EXTREME - Highly technical, predictive, limited expert consensus",
        "challenges": "Requires deep technical knowledge, future prediction, scarce sources"
    },
    
    # 6. Complex multi-factor claim
    {
        "claim": "Does intermittent fasting lead to sustainable weight loss better than calorie restriction?",
        "difficulty": "MEDIUM-HIGH - Medical nuance, individual variation, definition issues",
        "challenges": "Mixed study results, 'sustainable' is subjective, many variables"
    },
    
    # 7. Emerging technology with limited data
    {
        "claim": "Is lab-grown meat healthier and more environmentally sustainable than traditional meat?",
        "difficulty": "HIGH - New technology, limited long-term data, multiple dimensions",
        "challenges": "Scarce research, corporate bias in sources, environmental modeling complexity"
    }
]

async def run_stress_test(claim_data: dict):
    """Run a single stress test and measure performance"""
    claim = claim_data["claim"]
    print(f"\n{'='*80}")
    print(f"STRESS TEST: {claim}")
    print(f"Difficulty: {claim_data['difficulty']}")
    print(f"Challenges: {claim_data['challenges']}")
    print(f"{'='*80}\n")
    
    start_time = time.time()
    
    try:
        # Run the verification
        result = await verify_claim_logic(claim)
        
        execution_time = time.time() - start_time
        
        # Analyze the result
        print(f"\n✅ COMPLETED in {execution_time:.2f}s")
        print(f"\nVERDICT: {result['verdict']} (Confidence: {result['confidence']:.0%})")
        print(f"\nJUDGE'S REASONING:")
        print(result['reasoning'][:500] + "..." if len(result['reasoning']) > 500 else result['reasoning'])
        
        print(f"\n📊 PERFORMANCE METRICS:")
        print(f"  - Execution time: {result['execution_time_seconds']:.2f}s")
        print(f"  - Cost: ${result['total_cost_usd']:.4f}")
        print(f"  - Sources found: {len(result['sources'])}")
        print(f"  - Prover argument length: {len(result['prover_argument'])} chars")
        print(f"  - Debunker argument length: {len(result['debunker_argument'])} chars")
        print(f"  - Reasoning length: {len(result['reasoning'])} chars")
        
        # Quality checks
        print(f"\n🔍 QUALITY CHECKS:")
        quality_issues = []
        
        if result['confidence'] < 0.3:
            quality_issues.append("⚠️  Very low confidence - system is uncertain")
        if len(result['sources']) < 3:
            quality_issues.append("⚠️  Few sources found - may lack evidence")
        if len(result['prover_argument']) < 200:
            quality_issues.append("⚠️  Weak prover argument")
        if len(result['debunker_argument']) < 200:
            quality_issues.append("⚠️  Weak debunker argument")
        if len(result['reasoning']) < 150:
            quality_issues.append("⚠️  Shallow reasoning from judge")
        if result['execution_time_seconds'] > 60:
            quality_issues.append("⚠️  Slow execution (>60s)")
        
        if quality_issues:
            for issue in quality_issues:
                print(f"  {issue}")
        else:
            print("  ✅ All quality checks passed!")
        
        return {
            "claim": claim,
            "success": True,
            "verdict": result['verdict'],
            "confidence": result['confidence'],
            "execution_time": execution_time,
            "cost": result['total_cost_usd'],
            "quality_issues": quality_issues
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"\n❌ FAILED after {execution_time:.2f}s")
        print(f"Error: {str(e)}")
        
        return {
            "claim": claim,
            "success": False,
            "error": str(e),
            "execution_time": execution_time
        }

async def main():
    """Run all stress tests"""
    print("\n" + "="*80)
    print("VERIFAI STRESS TEST SUITE")
    print("Testing challenging claims to push the multi-agent system")
    print("="*80)
    
    # Let user choose which test to run
    print("\nAvailable stress tests:")
    for i, test in enumerate(STRESS_TEST_CLAIMS, 1):
        print(f"\n{i}. {test['claim']}")
        print(f"   Difficulty: {test['difficulty']}")
    
    print("\n0. Run ALL tests (warning: expensive and time-consuming)")
    print("\nWhich test would you like to run? (0-7): ", end="")
    
    # For now, let's run test #2 (AI unemployment) as default
    # In interactive mode, user would input choice
    choice = 2  # AI unemployment - highly challenging
    
    if choice == 0:
        # Run all tests
        results = []
        total_start = time.time()
        
        for test in STRESS_TEST_CLAIMS:
            result = await run_stress_test(test)
            results.append(result)
            await asyncio.sleep(2)  # Brief pause between tests
        
        total_time = time.time() - total_start
        
        # Summary
        print("\n" + "="*80)
        print("STRESS TEST SUMMARY")
        print("="*80)
        
        successful = sum(1 for r in results if r['success'])
        total_cost = sum(r.get('cost', 0) for r in results if r['success'])
        avg_time = sum(r['execution_time'] for r in results if r['success']) / max(successful, 1)
        
        print(f"\nCompleted: {successful}/{len(STRESS_TEST_CLAIMS)} tests")
        print(f"Total time: {total_time:.2f}s")
        print(f"Total cost: ${total_cost:.4f}")
        print(f"Average execution time: {avg_time:.2f}s")
        
        print("\nResults by difficulty:")
        for result in results:
            status = "✅" if result['success'] else "❌"
            if result['success']:
                print(f"  {status} {result['claim'][:60]}... - {result['verdict']} ({result['confidence']:.0%})")
            else:
                print(f"  {status} {result['claim'][:60]}... - ERROR")
    else:
        # Run single test
        test = STRESS_TEST_CLAIMS[choice - 1]
        result = await run_stress_test(test)
        
        print("\n" + "="*80)
        print("STRESS TEST COMPLETE")
        print("="*80)
        
        if result['success']:
            print(f"\n✅ Test completed successfully")
            print(f"Verdict: {result['verdict']} (Confidence: {result['confidence']:.0%})")
            print(f"Time: {result['execution_time']:.2f}s")
            print(f"Cost: ${result['cost']:.4f}")
            
            if result['quality_issues']:
                print(f"\nQuality issues detected: {len(result['quality_issues'])}")
        else:
            print(f"\n❌ Test failed: {result['error']}")

if __name__ == "__main__":
    print("\n🔥 RUNNING DEFAULT STRESS TEST (AI Unemployment Prediction)")
    print("This will test the system's ability to handle:")
    print("- Future predictions with no definitive answer")
    print("- Complex economic and technological factors")
    print("- Limited concrete evidence")
    print("- Highly speculative reasoning required\n")
    
    asyncio.run(main())
