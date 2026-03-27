"""
Tests for the Agent Service — schema validation and source-level pipeline tests.
"""

import pytest
import os
from pathlib import Path


# ═══════════════════════════════════════════════════════════════════════
# DiscoveryReport Schema Tests (direct file import)
# ═══════════════════════════════════════════════════════════════════════

SCHEMAS_PATH = str(
    (Path(__file__).resolve().parent.parent
     / "services" / "agent_service" / "models" / "schemas.py")
)

ORCHESTRATOR_PATH = str(
    (Path(__file__).resolve().parent.parent
     / "services" / "agent_service" / "services" / "orchestrator.py")
)


def _import_schemas():
    """Import schemas by file path to avoid namespace resolution issues."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("agent_schemas", SCHEMAS_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestDiscoveryReportSchema:
    """Test that the DiscoveryReport Pydantic schema works correctly."""

    @pytest.fixture(autouse=True)
    def load_schemas(self):
        self.schemas = _import_schemas()

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

    def test_pipeline_calls_all_stages(self):
        """Verify all 5 pipeline stages are called within run_discovery."""
        # Extract just the run_discovery method body
        start = self.source.index("async def run_discovery")
        end = self.source.index("async def _extract_keywords")
        method_body = self.source[start:end]

        assert "_extract_keywords" in method_body
        assert "search_papers" in method_body
        assert "batch_download_papers" in method_body
        assert "batch_import_papers" in method_body
        assert "_generate_report" in method_body

    def test_fallback_on_no_papers(self):
        """Verify no-papers fallback returns 'No papers found'."""
        assert "No papers found" in self.source
