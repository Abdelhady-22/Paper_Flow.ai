"""
Agent Service — Semantic Scholar API Integration

Searches for academic papers via the Semantic Scholar API.
Used by the CrewAI agent for paper discovery.
"""

import httpx
from typing import List, Optional
from services.agent_service.models.schemas import DiscoveredPaper
from shared.logger.logger import get_logger
from shared.error_handler.exceptions import PaperDiscoveryException
from settings import settings

logger = get_logger(__name__)

SEMANTIC_SCHOLAR_BASE = "https://api.semanticscholar.org/graph/v1"


async def search_papers(
    query: str,
    max_results: int = 5,
    fields: Optional[List[str]] = None,
) -> List[DiscoveredPaper]:
    """
    Search for papers on Semantic Scholar.

    Args:
        query: Search query
        max_results: Maximum number of results
        fields: API fields to return

    Returns:
        List of DiscoveredPaper objects
    """
    if fields is None:
        fields = ["title", "authors", "abstract", "year", "url", "citationCount", "paperId"]

    headers = {}
    if settings.SEMANTIC_SCHOLAR_API_KEY:
        headers["x-api-key"] = settings.SEMANTIC_SCHOLAR_API_KEY

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{SEMANTIC_SCHOLAR_BASE}/paper/search",
                params={
                    "query": query,
                    "limit": max_results,
                    "fields": ",".join(fields),
                },
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

        papers = []
        for item in data.get("data", []):
            authors = [a.get("name", "") for a in item.get("authors", [])]
            papers.append(
                DiscoveredPaper(
                    title=item.get("title", ""),
                    authors=authors,
                    abstract=item.get("abstract"),
                    year=item.get("year"),
                    url=item.get("url"),
                    paper_id=item.get("paperId"),
                    citations=item.get("citationCount"),
                )
            )

        logger.info("semantic_scholar_search", query=query, results=len(papers))
        return papers

    except httpx.HTTPStatusError as e:
        logger.error("semantic_scholar_http_error", status=e.response.status_code)
        raise PaperDiscoveryException("Paper search API returned an error.")
    except Exception as e:
        logger.error("semantic_scholar_error", error=str(e))
        raise PaperDiscoveryException("Paper search failed. Please try again.")
