"""
Tests for the Agent Orchestrator discovery pipeline.

Uses importlib to pre-load the orchestrator module so patch() can resolve targets.
"""

import pytest
import importlib
from unittest.mock import AsyncMock, patch, MagicMock


def _import_orchestrator():
    """Force-import the orchestrator module so patch() targets resolve."""
    return importlib.import_module("services.agent_service.services.orchestrator")


def _make_mock_paper():
    """Create a mock paper object with all required attributes."""
    paper = MagicMock()
    paper.title = "Attention Is All You Need"
    paper.year = 2017
    paper.authors = ["Vaswani", "Shazeer", "Parmar"]
    paper.citations = 50000
    paper.url = "https://example.com/paper.pdf"
    paper.abstract = "We propose the Transformer model."
    paper.paper_id = "paper-001"
    return paper


# ═══════════════════════════════════════════════════════════════════════
# AgentOrchestrator Tests
# ═══════════════════════════════════════════════════════════════════════

class TestAgentOrchestrator:
    """Tests for the CrewAI agent orchestrator pipeline."""

    @pytest.mark.asyncio
    async def test_discovery_no_papers_found(self):
        """When Semantic Scholar returns 0 papers, report should say so."""
        mod = _import_orchestrator()

        with patch.object(mod, "search_papers", new_callable=AsyncMock) as mock_search, \
             patch.object(mod, "progress_tracker") as mock_progress, \
             patch.object(mod, "get_provider_model", return_value="groq/llama3"), \
             patch.object(mod, "LLMClient") as mock_llm:

            mock_search.return_value = []
            mock_progress.publish = AsyncMock()

            mock_llm_instance = AsyncMock()
            mock_llm_instance.complete.return_value = "transformer attention"
            mock_llm.return_value = mock_llm_instance

            orch = mod.AgentOrchestrator()
            result = await orch.run_discovery(
                query="attention mechanisms in transformers",
                user_id="user-123",
                max_papers=5,
            )

            assert result.papers_found == 0
            assert "No papers found" in result.report

    @pytest.mark.asyncio
    async def test_keyword_extraction_fallback(self):
        """When LLM fails for keyword extraction, should fallback to original query."""
        mod = _import_orchestrator()

        with patch.object(mod, "get_provider_model", return_value="groq/llama3"), \
             patch.object(mod, "LLMClient") as mock_llm:

            mock_llm_instance = AsyncMock()
            mock_llm_instance.complete.side_effect = Exception("LLM error")
            mock_llm.return_value = mock_llm_instance

            orch = mod.AgentOrchestrator()
            result = await orch._extract_keywords("test query about AI")
            assert result == "test query about AI"

    @pytest.mark.asyncio
    async def test_discovery_with_papers_search_only(self):
        """Discovery with auto_import=False should search and report, not download."""
        mod = _import_orchestrator()

        mock_paper = _make_mock_paper()

        with patch.object(mod, "search_papers", new_callable=AsyncMock) as mock_search, \
             patch.object(mod, "progress_tracker") as mock_progress, \
             patch.object(mod, "get_provider_model", return_value="groq/llama3"), \
             patch.object(mod, "LLMClient") as mock_llm:

            mock_search.return_value = [mock_paper]
            mock_progress.publish = AsyncMock()

            mock_llm_instance = AsyncMock()
            mock_llm_instance.complete.return_value = "transformer attention"
            mock_llm.return_value = mock_llm_instance

            orch = mod.AgentOrchestrator()
            result = await orch.run_discovery(
                query="attention mechanisms",
                user_id="user-123",
                max_papers=1,
                auto_import=False,
            )

            assert result.papers_found == 1
            assert result.papers_downloaded == 0
            assert result.papers_imported == 0
            assert "Attention Is All You Need" in result.report
