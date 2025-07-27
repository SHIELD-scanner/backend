"""Tests for application API module."""

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.application import get_vulnerability_client, get_pod_client
from app.main import app


class TestApplicationAPI:

    """Test class for application API endpoints."""

    @pytest.fixture
    def mock_vulnerability_client(self):
        """Create a mock vulnerability client."""
        mock_client = MagicMock()
        mock_client.get_all.return_value = [
            MagicMock(severity="CRITICAL"),
            MagicMock(severity="HIGH"),
            MagicMock(severity="MEDIUM"),
        ]
        return mock_client

    @pytest.fixture 
    def mock_pod_client(self):
        """Create a mock pod client."""
        mock_client = MagicMock()
        mock_client.get_all.return_value = [
            MagicMock(namespace="test-ns1", cluster="test-cluster1"),
            MagicMock(namespace="test-ns2", cluster="test-cluster2"),
        ]
        return mock_client

    @pytest.fixture
    def test_client(self, mock_vulnerability_client, mock_pod_client):
        """Create test client with dependency overrides."""
        app.dependency_overrides[get_vulnerability_client] = lambda: mock_vulnerability_client
        app.dependency_overrides[get_pod_client] = lambda: mock_pod_client
        yield TestClient(app)
        app.dependency_overrides.clear()

    def test_application_sidebar_endpoint_exists(self, test_client, mock_vulnerability_client):
        """Test that application sidebar endpoint exists."""
        response = test_client.get("/application/sidebar")
        assert response.status_code == 200

    def test_application_dashboard_endpoint_exists(self, test_client, mock_vulnerability_client, mock_pod_client):
        """Test that application dashboard endpoint exists."""
        response = test_client.get("/application/dashboard")
        assert response.status_code == 200

    def test_sidebar_endpoint_response_format(self, test_client, mock_vulnerability_client):
        """Test sidebar endpoint response format."""
        response = test_client.get("/application/sidebar")

        assert response.status_code == 200
        data = response.json()

        assert "vulnerability_total" in data
        assert data["vulnerability_total"] == 3  # Updated to match mock data
        mock_vulnerability_client.get_all.assert_called()

    def test_sidebar_with_query_parameters(self, test_client, mock_vulnerability_client):
        """Test sidebar endpoint with query parameters."""
        response = test_client.get(
            "/application/sidebar?cluster=test-cluster&namespace=test-ns"
        )
        assert response.status_code == 200
        data = response.json()
        assert "vulnerability_total" in data
