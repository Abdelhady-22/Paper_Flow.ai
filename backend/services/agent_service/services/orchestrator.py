"""
Agent Service — CrewAI Orchestrator

Orchestrates the full agent pipeline :
keyword_agent → search_agent → download_agent → import_agent → report_agent

Uses CrewAI for sequential multi-agent execution.
Falls back to direct pipeline execution when CrewAI is not available.
"""

import uuid
from typing import Optional, List
from uuid import UUID

from services.agent_service.models.schemas import (
    DiscoveryResponse,
    DiscoveredPaper,
    DiscoveryReport,
)
from services.agent_service.utils.semantic_scholar import search_papers
from services.agent_service.utils.pdf_downloader import batch_download_papers
from services.agent_service.utils.import_pipeline import batch_import_papers
from shared.llm_client.client import LLMClient
from shared.llm_client.providers import get_provider_model
from shared.progress.tracker import progress_tracker
from shared.logger.logger import get_logger
from settings import settings

logger = get_logger(__name__)


class AgentOrchestrator:
    """
    Orchestrates the full CrewAI discovery pipeline.

    Pipeline: query → keywords → search → download → import → report
    """

    async def run_discovery(
        self,
        query: str,
        user_id: str,
        max_papers: int = 5,
        auto_import: bool = True,
    ) -> DiscoveryReport:
        """
        Full discovery pipeline:
        1. keyword_agent: Extract keywords from query via LLM
        2. search_agent: Search Semantic Scholar
        3. download_agent: Download PDFs (if auto_import=True)
        4. import_agent: OCR → chunk → embed → Qdrant + PostgreSQL
        5. report_agent: Generate structured report
        """
        task_id = str(uuid.uuid4())

        try:
            # ── Step 1: Keyword Extraction ────────────────────
            await progress_tracker.publish(
                task_id, "keyword_extraction", 0.1, "Extracting search keywords..."
            )
            keywords = await self._extract_keywords(query)
            logger.info("keywords_extracted", query=query, keywords=keywords)

            # ── Step 2: Search Semantic Scholar ────────────────
            await progress_tracker.publish(
                task_id, "searching", 0.2, f"Searching Semantic Scholar for: {keywords}"
            )
            papers = await search_papers(
                query=keywords, max_results=max_papers
            )
            logger.info("search_complete", papers_found=len(papers))

            if not papers:
                return DiscoveryReport(
                    task_id=task_id,
                    query=query,
                    keywords=keywords,
                    papers_found=0,
                    papers_downloaded=0,
                    papers_imported=0,
                    papers=[],
                    report="No papers found matching your query. Try different keywords.",
                )

            downloaded = []
            imported = []

            if auto_import:
                # ── Step 3: Download PDFs ─────────────────────
                await progress_tracker.publish(
                    task_id, "downloading", 0.4,
                    f"Downloading {len(papers)} papers..."
                )

                # Build download list from papers with URLs
                download_list = [
                    {"url": p.url, "title": p.title}
                    for p in papers
                    if p.url
                ]

                downloaded = await batch_download_papers(
                    papers=download_list,
                    user_id=user_id,
                )

                successful_downloads = [d for d in downloaded if d.get("success")]
                logger.info(
                    "download_complete",
                    total=len(download_list),
                    successful=len(successful_downloads),
                )

                # ── Step 4: Import into Knowledge Base ────────
                if successful_downloads:
                    await progress_tracker.publish(
                        task_id, "importing", 0.6,
                        f"Importing {len(successful_downloads)} papers into knowledge base..."
                    )

                    imported = await batch_import_papers(
                        papers=successful_downloads,
                        user_id=user_id,
                        task_id=task_id,
                    )

            # ── Step 5: Generate Report ───────────────────────
            await progress_tracker.publish(
                task_id, "reporting", 0.9, "Generating discovery report..."
            )

            report = await self._generate_report(
                query=query,
                keywords=keywords,
                papers=papers,
                downloaded=downloaded,
                imported=imported,
            )

            await progress_tracker.publish(
                task_id, "complete", 1.0, "Discovery complete!"
            )

            return DiscoveryReport(
                task_id=task_id,
                query=query,
                keywords=keywords,
                papers_found=len(papers),
                papers_downloaded=sum(1 for d in downloaded if d.get("success")),
                papers_imported=sum(1 for i in imported if i.get("success")),
                papers=papers,
                downloaded=downloaded,
                imported=imported,
                report=report,
            )

        except Exception as e:
            logger.error("discovery_pipeline_error", query=query, error=str(e))
            await progress_tracker.publish(
                task_id, "error", 0.0, f"Discovery failed: {str(e)}"
            )
            raise

    async def _extract_keywords(self, query: str) -> str:
        """Use LLM to extract precise search keywords from a natural language query."""
        try:
            provider_model = get_provider_model(settings.LLM_PROVIDER)
            client = LLMClient(
                provider=provider_model,
                timeout=settings.LLM_TIMEOUT,
                max_retries=settings.LLM_MAX_RETRIES,
            )
            response = await client.complete(
                system=(
                    "You are a keyword extraction expert. "
                    "Extract 3-5 precise academic search keywords from the user's query. "
                    "Return ONLY the keywords separated by spaces. No explanations."
                ),
                prompt=f"Extract search keywords from: {query}",
                temperature=0.1,
                max_tokens=100,
            )
            return response.strip()
        except Exception:
            # Fallback: use original query
            return query

    async def _generate_report(
        self,
        query: str,
        keywords: str,
        papers: list,
        downloaded: list,
        imported: list,
    ) -> str:
        """Generate a structured discovery report using report_agent logic."""
        successful_imports = sum(1 for i in imported if i.get("success"))
        failed_imports = sum(1 for i in imported if not i.get("success"))

        report_lines = [
            f"## Discovery Report",
            f"",
            f"**Query**: {query}",
            f"**Keywords**: {keywords}",
            f"**Papers Found**: {len(papers)}",
            f"**Papers Downloaded**: {sum(1 for d in downloaded if d.get('success'))}",
            f"**Papers Imported**: {successful_imports}",
            f"**Failed Imports**: {failed_imports}",
            f"",
            f"### Papers Found",
        ]

        for i, paper in enumerate(papers, 1):
            report_lines.append(
                f"{i}. **{paper.title}** "
                f"({paper.year or 'N/A'}) — "
                f"{', '.join(paper.authors[:3])}"
                f"{' ...' if len(paper.authors) > 3 else ''}"
                f" | Citations: {paper.citations or 0}"
            )

        return "\n".join(report_lines)
