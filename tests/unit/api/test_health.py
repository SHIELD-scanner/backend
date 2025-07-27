"""Tests for health API module."""

from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.api.health import get_database_client
from app.main import app


class TestHealthAPI:

    """Test class for health API endpoints."""

    @pytest.fixture
    def mock_database_client(self):
        """Create a mock database client."""
        return Mock()

    @pytest.fixture
    def client(self, mock_database_client):
        """Create test client with dependency override."""
        app.dependency_overrides[get_database_client] = lambda: mock_database_client
        yield TestClient(app)
        app.dependency_overrides.clear()

    def test_health_endpoint_success(self, client, mock_database_client):
        """Test health endpoint returns success."""
        # Mock successful database connection
        mock_database_client.client.list_database_names.return_value = ["test_db"]
        
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        # Check response structure - actual API returns "ok"
        assert "status" in data
        assert data["status"] == "ok"
        assert "message" in data
        assert "version" in data
        assert "database" in data
        assert data["database"] == "connected"

    def test_health_endpoint_response_format(self, client, mock_database_client):
        """Test health endpoint response format."""
        # Mock successful database connection
        mock_database_client.client.list_database_names.return_value = ["test_db"]
        
        response = client.get("/health")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        data = response.json()
        assert isinstance(data, dict)

    def test_health_endpoint_available(self, client, mock_database_client):
        """Test that health endpoint is available and accessible."""
        # Mock successful database connection
        mock_database_client.client.list_database_names.return_value = ["test_db"]
        
        response = client.get("/health")

        # Should not return 404 or 405
        assert response.status_code != 404
        assert response.status_code != 405
        assert response.status_code == 200

    def test_health_endpoint_method_not_allowed(self, client):
        """Test health endpoint with wrong HTTP method."""
        # Test POST method (should not be allowed)
        response = client.post("/health")
        assert response.status_code == 405  # Method Not Allowed

        # Test PUT method (should not be allowed)
        response = client.put("/health")
        assert response.status_code == 405  # Method Not Allowed

        # Test DELETE method (should not be allowed)
        response = client.delete("/health")
        assert response.status_code == 405  # Method Not Allowed

    def test_health_endpoint_consistency(self, client, mock_database_client):
        """Test health endpoint returns consistent results."""
        # Mock successful database connection
        mock_database_client.client.list_database_names.return_value = ["test_db"]
        
        # Make multiple requests
        responses = [client.get("/health") for _ in range(3)]

        # All should be successful
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"

    def test_health_endpoint_no_authentication_required(self, client, mock_database_client):
        """Test health endpoint doesn't require authentication."""
        # Mock successful database connection
        mock_database_client.client.list_database_names.return_value = ["test_db"]
        
        # Health endpoints should be publicly accessible
        response = client.get("/health")

        # Should not return 401 Unauthorized or 403 Forbidden
        assert response.status_code != 401
        assert response.status_code != 403
        assert response.status_code == 200
