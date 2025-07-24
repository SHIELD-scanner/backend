"""Tests for health API module."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestHealthAPI:

    """Test class for health API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_health_endpoint_success(self, client):
        """Test health endpoint returns success."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        # Check response structure - actual API returns "ok"
        assert "status" in data
        assert data["status"] == "ok"
        assert "message" in data
        assert "version" in data

    def test_health_endpoint_response_format(self, client):
        """Test health endpoint response format."""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        data = response.json()
        assert isinstance(data, dict)

    def test_health_endpoint_available(self, client):
        """Test that health endpoint is available and accessible."""
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

    def test_health_endpoint_consistency(self, client):
        """Test health endpoint returns consistent results."""
        # Make multiple requests
        responses = [client.get("/health") for _ in range(3)]

        # All should be successful
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"

    def test_health_endpoint_no_authentication_required(self, client):
        """Test health endpoint doesn't require authentication."""
        # Health endpoints should be publicly accessible
        response = client.get("/health")

        # Should not return 401 Unauthorized or 403 Forbidden
        assert response.status_code != 401
        assert response.status_code != 403
        assert response.status_code == 200
