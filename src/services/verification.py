"""Verification service: Main claim verification orchestration."""
import asyncio
import logging
import time

from config.settings import (
    EXA_SEARCH_TIMEOUT_SECONDS, DEBATE_TIMEOUT_SECONDS,
    PREDICTION_KEYWORDS, CONFIDENCE_THRESHOLD_FOR_MANUAL_REVIEW,
    CONFIDENCE_FLOOR_FOR_REFUND
)
from src.services.search import search_and_retrieve_sources, calculate_source_weights
from src.agents.prover import run_prover_agent
from src.agents.debunker import run_debunker_agent
from src.agents.judge import run_judge_agent
from performance_log import PerformanceLogger
from src.utils.token_tracker import token_tracker
from src.utils.philosophical_filter import is_philosophical_claim, get_philosophical_response

logger = logging.getLogger(__name__)


async def verify_claim_logic(claim: str) -> dict:
    """
    Multi-agent fact verification system using three specialized agents:
    - Prover (DeepInfra Llama 3.3 70B): Finds supporting evidence
    - Debunker (DeepInfra DeepSeek-V3): Finds contradicting evidence
    - Judge (Claude): Weighs arguments and issues final verdict

    Now handles both factual claims AND predictions (weather, events, trends)
    Implements HITL thresholding, circuit-breaker style fallbacks, and structured logging.
    
    Args:
        claim: The claim to verify
        
    Returns:
        Dictionary with verification result including verdict, confidence_score, citations, and metadata
    """
    # Verification logic for VerifAI agent-x402 service
    start_time = time.perf_counter()
    logger.info("verify.start claim=%s", claim)

    # Reset token tracking for this request
    token_tracker.reset()
    manual_review = False

    try:
        # STEP 0: Philosophical Claim Pre-Filter
        # Catches normative/value judgments before expensive multi-agent debate
        is_philosophical, filter_reason = is_philosophical_claim(claim)
        if is_philosophical:
            logger.info("verify.pre_filtered reason=%s", filter_reason)
            response = get_philosophical_response(claim, filter_reason)
            
            # Log performance (zero LLM costs since we skipped debate)
            execution_time = time.perf_counter() - start_time
            try:
                PerformanceLogger.log_request(
                    claim=claim,
                    verdict=response["verdict"],
                    confidence_score=response["confidence_score"],
                    prover_tokens={"input": 0, "output": 0, "model": "N/A"},
                    debunker_tokens={"input": 0, "output": 0, "model": "N/A"},
                    judge_tokens={"input": 0, "output": 0, "model": "N/A"},
                    search_count=0,
                    execution_time=execution_time,
                    was_refunded=True  # Always refund philosophical claims
                )
            except Exception as log_error:
                logger.warning("performance_log.failed err=%s", log_error)
            
            return response
        
        # Detect if this is a prediction or factual claim
        is_prediction = any(keyword in claim.lower() for keyword in PREDICTION_KEYWORDS)
        logger.info("claim.type=%s", "prediction" if is_prediction else "factual")

        # 1. Gather sources (fail safe if Exa is down)
        try:
            sources, text_blobs = await search_and_retrieve_sources(
                claim,
                timeout_seconds=EXA_SEARCH_TIMEOUT_SECONDS
            )
        except Exception as exa_error:
            logger.error("sources.fetch.failed err=%s", exa_error)
            return {
                "verdict": "Error",
                "confidence_score": 0.0,
                "reason": "Source retrieval failed",
                "summary": "Unable to verify claim because sources could not be retrieved.",
                "audit_trail": f"Source fetch error: {exa_error}",
                "claim_type": "prediction" if is_prediction else "factual",
                "manual_review": True
            }

        weights = calculate_source_weights(sources)

        # 2. Run Prover and Debunker in parallel with timeouts
        logger.info("debate.start")
        prover_task = run_prover_agent(claim, text_blobs, is_prediction)
        debunker_task = run_debunker_agent(claim, text_blobs, is_prediction)

        try:
            prover_argument, debunker_argument = await asyncio.wait_for(
                asyncio.gather(prover_task, debunker_task, return_exceptions=True),
                timeout=DEBATE_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            logger.error("debate.timeout")
            return {
                "verdict": "Error",
                "confidence_score": 0.0,
                "reason": "Debate timed out",
                "summary": "Unable to verify claim because model calls timed out.",
                "audit_trail": "Debate timeout",
                "claim_type": "prediction" if is_prediction else "factual",
                "manual_review": True
            }

        manual_review = False
        if isinstance(prover_argument, Exception):
            logger.warning("prover.failed err=%s", prover_argument)
            prover_argument = "Unable to generate prover argument."
            manual_review = True
        if isinstance(debunker_argument, Exception):
            logger.warning("debunker.failed err=%s", debunker_argument)
            debunker_argument = "Unable to generate debunker argument."
            manual_review = True

        logger.info(
            "debate.done prover_len=%d debunker_len=%d",
            len(prover_argument),
            len(debunker_argument),
        )

        # 3. Judge reviews both arguments and raw sources
        result = await run_judge_agent(
            claim,
            text_blobs,
            weights,
            prover_argument,
            debunker_argument,
            is_prediction,
        )

        verdict = result.get("verdict", "Error")
        confidence = result.get("confidence_score", 0.0)
        summary = result.get("summary", "Analysis complete")

        # Decision matrix for automatic refunds based on confidence:
        # < 0.40: Inconclusive (AI cannot find answer) → Full refund
        # 0.40-0.65: Low confidence (AI found answer but uncertain) → Standard settlement
        # > 0.65: High confidence → Standard settlement
        should_refund = confidence < CONFIDENCE_FLOOR_FOR_REFUND
        
        # HITL threshold: if confidence is low, flag manual_review
        if confidence < CONFIDENCE_THRESHOLD_FOR_MANUAL_REVIEW:
            manual_review = True
            # Distinguish between "Inconclusive" (can't find answer) vs just low confidence
            if should_refund:
                verdict = "Inconclusive" if not is_prediction else "Uncertain"

        # Track verdict for cost analysis (especially for inconclusive results)
        token_tracker.set_verdict(verdict)

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "verify.done verdict=%s confidence=%.2f ms=%.1f manual_review=%s",
            verdict,
            confidence,
            duration_ms,
            manual_review,
        )

        # Log performance metrics
        execution_time = time.perf_counter() - start_time
        try:
            tokens = token_tracker.get_all()
            PerformanceLogger.log_request(
                claim=claim,
                verdict=verdict,
                confidence_score=confidence,
                prover_tokens=tokens['prover'],
                debunker_tokens=tokens['debunker'],
                judge_tokens=tokens['judge'],
                search_count=len(sources),
                execution_time=execution_time,
                was_refunded=should_refund  # Track refund decisions
            )
        except Exception as log_error:
            logger.warning("performance_log.failed err=%s", log_error)

        return {
            "verdict": verdict,
            "confidence_score": confidence,
            "reasoning": judge_result.get("reasoning", summary),
            "evidence_for": judge_result.get("evidence_for", []),
            "evidence_against": judge_result.get("evidence_against", []),
            "citations": sources,
            "claim_type": "prediction" if is_prediction else "factual",
            "audit_trail": f"Multi-agent debate: Prover ({prover_argument[:80]}...) vs Debunker ({debunker_argument[:80]}...). Judge: {summary}",
            "summary": summary,
            "debate": {
                "prover": prover_argument,
                "debunker": debunker_argument
            },
            "manual_review": manual_review,
            "payment_status": "refunded_due_to_uncertainty" if should_refund else "settled"
        }
    except Exception as e:
        logger.exception("verify.failed err=%s", e)
        # System error = automatic refund
        return {
            "verdict": "Error",
            "confidence_score": 0.0,
            "reason": f"Verification error: {str(e)}",
            "summary": "Unable to verify claim due to service error.",
            "audit_trail": f"Error: {str(e)}",
            "claim_type": "unknown",
            "manual_review": True,
            "payment_status": "refunded_due_to_system_error"
        }
