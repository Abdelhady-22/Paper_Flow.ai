"""
Tests for the FastAPI Gateway — smoke tests that verify configuration
without importing the full application (which requires all service dependencies).

These tests verify the gateway configuration by checking the source file directly,
avoiding the heavy import chain (gateway → routes → services → PaddleOCR, etc.).
"""

import pytest
import ast
import os


# ═══════════════════════════════════════════════════════════════════════
# Gateway Configuration Tests (source-level, no import needed)
# ═══════════════════════════════════════════════════════════════════════

GATEWAY_MAIN_PATH = os.path.join(
    os.path.dirname(__file__), "..", "gateway", "main.py"
)


class TestGatewayConfiguration:
    """Verify gateway configuration by parsing the source file."""

    @pytest.fixture(autouse=True)
    def load_source(self):
        with open(GATEWAY_MAIN_PATH, "r") as f:
            self.source = f.read()
        self.tree = ast.parse(self.source)

    def test_health_endpoint_exists(self):
        """Verify /health endpoint is defined in gateway."""
        assert '"/health"' in self.source

    def test_root_endpoint_exists(self):
        """Verify root / endpoint is defined in gateway."""
        assert '"/"' in self.source or "'/' " in self.source

    def test_cors_middleware_configured(self):
        """Verify CORS middleware is added."""
        assert "CORSMiddleware" in self.source

    def test_api_version_prefix(self):
        """Verify routes are mounted under /api/v1."""
        assert "/api/v1" in self.source

    def test_all_service_routers_mounted(self):
        """Verify all 8 service routers are imported and mounted."""
        expected_routers = [
            "ocr_router",
            "summary_router",
            "translation_router",
            "chat_router",
            "voice_router",
            "export_router",
            "agent_router",
            "qa_router",
        ]
        for router_name in expected_routers:
            assert router_name in self.source, f"Missing router: {router_name}"

    def test_startup_shutdown_events(self):
        """Verify lifecycle events are configured."""
        assert "startup" in self.source
        assert "shutdown" in self.source

    def test_app_title(self):
        """Verify the app has a proper title."""
        assert "Research Paper Assistant" in self.source
