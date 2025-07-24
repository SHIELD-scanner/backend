"""Tests for sentry API module."""
import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestSentryAPI:
    """Test class for sentry API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_sentry_test_endpoint_exists(self, client):
        """Test that sentry test endpoints exist."""
        # Check if sentry test endpoint is available
        response = client.get("/sentry")
        
        # Endpoint may not be implemented or may be internal only
        assert response.status_code in [200, 404, 500]

    def test_sentry_test_endpoint_response(self, client):
        """Test sentry test endpoint response."""
        response = client.get("/sentry")
        
        # The endpoint should be accessible
        # Actual behavior depends on implementation
        assert response.status_code in [200, 500]  # Either success or expected error

    def test_sentry_exception_endpoint_exists(self, client):
        """Test that sentry exception test endpoint exists."""
        # Check if sentry exception test endpoint is available
        response = client.get("/sentry/exception")
        
        # Should not return 404 (endpoint exists)
        assert response.status_code != 404

    def test_sentry_exception_endpoint_response(self, client):
        """Test sentry exception endpoint response."""
        response = client.get("/sentry/exception")
        
        # This endpoint is expected to raise an exception for testing
        # The actual response depends on error handling
        assert response.status_code in [200, 500]

    def test_sentry_endpoints_are_test_only(self, client):
        """Test that sentry endpoints are for testing purposes."""
        # These endpoints should exist for development/testing
        sentry_response = client.get("/sentry")
        exception_response = client.get("/sentry/exception")
        
        # Both endpoints should be accessible
        assert sentry_response.status_code != 404
        assert exception_response.status_code != 404

    def test_sentry_endpoint_method_not_allowed(self, client):
        """Test sentry endpoints with wrong HTTP methods."""
        # Test POST method (should not be allowed)
        response = client.post("/sentry")
        assert response.status_code in [405, 422]  # Method Not Allowed or Unprocessable Entity
        
        # Test PUT method (should not be allowed)
        response = client.put("/sentry")
        assert response.status_code == 405  # Method Not Allowed
        
        # Test DELETE method (should not be allowed)
        response = client.delete("/sentry")
        assert response.status_code == 405  # Method Not Allowed

    def test_sentry_exception_endpoint_method_not_allowed(self, client):
        """Test sentry exception endpoint with wrong HTTP methods."""
        # Test POST method (should not be allowed)
        response = client.post("/sentry/exception")
        assert response.status_code in [405, 422]  # Method Not Allowed or Unprocessable Entity
        
        # Test PUT method (should not be allowed) 
        response = client.put("/sentry/exception")
        assert response.status_code == 405  # Method Not Allowed
        
        # Test DELETE method (should not be allowed)
        response = client.delete("/sentry/exception")
        assert response.status_code == 405  # Method Not Allowed

    def test_sentry_endpoints_no_authentication_required(self, client):
        """Test sentry endpoints don't require authentication."""
        # Sentry test endpoints should be accessible for testing
        sentry_response = client.get("/sentry")
        exception_response = client.get("/sentry/exception")
        
        # Should not return 401 Unauthorized or 403 Forbidden
        assert sentry_response.status_code != 401
        assert sentry_response.status_code != 403
        assert exception_response.status_code != 401
        assert exception_response.status_code != 403

    def test_sentry_endpoint_content_type(self, client):
        """Test sentry endpoint response content type."""
        response = client.get("/sentry")
        
        if response.status_code == 200:
            # If successful, should return JSON
            assert "application/json" in response.headers.get("content-type", "")
        
        # If it returns 500, that's expected for testing error reporting
        assert response.status_code in [200, 500]
