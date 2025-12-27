"""Debunker Agent: Finds flaws and counter-evidence."""
import logging
from openai import AsyncOpenAI
from google import genai
from google.genai import types

from config.settings import (
    DEEPINFRA_API_KEY, GEMINI_API_KEY, DEEPINFRA_BASE_URL,
    DEBUNKER_MODEL, GEMINI_FALLBACK_MODEL, DEBUNKER_TEMPERATURE,
    DEBUNKER_MAX_TOKENS, DEBUNKER_SYSTEM_PROMPT
)
from src.utils.token_tracker import token_tracker

logger = logging.getLogger(__name__)

# Initialize clients
deepinfra_client = AsyncOpenAI(
    api_key=DEEPINFRA_API_KEY,
    base_url=DEEPINFRA_BASE_URL,
    max_retries=0
)
gemini_client = genai.Client(api_key=GEMINI_API_KEY)


async def run_debunker_agent(claim: str, data_points: list[str], is_prediction: bool = False) -> str:
    """
    Debunker Agent: Finds flaws and counter-evidence.
    Primary: DeepInfra DeepSeek-V3
    Fallback: Gemini (only if DeepInfra fails)

    Handles both factual claims and predictions.
    """
    context = "\n\n".join([f"Source {i+1}: {text}" for i, text in enumerate(data_points)])

    if is_prediction:
        prompt = f"""You are a critical skeptic challenging this PREDICTION.

PREDICTION: {claim}

SOURCES (forecasts, expert opinions, trend data):
{context}

Your task: Find contradictions, uncertainty, or evidence that CHALLENGES this prediction's likelihood.
Point out limitations in forecasts, conflicting expert opinions, or factors that could prevent it.
Be critical but honest - only cite what the sources actually say.

Return 2-3 sentences arguing AGAINST the prediction or noting its uncertainty."""
    else:
        prompt = f"""You are a critical skeptic trying to DEBUNK or find flaws in this claim.

CLAIM: {claim}

SOURCES:
{context}

Your task: Find contradictions, gaps, or evidence that CHALLENGES the claim.
Be critical but honest - only cite what the sources actually say.
If the claim appears true, point out any limitations or caveats in the evidence.

Return 2-3 sentences arguing AGAINST the claim or noting weaknesses in the evidence."""

    # Try DeepInfra first
    try:
        response = await deepinfra_client.chat.completions.create(
            model=DEBUNKER_MODEL,
            messages=[
                {"role": "system", "content": DEBUNKER_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=DEBUNKER_TEMPERATURE,
            max_tokens=DEBUNKER_MAX_TOKENS
        )

            # Track token usage
            token_tracker.set_debunker_tokens(
                model=DEBUNKER_MODEL,
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens
            )

        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning("debunker.deepinfra.failed err=%s", str(e)[:200])

        # Fallback to Gemini
        try:
            response = gemini_client.models.generate_content(
                model=GEMINI_FALLBACK_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=DEBUNKER_TEMPERATURE)
            )

                # Track Gemini usage (no cost, but track for analytics)
                token_tracker.set_debunker_tokens(
                    model=GEMINI_FALLBACK_MODEL,
                    input_tokens=response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0,
                    output_tokens=response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0
                )

            return response.text.strip()
        except Exception as gemini_error:
            logger.error("debunker.gemini.failed err=%s", gemini_error)
            return "Unable to generate debunker argument."
