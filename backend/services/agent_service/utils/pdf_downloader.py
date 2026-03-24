"""
Agent Service — PDF Downloader

Downloads discovered papers as PDFs using async httpx.
Handles retries, file validation, and secure storage.
Used by the download_agent in the CrewAI pipeline.
"""

import httpx
import uuid
from pathlib import Path
from shared.logger.logger import get_logger
from shared.error_handler.exceptions import PaperDiscoveryException
from settings import settings

logger = get_logger(__name__)


async def download_paper_pdf(
    pdf_url: str,
    title: str,
    user_id: str,
    max_retries: int = 3,
) -> dict:
    """
    Download a paper PDF from a given URL.

    Args:
        pdf_url: URL of the PDF to download
        title: Paper title (for logging and naming)
        user_id: User who initiated the discovery
        max_retries: Number of download retries

    Returns:
        Dict with paper_id, file_path, title, success status
    """
    paper_id = str(uuid.uuid4())
    download_dir = Path(settings.AGENT_DOWNLOAD_DIR) / user_id / paper_id
    download_dir.mkdir(parents=True, exist_ok=True)
    file_path = download_dir / "paper.pdf"

    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(
                timeout=60, follow_redirects=True
            ) as client:
                response = await client.get(pdf_url)
                response.raise_for_status()

                content = response.content

                # Validate it's actually a PDF
                if not content.startswith(b"%PDF"):
                    logger.warning(
                        "download_not_pdf",
                        url=pdf_url,
                        title=title,
                    )
                    return {
                        "paper_id": paper_id,
                        "title": title,
                        "success": False,
                        "error": "Downloaded file is not a valid PDF",
                    }

                # Write to disk
                file_path.write_bytes(content)

                logger.info(
                    "paper_downloaded",
                    paper_id=paper_id,
                    title=title,
                    size_bytes=len(content),
                )

                return {
                    "paper_id": paper_id,
                    "file_path": str(file_path),
                    "title": title,
                    "size_bytes": len(content),
                    "success": True,
                }

        except httpx.HTTPStatusError as e:
            logger.warning(
                "download_http_error",
                url=pdf_url,
                status=e.response.status_code,
                attempt=attempt + 1,
            )
        except httpx.TimeoutException:
            logger.warning(
                "download_timeout",
                url=pdf_url,
                attempt=attempt + 1,
            )
        except Exception as e:
            logger.error(
                "download_error",
                url=pdf_url,
                error=str(e),
                attempt=attempt + 1,
            )

    return {
        "paper_id": paper_id,
        "title": title,
        "success": False,
        "error": f"Failed to download after {max_retries} attempts",
    }


async def batch_download_papers(
    papers: list,
    user_id: str,
) -> list:
    """
    Download multiple papers concurrently using asyncio.gather.
    Implements batch processing from Section 22.

    Args:
        papers: List of dicts with 'url' and 'title' keys
        user_id: User who initiated the discovery

    Returns:
        List of download result dicts
    """
    import asyncio

    tasks = [
        download_paper_pdf(
            pdf_url=p.get("url", ""),
            title=p.get("title", "Unknown"),
            user_id=user_id,
        )
        for p in papers
        if p.get("url")
    ]

    if not tasks:
        return []

    results = await asyncio.gather(*tasks, return_exceptions=True)

    successful = []
    for result in results:
        if isinstance(result, Exception):
            logger.error("batch_download_exception", error=str(result))
        else:
            successful.append(result)

    logger.info(
        "batch_download_complete",
        total=len(tasks),
        successful=sum(1 for r in successful if r.get("success")),
        failed=sum(1 for r in successful if not r.get("success")),
    )

    return successful
