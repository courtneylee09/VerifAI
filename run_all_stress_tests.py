"""
Master Stress Test Suite Runner

Orchestrates all stress tests and generates comprehensive report for launch readiness.

Usage:
    python run_all_stress_tests.py                 # Run all tests with defaults
    python run_all_stress_tests.py --quick         # Quick tests (2-3 min total)
    python run_all_stress_tests.py --full          # Full suite (15-20 min total)
    python run_all_stress_tests.py --skip-concurrent  # Skip long test
"""

import asyncio
import subprocess
import sys
import time
import argparse
import json
from datetime import datetime
from pathlib import Path

# ============================================================================
# Test Configurations
# ============================================================================

TESTS = {
    "concurrent_5": {
        "name": "Concurrent Load (5 workers, 20 claims each)",
        "script": "concurrent_stress_test.py",
        "args": ["--workers=5", "--claims=20"],
        "duration": "~2 minutes"
    },
    "concurrent_10": {
        "name": "Concurrent Load (10 workers, 15 claims each)",
        "script": "concurrent_stress_test.py",
        "args": ["--workers=10", "--claims=15"],
        "duration": "~2 minutes"
    },
    "payment_20": {
        "name": "Payment Validation (20 concurrent, 60s)",
        "script": "payment_load_test.py",
        "args": ["--concurrent=20", "--duration=60"],
        "duration": "~1 minute"
    },
    "payment_50": {
        "name": "Payment Validation (50 concurrent, 60s)",
        "script": "payment_load_test.py",
        "args": ["--concurrent=50", "--duration=60"],
        "duration": "~1 minute"
    }
}

QUICK_TESTS = ["concurrent_5", "payment_20"]
FULL_TESTS = list(TESTS.keys())

# ============================================================================
# Runner
# ============================================================================

class StressTestRunner:
    """Orchestrate and report on stress tests."""
    
    def __init__(self, test_mode: str = "standard"):
        self.test_mode = test_mode
        self.results = []
        self.start_time = None
        self.end_time = None
        
        # Select tests based on mode
        if test_mode == "quick":
            self.tests_to_run = QUICK_TESTS
        elif test_mode == "full":
            self.tests_to_run = FULL_TESTS
        else:
            self.tests_to_run = FULL_TESTS
    
    def print_header(self):
        """Print test suite header."""
        print("\n" + "="*80)
        print("VERIFAI STRESS TEST SUITE")
        print("="*80)
        print(f"Mode: {self.test_mode.upper()}")
        print(f"Tests to run: {len(self.tests_to_run)}")
        # Extract numeric duration (e.g., "~2 minutes" -> 2)
        total_time = sum(int(TESTS[t]['duration'].split()[0].lstrip('~')) for t in self.tests_to_run)
        print(f"Total estimated time: ~{total_time} minutes")
        print("="*80 + "\n")
    
    def run_test(self, test_id: str) -> bool:
        """Run a single test."""
        test_config = TESTS[test_id]
        
        print(f"\n{'='*80}")
        print(f"🧪 TEST: {test_config['name']}")
        print(f"{'='*80}\n")
        
        # Build command
        cmd = ["python", test_config["script"]] + test_config["args"]
        
        print(f"Running: {' '.join(cmd)}\n")
        
        try:
            result = subprocess.run(cmd, capture_output=False, text=True)
            success = result.returncode == 0
            
            self.results.append({
                "test_id": test_id,
                "name": test_config["name"],
                "status": "PASSED" if success else "FAILED",
                "returncode": result.returncode,
                "timestamp": datetime.now().isoformat()
            })
            
            return success
        
        except Exception as e:
            print(f"❌ Error running test: {e}")
            self.results.append({
                "test_id": test_id,
                "name": test_config["name"],
                "status": "ERROR",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            return False
    
    def print_summary(self):
        """Print overall results summary."""
        print("\n" + "="*80)
        print("STRESS TEST SUITE SUMMARY")
        print("="*80)
        
        duration = (self.end_time - self.start_time) if self.start_time and self.end_time else 0
        passed = sum(1 for r in self.results if r["status"] == "PASSED")
        failed = sum(1 for r in self.results if r["status"] in ["FAILED", "ERROR"])
        
        print(f"\nResults: {passed} passed, {failed} failed")
        print(f"Duration: {duration/60:.1f} minutes\n")
        
        print("Test Results:")
        for result in self.results:
            status_icon = "✅" if result["status"] == "PASSED" else "❌"
            print(f"  {status_icon} {result['test_id']}: {result['status']}")
        
        print("\n" + "="*80)
        
        if failed == 0:
            print("✅ ALL TESTS PASSED - READY FOR LAUNCH")
        else:
            print(f"⚠️  {failed} TEST(S) FAILED - FIX BEFORE LAUNCHING")
        
        print("="*80 + "\n")
        
        # Save summary
        self._save_summary()
    
    def _save_summary(self):
        """Save test results to JSON."""
        results_dir = Path("logs")
        results_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = results_dir / f"stress_test_suite_{timestamp}.json"
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "mode": self.test_mode,
            "duration_minutes": (self.end_time - self.start_time) / 60 if self.start_time and self.end_time else 0,
            "tests_run": len(self.results),
            "passed": sum(1 for r in self.results if r["status"] == "PASSED"),
            "failed": sum(1 for r in self.results if r["status"] in ["FAILED", "ERROR"]),
            "results": self.results
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"📊 Summary saved to: {summary_file}")
    
    def run_all(self):
        """Run all tests."""
        self.print_header()
        self.start_time = time.time()
        
        for test_id in self.tests_to_run:
            try:
                self.run_test(test_id)
            except KeyboardInterrupt:
                print("\n\n⚠️  Test suite interrupted by user")
                break
        
        self.end_time = time.time()
        self.print_summary()


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Run complete VerifAI stress test suite"
    )
    parser.add_argument(
        "--mode",
        choices=["quick", "full", "standard"],
        default="standard",
        help="Test mode: quick (~5 min), full (~10 min), or standard (default)"
    )
    parser.add_argument(
        "--skip-concurrent",
        action="store_true",
        help="Skip long concurrent tests"
    )
    parser.add_argument(
        "--skip-payment",
        action="store_true",
        help="Skip payment tests"
    )
    
    args = parser.parse_args()
    
    runner = StressTestRunner(test_mode=args.mode)
    
    # Filter tests based on args
    if args.skip_concurrent:
        runner.tests_to_run = [t for t in runner.tests_to_run if "concurrent" not in t]
    if args.skip_payment:
        runner.tests_to_run = [t for t in runner.tests_to_run if "payment" not in t]
    
    try:
        runner.run_all()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted")
        sys.exit(1)


if __name__ == "__main__":
    main()
