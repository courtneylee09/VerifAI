"""Search service: Exa integration for web source retrieval."""
import asyncio
import logging
from exa_py import Exa

from config.settings import EXA_API_KEY, EXA_NUM_RESULTS, MAX_SOURCE_TEXT_LENGTH

logger = logging.getLogger(__name__)

# Initialize Exa client
exa = Exa(api_key=EXA_API_KEY)


async def search_and_retrieve_sources(claim: str, timeout_seconds: int = 20) -> tuple[list[str], list[str]]:
    """
    Retrieve web sources and content using Exa API.
    
    Args:
        claim: The claim to search for
        timeout_seconds: Timeout for the search operation
        
    Returns:
        Tuple of (sources_urls, text_blobs)
        
    Raises:
        Exception: If search fails
    """
    try:
        search_results = await asyncio.wait_for(
            asyncio.to_thread(
                exa.search_and_contents,
                claim,
                num_results=EXA_NUM_RESULTS,
                text=True
            ),
            timeout=timeout_seconds
        )
        
        sources = [res.url for res in search_results.results]
        text_blobs = [
            res.text[:MAX_SOURCE_TEXT_LENGTH] if res.text else ""
            for res in search_results.results
        ]
        
        logger.info("sources.retrieved count=%d", len(sources))
        return sources, text_blobs
        
    except asyncio.TimeoutError:
        logger.error("sources.timeout timeout_seconds=%d", timeout_seconds)
        raise Exception(f"Source retrieval timed out after {timeout_seconds}s")
    except Exception as e:
        logger.error("sources.fetch.failed err=%s", str(e)[:200])
        raise


def calculate_source_weights(sources: list[str]) -> list[float]:
    """
    Calculate weights for sources (Wikipedia weighted at 0.5x, others at 1.0x).
    
    Args:
        sources: List of source URLs
        
    Returns:
        List of weights corresponding to each source
    """
    return [0.5 if "wikipedia.org" in url.lower() else 1.0 for url in sources]
