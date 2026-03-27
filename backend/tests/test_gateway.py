"""
Tests for the FastAPI Gateway — health check, root, CORS, and route mounting.

Uses importlib to ensure the gateway.main module is importable before patching.
"""

import sys
import pytest
import importlib
from unittest.mock import AsyncMock, patch


def _import_gateway_main():
    """
    Force-import gateway.main so patch() can resolve it.
    gateway/__init__.py doesn't expose `main`, so we need importlib.
    """
    return importlib.import_module("gateway.main")


# ═══════════════════════════════════════════════════════════════════════
# Gateway Health & Root Tests
# ═══════════════════════════════════════════════════════════════════════

class TestGatewayEndpoints:
    """Test the gateway health and root endpoints."""

    @pytest.fixture(autouse=True)
    def setup_client(self):
        """Create a TestClient for the gateway app."""
        gateway_main = _import_gateway_main()
        from fastapi.testclient import TestClient
        self.client = TestClient(gateway_main.app, raise_server_exceptions=False)
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
    def setup_app(self):
        gateway_main = _import_gateway_main()
        self.app = gateway_main.app
        yield

    def _route_paths(self):
        return [r.path for r in self.app.routes]

    def test_routes_include_ocr(self):
        assert any("/api/v1/ocr" in r for r in self._route_paths())

    def test_routes_include_summarize(self):
        assert any("/api/v1/summary" in r or "/api/v1/summarize" in r for r in self._route_paths())

    def test_routes_include_translate(self):
        assert any("/api/v1/translate" in r or "/api/v1/translation" in r for r in self._route_paths())

    def test_routes_include_chat(self):
        assert any("/api/v1/chat" in r for r in self._route_paths())

    def test_routes_include_voice(self):
        assert any("/api/v1/voice" in r or "/api/v1/tts" in r or "/api/v1/stt" in r for r in self._route_paths())

    def test_routes_include_export(self):
        assert any("/api/v1/export" in r for r in self._route_paths())

    def test_routes_include_agent(self):
        assert any("/api/v1/agent" in r or "/api/v1/discover" in r for r in self._route_paths())

    def test_routes_include_qa(self):
        assert any("/api/v1/qa" in r for r in self._route_paths())
