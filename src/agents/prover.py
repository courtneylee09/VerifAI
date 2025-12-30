"""Prover Agent: Builds strongest case FOR the claim using provided sources."""
import logging
from openai import AsyncOpenAI
from google import genai
from google.genai import types

from config.settings import (
    DEEPINFRA_API_KEY, GEMINI_API_KEY, DEEPINFRA_BASE_URL,
    PROVER_MODEL, GEMINI_FALLBACK_MODEL, PROVER_TEMPERATURE,
    PROVER_MAX_TOKENS, PROVER_SYSTEM_PROMPT
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


async def run_prover_agent(claim: str, data_points: list[str], is_prediction: bool = False) -> str:
    """
    Prover Agent: Builds the strongest case FOR the claim.
    Primary: DeepInfra Llama 3.3 70B
    Fallback: Gemini (only if DeepInfra fails)

    Handles both factual claims and predictions.
    """
    context = "\n\n".join([f"Source {i+1}: {text}" for i, text in enumerate(data_points)])

    if is_prediction:
        prompt = f"""You are a skilled analyst building the STRONGEST case that this PREDICTION is likely to occur.        

PREDICTION: {claim}

SOURCES (forecasts, expert opinions, trend data):
{context}

Your task: Find evidence, forecasts, or expert opinions that SUPPORT this prediction being likely.
Present the most convincing argument for why this prediction could come true.
Be persuasive but honest - only cite what the sources actually say.

Return 2-3 sentences arguing FOR the prediction's likelihood."""
    else:
        prompt = f"""You are a skilled advocate building the STRONGEST case to PROVE this claim is true.

CLAIM: {claim}

SOURCES:
{context}

Your task: Find evidence that SUPPORTS the claim. Present the most convincing argument.
Be persuasive but honest - only cite what the sources actually say.

Return 2-3 sentences arguing FOR the claim."""

    # Try DeepInfra first
    try:
        response = await deepinfra_client.chat.completions.create(
            model=PROVER_MODEL,
            messages=[
                {"role": "system", "content": PROVER_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=PROVER_TEMPERATURE,
            max_tokens=PROVER_MAX_TOKENS
        )

        # Track token usage
        token_tracker.set_prover_tokens(
            model=PROVER_MODEL,
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning("prover.deepinfra.failed err=%s", str(e)[:200])

        # Fallback to Gemini
        try:
            response = gemini_client.models.generate_content(
                model=GEMINI_FALLBACK_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=PROVER_TEMPERATURE)
            )

            # Track Gemini usage (no cost, but track for analytics)
            token_tracker.set_prover_tokens(
                model=GEMINI_FALLBACK_MODEL,
                input_tokens=response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0,
                output_tokens=response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0
            )

            return response.text.strip()
        except Exception as gemini_error:
            logger.error("prover.gemini.failed err=%s", gemini_error)
            return "Unable to generate prover argument."
