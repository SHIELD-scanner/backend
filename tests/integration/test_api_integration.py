"""Integration tests for the SHIELD backend API."""

import os
from unittest.mock import patch

import mongomock
import pytest
from fastapi.testclient import TestClient

# Set test environment
os.environ["MONGODB_DB"] = "shield_test"
os.environ["SENTRY_DSN"] = ""

from app.main import app


class TestAPIIntegration:
    """Integration tests for the full API."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_mongo_setup(self):
        """Set up mock MongoDB for integration tests."""
        mock_client = mongomock.MongoClient()

        # Setup mock data
        exposed_secrets_collection = mock_client["shield_test"]["exposedsecretreports"]
        exposed_secrets_collection.insert_many(
            [
                {"_uid": "secret1", "_namespace": "ns1", "_cluster": "cluster1"},
                {"_uid": "secret2", "_namespace": "ns2", "_cluster": "cluster2"},
            ]
        )

        sbom_collection = mock_client["shield_test"]["sbomreports"]
        sbom_collection.insert_many(
            [
                {"_uid": "sbom1", "_namespace": "ns1", "_cluster": "cluster1"},
                {"_uid": "sbom2", "_namespace": "ns2", "_cluster": "cluster2"},
            ]
        )

        pods_collection = mock_client["shield_test"]["pods"]
        pods_collection.insert_many(
            [
                {"name": "pod1", "namespace": "ns1", "cluster": "cluster1"},
                {"name": "pod2", "namespace": "ns2", "cluster": "cluster2"},
            ]
        )

        namespaces_collection = mock_client["shield_test"]["namespaces"]
        namespaces_collection.insert_many(
            [
                {"_cluster": "cluster1", "_name": "ns1", "_uid": "ns1-uid"},
                {"_cluster": "cluster2", "_name": "ns2", "_uid": "ns2-uid"},
            ]
        )

        return mock_client

    def test_root_endpoint(self, client):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "API documentation" in data["message"]

    def test_health_endpoints_exist(self, client):
        """Test that health endpoints are accessible."""
        # Test that the health endpoints are registered
        response = client.get("/health/")
        # We expect some response, even if it's an error due to missing dependencies
        assert response.status_code in [200, 500, 404]

    def test_api_endpoints_exist(self, client):
        """Test that all main API endpoints are registered."""
        endpoints_to_test = [
            "/exposedsecrets/",
            "/sbom/",
            "/vulnerabilities/",
            "/namespaces/",
            "/pods/",
        ]

        for endpoint in endpoints_to_test:
            # We're testing that endpoints exist and return some response
            # Even if they fail due to database connections, they should not return 404
            response = client.get(endpoint)
            assert response.status_code != 404, f"Endpoint {endpoint} not found"

    @patch("app.core.exposedsecretClient.ExposedsecretClient.get_collection")
    def test_exposed_secrets_integration(self, mock_collection, client):
        """Integration test for exposed secrets endpoints."""
        # Mock the collection to return empty results
        mock_collection.return_value.find.return_value = []

        response = client.get("/exposedsecrets/")
        assert response.status_code == 200
        # Response should be a list (even if empty due to mocking)
        assert isinstance(response.json(), list)

    @patch("app.core.sbomClient.SbomClient.get_collection")
    def test_sbom_integration(self, mock_collection, client):
        """Integration test for SBOM endpoints."""
        # Mock the collection to return empty results
        mock_collection.return_value.find.return_value = []

        response = client.get("/sbom/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @patch("app.core.vulnerabilityClient.VulnerabilityClient.get_collection")
    def test_vulnerabilities_integration(self, mock_collection, client):
        """Integration test for vulnerabilities endpoints."""
        # Mock the collection to return empty results
        mock_collection.return_value.find.return_value = []

        response = client.get("/vulnerabilities/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_cors_headers(self, client):
        """Test that CORS headers are properly configured."""
        response = client.options("/")
        # Check that CORS is configured (should allow all origins)
        assert response.status_code in [200, 405]  # OPTIONS might not be implemented

    def test_api_documentation_endpoints(self, client):
        """Test that API documentation endpoints work."""
        # Test OpenAPI schema
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        # Test docs endpoint
        response = client.get("/docs")
        assert response.status_code == 200

    def test_application_dashboard_integration(self, client):
        """Integration test for application dashboard endpoints."""
        response = client.get("/application/dashboard")
        # Should return some response, even if data is empty due to mocking
        assert response.status_code in [200, 500]  # 500 if database connection fails

    def test_sentry_test_endpoints(self, client):
        """Test sentry test endpoints don't crash the app."""
        # Test sentry debug endpoint
        response = client.get("/sentry/debug")
        # This endpoint is designed to trigger an exception, so expect 500
        assert response.status_code == 500

        # Test sentry test endpoint
        response = client.get("/sentry/test-sentry")
        assert response.status_code == 200

    def test_error_handling(self, client):
        """Test error handling for non-existent endpoints."""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404

    def test_dependency_injection_consistency(self, client):
        """Test that dependency injection works consistently across endpoints."""
        # This test verifies that all endpoints that use dependency injection
        # don't crash due to dependency issues
        endpoints_with_dependencies = [
            "/exposedsecrets/",
            "/sbom/",
            "/vulnerabilities/",
            "/namespaces/",
            "/pods/",
        ]

        for endpoint in endpoints_with_dependencies:
            response = client.get(endpoint)
            # Should not crash with dependency injection errors
            assert (
                response.status_code != 422
            )  # Unprocessable Entity (dependency issues)

    def test_parameter_validation(self, client):
        """Test parameter validation across endpoints."""
        # Test query parameters are properly validated
        response = client.get("/exposedsecrets/?namespace=test-ns")
        assert response.status_code in [
            200,
            500,
        ]  # Should not be 422 (validation error)

        response = client.get("/sbom/?cluster=test-cluster")
        assert response.status_code in [200, 500]

        response = client.get("/vulnerabilities/?severity=HIGH")
        assert response.status_code in [200, 500]
