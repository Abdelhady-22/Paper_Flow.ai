"""
Tests for the FastAPI Gateway — health check, root, CORS, and route mounting.
"""

import pytest
from unittest.mock import patch, AsyncMock


# ═══════════════════════════════════════════════════════════════════════
# Gateway Health & Root Tests
# ═══════════════════════════════════════════════════════════════════════

class TestGatewayEndpoints:
    """Test the gateway health and root endpoints."""

    @pytest.fixture(autouse=True)
    def setup_client(self):
        """Create a TestClient for the gateway app."""
        # Patch infrastructure init to avoid real connections
        with patch("gateway.main.init_qdrant", new_callable=AsyncMock), \
             patch("gateway.main.init_redis", new_callable=AsyncMock), \
             patch("gateway.main.close_db", new_callable=AsyncMock), \
             patch("gateway.main.close_qdrant", new_callable=AsyncMock), \
             patch("gateway.main.close_redis", new_callable=AsyncMock):
            from gateway.main import app
            from fastapi.testclient import TestClient
            self.client = TestClient(app, raise_server_exceptions=False)
            yield

    def test_health_check(self):
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "gateway"
        assert data["version"] == "1.0.0"

    def test_root_endpoint(self):
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Research Paper Assistant API"
        assert data["version"] == "1.0.0"
        assert data["docs"] == "/docs"

    def test_docs_ui_accessible(self):
        response = self.client.get("/docs")
        assert response.status_code == 200

    def test_redoc_accessible(self):
        response = self.client.get("/redoc")
        assert response.status_code == 200


# ═══════════════════════════════════════════════════════════════════════
# Route Mounting Verification
# ═══════════════════════════════════════════════════════════════════════

class TestRouteMounting:
    """Verify all service routes are mounted under /api/v1."""

    @pytest.fixture(autouse=True)
    def setup_client(self):
        with patch("gateway.main.init_qdrant", new_callable=AsyncMock), \
             patch("gateway.main.init_redis", new_callable=AsyncMock), \
             patch("gateway.main.close_db", new_callable=AsyncMock), \
             patch("gateway.main.close_qdrant", new_callable=AsyncMock), \
             patch("gateway.main.close_redis", new_callable=AsyncMock):
            from gateway.main import app
            self.app = app
            yield

    def test_routes_include_ocr(self):
        routes = [r.path for r in self.app.routes]
        assert any("/api/v1/ocr" in r for r in routes)

    def test_routes_include_summarize(self):
        routes = [r.path for r in self.app.routes]
        assert any("/api/v1/summary" in r or "/api/v1/summarize" in r for r in routes)

    def test_routes_include_translate(self):
        routes = [r.path for r in self.app.routes]
        assert any("/api/v1/translate" in r or "/api/v1/translation" in r for r in routes)

    def test_routes_include_chat(self):
        routes = [r.path for r in self.app.routes]
        assert any("/api/v1/chat" in r for r in routes)

    def test_routes_include_voice(self):
        routes = [r.path for r in self.app.routes]
        assert any("/api/v1/voice" in r or "/api/v1/tts" in r or "/api/v1/stt" in r for r in routes)

    def test_routes_include_export(self):
        routes = [r.path for r in self.app.routes]
        assert any("/api/v1/export" in r for r in routes)

    def test_routes_include_agent(self):
        routes = [r.path for r in self.app.routes]
        assert any("/api/v1/agent" in r or "/api/v1/discover" in r for r in routes)

    def test_routes_include_qa(self):
        routes = [r.path for r in self.app.routes]
        assert any("/api/v1/qa" in r for r in routes)
