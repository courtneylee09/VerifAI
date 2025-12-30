"""
Token usage tracker for performance logging.
Stores token counts globally during request execution.
"""

from typing import Dict, Optional

class TokenTracker:
    """Thread-local storage for token usage during verification."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Clear all tracked tokens."""
        self.prover_tokens: Optional[Dict] = None
        self.debunker_tokens: Optional[Dict] = None
        self.judge_tokens: Optional[Dict] = None
        self.verdict_type: Optional[str] = None  # Track verdict for cost analysis
        self.is_inconclusive: bool = False  # Flag for discount analysis
    
    def set_prover_tokens(self, model: str, input_tokens: int, output_tokens: int):
        """Record prover agent token usage."""
        self.prover_tokens = {
            "model": model,
            "input": input_tokens,
            "output": output_tokens
        }
    
    def set_debunker_tokens(self, model: str, input_tokens: int, output_tokens: int):
        """Record debunker agent token usage."""
        self.debunker_tokens = {
            "model": model,
            "input": input_tokens,
            "output": output_tokens
        }
    
    def set_judge_tokens(self, model: str, input_tokens: int, output_tokens: int):
        """Record judge agent token usage."""
        self.judge_tokens = {
            "model": model,
            "input": input_tokens,
            "output": output_tokens
        }
    
    def set_verdict(self, verdict: str):
        """
        Record the final verdict for cost analysis.
        Flags inconclusive results for potential discount consideration.
        
        Args:
            verdict: "True"/"False"/"Inconclusive" (or "Likely"/"Unlikely"/"Uncertain" for predictions)
        """
        self.verdict_type = verdict
        # Flag inconclusive/uncertain verdicts for discount analysis
        self.is_inconclusive = verdict.lower() in ["inconclusive", "uncertain"]
    
    def get_all(self) -> Dict:
        """Get all tracked token data including verdict info."""
        return {
            "prover": self.prover_tokens,
            "debunker": self.debunker_tokens,
            "judge": self.judge_tokens,
            "verdict_type": self.verdict_type,
            "is_inconclusive": self.is_inconclusive
        }


# Global instance for tracking during requests
token_tracker = TokenTracker()
