"""Judge Agent: Weighs both arguments and issues final verdict."""
import json
import re
import logging
from anthropic import Anthropic

from config.settings import (
    ANTHROPIC_API_KEY, JUDGE_MODEL, JUDGE_MAX_TOKENS
)
from src.utils.token_tracker import token_tracker

logger = logging.getLogger(__name__)

# Initialize client
claude_client = Anthropic(api_key=ANTHROPIC_API_KEY)


async def run_judge_agent(
    claim: str, 
    data_points: list[str], 
    weights: list[float], 
    prover_arg: str, 
    debunker_arg: str, 
    is_prediction: bool = False
) -> dict:
    """
    Judge Agent (Claude 3.5 Haiku): Weighs both arguments and issues final verdict.
    Handles both factual verification and prediction likelihood assessment.
    """
    # Combine sources with weights for judge context
    context_parts = []
    for i, (text, weight) in enumerate(zip(data_points, weights)):
        weight_label = " (Wikipedia - 0.5x weight)" if weight == 0.5 else " (1.0x weight)"
        context_parts.append(f"Source {i+1}{weight_label}: {text}")
    context = "\n\n".join(context_parts)

    if is_prediction:
        prompt = f"""You are a high-accuracy Prediction Analyst. Two experts have debated the likelihood of this prediction. Weigh both arguments and assess probability.

PREDICTION: {claim}

OPTIMIST'S ARGUMENT (arguing prediction is LIKELY):
{prover_arg}

SKEPTIC'S ARGUMENT (arguing prediction is UNLIKELY or UNCERTAIN):
{debunker_arg}

ORIGINAL SOURCES (forecasts, expert opinions, trend data):
{context}

TASK:
1. Weigh both arguments against the raw sources.
2. Check for consensus or disagreement among forecasts/experts.
3. Wikipedia sources should be weighted at 0.5x (half weight) compared to other sources at 1.0x.
4. For predictions, provide a 'verdict': "Likely", "Unlikely", or "Uncertain"
5. Provide a 'confidence_score' between 0.0 and 1.0 representing prediction confidence (NOT certainty)
6. Summarize your reasoning in one sentence.

Respond in JSON format with these exact fields:
{{
    "verdict": "Likely|Unlikely|Uncertain",
    "confidence_score": 0.65,
    "summary": "One sentence summary explaining the prediction assessment"
}}"""
    else:
        prompt = f"""You are a high-accuracy Verification Judge. Two advocates have debated this claim. Weigh both arguments and issue a final ruling.

CLAIM: {claim}

PROVER'S ARGUMENT (arguing FOR the claim):
{prover_arg}

DEBUNKER'S ARGUMENT (arguing AGAINST the claim):
{debunker_arg}

ORIGINAL SOURCES:
{context}

TASK:
1. Weigh both arguments against the raw sources.
2. Check for contradictions between sources.
3. Wikipedia sources should be weighted at 0.5x (half weight) compared to other sources at 1.0x.
4. Provide a 'verdict': "Verified", "Unverified", or "Inconclusive".
5. Provide a 'confidence_score' between 0.0 and 1.0.
6. Summarize your reasoning in one sentence.

Respond in JSON format with these exact fields:
{{
    "verdict": "Verified|Unverified|Inconclusive",
    "confidence_score": 0.95,
    "summary": "One sentence summary explaining the ruling"
}}"""

    try:
        response = claude_client.messages.create(
            model=JUDGE_MODEL,
            max_tokens=JUDGE_MAX_TOKENS,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

            # Track token usage
            token_tracker.set_judge_tokens(
                model=JUDGE_MODEL,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens
            )

        response_text = response.content[0].text
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = {
                    "verdict": "Inconclusive",
                    "confidence_score": 0.5,
                    "summary": "Unable to parse judge response properly."
                }

        return result

    except Exception as e:
        logger.error("judge.failed err=%s", e)
        return {
            "verdict": "Inconclusive",
            "confidence_score": 0.5,
            "summary": f"Judge analysis failed: {str(e)}"
        }
