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
    
    def get_all(self) -> Dict:
        """Get all tracked token data."""
        return {
            "prover": self.prover_tokens,
            "debunker": self.debunker_tokens,
            "judge": self.judge_tokens
        }


# Global instance for tracking during requests
token_tracker = TokenTracker()
