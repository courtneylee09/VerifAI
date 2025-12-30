"""
Philosophical Claim Pre-Filter

Detects normative/value judgment claims BEFORE running expensive multi-agent debate.
If detected, immediately returns Inconclusive with confidence=0.30 (< 0.40 refund threshold).

This is a cost-saving + brand-protection mechanism.
"""

import re
from typing import Tuple

# Normative language patterns that indicate philosophical/subjective claims
NORMATIVE_PATTERNS = [
    # Explicit value judgments
    r'\binherently\s+(evil|good|bad|wrong|right)\b',
    r'\bmorally\s+(wrong|right|corrupt|good|bad)\b',
    r'\b(all|every)\s+\w+\s+(are|is)\s+(corrupt|evil|good|bad)\b',
    
    # Absolute moral claims
    r'\b(failed|corrupt)\s+system\b',
    r'\bexploiting\s+(workers|people)\b',
    r'\bcause[sd]?\s+more\s+harm\s+than\s+good\b',
    
    # Universal negative/positive claims (often philosophical)
    r'\b(all|every)\s+(politicians?|billionaires?|corporations?)\s+(are|is)\s+corrupt\b',
    r'\ball\s+\w+\s+(media|news)\s+(is|are)\s+propaganda\b',
    
    # Normative modals
    r'\bshould(n\'t)?\s+\w+\b.*\?',  # Questions with "should"
    r'\bdeserve[sd]?\b',
    
    # Subjective aesthetic/quality judgments
    r'\bbest\b.*\?',
    r'\bbelong\s+on\b',  # "Does X belong on Y?"
    r'\bis\s+\w+\s+(beautiful|ugly|perfect|flawed)\b',
]

def is_philosophical_claim(claim: str) -> Tuple[bool, str]:
    """
    Check if claim contains normative/philosophical language.
    
    Returns:
        (is_philosophical, reason)
    """
    claim_lower = claim.lower()
    
    for pattern in NORMATIVE_PATTERNS:
        match = re.search(pattern, claim_lower, re.IGNORECASE)
        if match:
            return (True, f"Normative pattern detected: '{match.group()}'")
    
    return (False, "")

def get_philosophical_response(claim: str, reason: str) -> dict:
    """
    Generate immediate Inconclusive response for philosophical claims.
    
    This saves ~$0.003-0.004 in LLM costs and protects brand by not
    charging customers for subjective moral debates.
    """
    return {
        "verdict": "Inconclusive",
        "confidence_score": 0.30,  # Below 0.40 refund threshold
        "citations": [],
        "claim_type": "philosophical",
        "audit_trail": f"Pre-filter detected normative claim: {reason}. VerifAI is designed for factual verification, not philosophical debates.",
        "summary": f"This claim involves subjective value judgments ({reason}) that cannot be empirically verified. VerifAI specializes in factual claims with objective evidence.",
        "debate": {
            "prover": "N/A - Pre-filtered as philosophical claim",
            "debunker": "N/A - Pre-filtered as philosophical claim"
        },
        "manual_review": True,
        "payment_status": "refunded_due_to_uncertainty",
        "pre_filtered": True,
        "filter_reason": reason
    }
