"""Tests for application API module."""

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.api.application import get_vulnerability_client
from app.main import app


class TestApplicationAPI:
    """Test class for application API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_application_sidebar_endpoint_exists(self, client):
        """Test that application sidebar endpoint exists."""
        response = client.get("/application/sidebar")
        assert response.status_code == 200

    def test_application_dashboard_endpoint_exists(self, client):
        """Test that application dashboard endpoint exists."""
        response = client.get("/application/dashboard")
        assert response.status_code == 200

    def test_sidebar_endpoint_response_format(self, client):
        """Test sidebar endpoint response format."""
        mock_client = MagicMock()
        mock_client.get_all.return_value = [MagicMock(), MagicMock()]

        # Override the dependency
        client.app.dependency_overrides[get_vulnerability_client] = lambda: mock_client

        try:
            response = client.get("/application/sidebar")
        finally:
            # Clean up the override
            client.app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()

        assert "vulnerability_total" in data
        assert data["vulnerability_total"] == 2
        mock_client.get_all.assert_called_once()

    def test_sidebar_with_query_parameters(self, client):
        """Test sidebar endpoint with query parameters."""
        response = client.get(
            "/application/sidebar?cluster=test-cluster&namespace=test-ns"
        )
        assert response.status_code == 200
        data = response.json()
        assert "vulnerability_total" in data
