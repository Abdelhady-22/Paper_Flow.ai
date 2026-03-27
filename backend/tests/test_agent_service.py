"""
Tests for the Agent Orchestrator discovery pipeline.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock


# ═══════════════════════════════════════════════════════════════════════
# AgentOrchestrator Tests
# ═══════════════════════════════════════════════════════════════════════

class TestAgentOrchestrator:
    """Tests for the CrewAI agent orchestrator pipeline."""

    @pytest.mark.asyncio
    async def test_discovery_no_papers_found(self):
        """When Semantic Scholar returns 0 papers, report should say so."""
        with patch("services.agent_service.services.orchestrator.search_papers", new_callable=AsyncMock) as mock_search, \
             patch("services.agent_service.services.orchestrator.progress_tracker") as mock_progress, \
             patch("services.agent_service.services.orchestrator.get_provider_model", return_value="groq/llama3"), \
             patch("services.agent_service.services.orchestrator.LLMClient") as mock_llm:

            mock_search.return_value = []
            mock_progress.publish = AsyncMock()

            # Mock keyword extraction
            mock_llm_instance = AsyncMock()
            mock_llm_instance.complete.return_value = "transformer attention"
            mock_llm.return_value = mock_llm_instance

            from services.agent_service.services.orchestrator import AgentOrchestrator

            orch = AgentOrchestrator()
            result = await orch.run_discovery(
                query="attention mechanisms in transformers",
                user_id="user-123",
                max_papers=5,
            )

            assert result.papers_found == 0
            assert "No papers found" in result.report

    @pytest.mark.asyncio
    async def test_keyword_extraction_fallback(self):
        """When LLM fails, keyword extraction should fallback to original query."""
        with patch("services.agent_service.services.orchestrator.get_provider_model", return_value="groq/llama3"), \
             patch("services.agent_service.services.orchestrator.LLMClient") as mock_llm:

            mock_llm_instance = AsyncMock()
            mock_llm_instance.complete.side_effect = Exception("LLM error")
            mock_llm.return_value = mock_llm_instance

            from services.agent_service.services.orchestrator import AgentOrchestrator

            orch = AgentOrchestrator()
            result = await orch._extract_keywords("test query about AI")
            assert result == "test query about AI"

    @pytest.mark.asyncio
    async def test_discovery_with_papers(self):
        """Full pipeline with mocked papers."""
        mock_paper = MagicMock()
        mock_paper.title = "Attention Is All You Need"
        mock_paper.year = 2017
        mock_paper.authors = ["Vaswani", "Shazeer", "Parmar"]
        mock_paper.citations = 50000
        mock_paper.url = "https://example.com/paper.pdf"

        with patch("services.agent_service.services.orchestrator.search_papers", new_callable=AsyncMock) as mock_search, \
             patch("services.agent_service.services.orchestrator.batch_download_papers", new_callable=AsyncMock) as mock_download, \
             patch("services.agent_service.services.orchestrator.batch_import_papers", new_callable=AsyncMock) as mock_import, \
             patch("services.agent_service.services.orchestrator.progress_tracker") as mock_progress, \
             patch("services.agent_service.services.orchestrator.get_provider_model", return_value="groq/llama3"), \
             patch("services.agent_service.services.orchestrator.LLMClient") as mock_llm:

            mock_search.return_value = [mock_paper]
            mock_download.return_value = [{"success": True, "path": "/tmp/paper.pdf"}]
            mock_import.return_value = [{"success": True}]
            mock_progress.publish = AsyncMock()

            mock_llm_instance = AsyncMock()
            mock_llm_instance.complete.return_value = "transformer attention"
            mock_llm.return_value = mock_llm_instance

            from services.agent_service.services.orchestrator import AgentOrchestrator

            orch = AgentOrchestrator()
            result = await orch.run_discovery(
                query="attention mechanisms",
                user_id="user-123",
                max_papers=1,
                auto_import=True,
            )

            assert result.papers_found == 1
            assert result.papers_downloaded == 1
            assert result.papers_imported == 1
            assert "Attention Is All You Need" in result.report
