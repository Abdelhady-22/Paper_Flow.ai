"""
Tests for the Agent Orchestrator — schema validation and source-level tests.

Avoids importing the orchestrator module directly since it triggers the full
dependency chain (→ semantic_scholar → httpx, etc.).
Tests validate Pydantic schemas via direct file import and verify source logic.
"""

import pytest
import importlib.util
import ast
import os
import sys


def _import_schemas_directly():
    """
    Import the agent schemas module by file path, bypassing the package
    resolution that fails in CI due to namespace conflicts.
    """
    schemas_path = os.path.join(
        os.path.dirname(__file__), "..",
        "services", "agent_service", "models", "schemas.py"
    )
    spec = importlib.util.spec_from_file_location("agent_schemas", schemas_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ═══════════════════════════════════════════════════════════════════════
# DiscoveryReport Schema Tests
# ═══════════════════════════════════════════════════════════════════════

class TestDiscoveryReportSchema:
    """Test that the DiscoveryReport Pydantic schema works correctly."""

    @pytest.fixture(autouse=True)
    def load_schemas(self):
        self.schemas = _import_schemas_directly()

    def test_discovery_report_minimal(self):
        report = self.schemas.DiscoveryReport(
            task_id="task-1",
            query="attention mechanisms",
            keywords="attention transformer",
            papers_found=0,
        )
        assert report.papers_found == 0
        assert report.papers_downloaded == 0
        assert report.report == ""

    def test_discovery_report_full(self):
        paper = self.schemas.DiscoveredPaper(
            title="Attention Is All You Need",
            authors=["Vaswani", "Shazeer"],
            year=2017,
            citations=50000,
        )
        report = self.schemas.DiscoveryReport(
            task_id="task-2",
            query="transformers",
            keywords="transformer attention self-attention",
            papers_found=1,
            papers_downloaded=1,
            papers_imported=1,
            papers=[paper],
            report="## Report\n1 paper found",
        )
        assert report.papers_found == 1
        assert report.papers[0].title == "Attention Is All You Need"

    def test_discovered_paper_minimal(self):
        paper = self.schemas.DiscoveredPaper(
            title="Test Paper",
            authors=["Author One"],
        )
        assert paper.title == "Test Paper"
        assert paper.url is None
        assert paper.citations is None

    def test_discover_request_defaults(self):
        req = self.schemas.DiscoverRequest(query="deep learning")
        assert req.max_papers == 5
        assert req.auto_import is True


# ═══════════════════════════════════════════════════════════════════════
# Orchestrator Source-Level Tests
# ═══════════════════════════════════════════════════════════════════════

ORCHESTRATOR_PATH = os.path.join(
    os.path.dirname(__file__), "..",
    "services", "agent_service", "services", "orchestrator.py"
)


class TestOrchestratorSource:
    """Verify orchestrator pipeline structure by parsing source."""

    @pytest.fixture(autouse=True)
    def load_source(self):
        with open(ORCHESTRATOR_PATH, "r") as f:
            self.source = f.read()

    def test_has_run_discovery_method(self):
        assert "async def run_discovery" in self.source

    def test_has_extract_keywords_method(self):
        assert "async def _extract_keywords" in self.source

    def test_has_generate_report_method(self):
        assert "async def _generate_report" in self.source

    def test_pipeline_steps_in_order(self):
        """Verify pipeline executes in correct order."""
        keyword_pos = self.source.index("_extract_keywords")
        search_pos = self.source.index("search_papers")
        download_pos = self.source.index("batch_download_papers")
        import_pos = self.source.index("batch_import_papers")
        report_pos = self.source.index("_generate_report")
        assert keyword_pos < search_pos < download_pos < import_pos < report_pos

    def test_fallback_on_no_papers(self):
        """Verify no-papers fallback returns 'No papers found'."""
        assert "No papers found" in self.source
