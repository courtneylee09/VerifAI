"""Search service: Exa integration for web source retrieval."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from exa_py import Exa

from config.settings import EXA_API_KEY, NEWSAPI_KEY, EXA_NUM_RESULTS, MAX_SOURCE_TEXT_LENGTH

logger = logging.getLogger(__name__)

# Initialize Exa client
exa = Exa(api_key=EXA_API_KEY)

# NewsAPI client (lazy initialization)
_newsapi_client = None


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


async def search_news_sources(claim: str, timeout_seconds: int = 20) -> tuple[list[str], list[str], list[datetime]]:
    """
    Retrieve real-time news sources using NewsAPI + Exa.
    
    Prioritizes recent news articles (last 48 hours) for breaking news verification.
    Falls back to Exa if NewsAPI is unavailable.
    
    Args:
        claim: The news claim to search for
        timeout_seconds: Timeout for the search operation
        
    Returns:
        Tuple of (sources_urls, text_blobs, published_dates)
        
    Raises:
        Exception: If search fails
    """
    from datetime import datetime as dt, timedelta
    
    try:
        # Try NewsAPI first (real-time news)
        if NEWSAPI_KEY:
            try:
                import httpx
                
                # Search last 48 hours for breaking news
                from_date = (dt.utcnow() - timedelta(hours=48)).strftime('%Y-%m-%d')
                
                async with httpx.AsyncClient(timeout=timeout_seconds) as client:
                    response = await client.get(
                        "https://newsapi.org/v2/everything",
                        params={
                            "q": claim,
                            "from": from_date,
                            "sortBy": "publishedAt",
                            "pageSize": EXA_NUM_RESULTS,
                            "apiKey": NEWSAPI_KEY,
                            "language": "en"
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        articles = data.get("articles", [])
                        
                        if articles:
                            sources = [art["url"] for art in articles if art.get("url")]
                            text_blobs = [
                                (art.get("title", "") + " " + art.get("description", "") + " " + art.get("content", ""))[:MAX_SOURCE_TEXT_LENGTH]
                                for art in articles
                            ]
                            published_dates = [
                                dt.fromisoformat(art["publishedAt"].replace("Z", "+00:00")) if art.get("publishedAt") else dt.utcnow()
                                for art in articles
                            ]
                            
                            logger.info("newsapi.sources.retrieved count=%d", len(sources))
                            return sources, text_blobs, published_dates
            except Exception as newsapi_error:
                logger.warning("newsapi.failed err=%s, falling back to exa", str(newsapi_error)[:200])
        
        # Fallback to Exa (general web search)
        sources, text_blobs = await search_and_retrieve_sources(claim, timeout_seconds)
        published_dates = [dt.utcnow()] * len(sources)  # No dates from Exa
        
        logger.info("exa.sources.retrieved count=%d (no newsapi)", len(sources))
        return sources, text_blobs, published_dates
        
    except Exception as e:
        logger.error("news.sources.fetch.failed err=%s", str(e)[:200])
        raise


def calculate_source_weights(sources: list[str], published_dates: Optional[list[datetime]] = None) -> list[float]:
    """
    Calculate weights for sources based on domain credibility and recency.
    
    Base weights:
    - Wikipedia: 0.5x (encyclopedic, not primary source)
    - News sites: 1.0x
    - Other: 1.0x
    
    Recency multipliers (for news verification):
    - Last 24 hours: 1.5x
    - Last 7 days: 1.2x
    - Older: 1.0x
    
    Args:
        sources: List of source URLs
        published_dates: Optional list of publication dates for recency weighting
        
    Returns:
        List of weights corresponding to each source
    """
    weights = []
    now = datetime.utcnow()
    
    for i, url in enumerate(sources):
        # Base weight
        if "wikipedia.org" in url.lower():
            base_weight = 0.5
        else:
            base_weight = 1.0
        
        # Recency multiplier (if dates provided)
        recency_multiplier = 1.0
        if published_dates and i < len(published_dates) and published_dates[i]:
            age = now - published_dates[i]
            if age <= timedelta(hours=24):
                recency_multiplier = 1.5  # Breaking news
            elif age <= timedelta(days=7):
                recency_multiplier = 1.2  # Recent news
        
        weights.append(base_weight * recency_multiplier)
    
    return weights
