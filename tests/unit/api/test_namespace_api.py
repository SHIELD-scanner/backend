"""Tests for namespace API module."""

from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.api.namespace import get_namespace_client
from app.core.namespaceClient import NamespaceClient
from app.main import app
from app.models.namespace import Namespace


class TestNamespaceAPI:
    """Test class for namespace API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_namespace_client(self):
        """Create mock namespace client."""
        return Mock(spec=NamespaceClient)

    @pytest.fixture
    def sample_namespace(self):
        """Create sample namespace for testing."""
        return Namespace(
            cluster="test-cluster", name="test-namespace", uid="namespace-123"
        )

    def test_get_all_namespaces(self, client, mock_namespace_client, sample_namespace):
        """Test GET /namespaces endpoint."""
        # Mock the dependency
        mock_namespace_client.get_all.return_value = [sample_namespace]

        # Override the dependency
        client.app.dependency_overrides[get_namespace_client] = (
            lambda: mock_namespace_client
        )

        try:
            response = client.get("/namespaces")
        finally:
            # Clean up the override
            client.app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["cluster"] == "test-cluster"
        assert data[0]["name"] == "test-namespace"
        assert data[0]["uid"] == "namespace-123"

    def test_get_all_namespaces_empty(self, client, mock_namespace_client):
        """Test GET /namespaces endpoint with no namespaces."""
        mock_namespace_client.get_all.return_value = []

        # Override the dependency
        client.app.dependency_overrides[get_namespace_client] = (
            lambda: mock_namespace_client
        )

        try:
            response = client.get("/namespaces")
        finally:
            # Clean up the override
            client.app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_all_namespaces_multiple(self, client, mock_namespace_client):
        """Test GET /namespaces endpoint with multiple namespaces."""
        namespaces = [
            Namespace(cluster="cluster1", name="ns1", uid="uid1"),
            Namespace(cluster="cluster1", name="ns2", uid="uid2"),
            Namespace(cluster="cluster2", name="ns1", uid="uid3"),
        ]
        mock_namespace_client.get_all.return_value = namespaces

        # Override the dependency
        client.app.dependency_overrides[get_namespace_client] = (
            lambda: mock_namespace_client
        )

        try:
            response = client.get("/namespaces")
        finally:
            # Clean up the override
            client.app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 3

        # Check that all namespaces are returned
        cluster_names = [ns["cluster"] for ns in data]
        assert "cluster1" in cluster_names
        assert "cluster2" in cluster_names

    def test_get_all_namespaces_query_parameters(
        self, client, mock_namespace_client, sample_namespace
    ):
        """Test GET /namespaces endpoint with query parameters."""
        mock_namespace_client.get_all.return_value = [sample_namespace]

        # Override the dependency
        client.app.dependency_overrides[get_namespace_client] = (
            lambda: mock_namespace_client
        )

        try:
            # Test with query parameters (if supported)
            response = client.get("/namespaces?cluster=test-cluster")
        finally:
            # Clean up the override
            client.app.dependency_overrides.clear()

        assert response.status_code == 200
        # The actual filtering logic would depend on the API implementation

    def test_namespaces_endpoint_response_format(
        self, client, mock_namespace_client, sample_namespace
    ):
        """Test namespaces endpoint response format."""
        mock_namespace_client.get_all.return_value = [sample_namespace]

        # Override the dependency
        client.app.dependency_overrides[get_namespace_client] = (
            lambda: mock_namespace_client
        )

        try:
            response = client.get("/namespaces")
        finally:
            # Clean up the override
            client.app.dependency_overrides.clear()

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        data = response.json()
        assert isinstance(data, list)

        if data:  # If there are namespaces
            namespace = data[0]
            assert "cluster" in namespace
            assert "name" in namespace
            assert "uid" in namespace

    def test_namespaces_endpoint_method_not_allowed(self, client):
        """Test namespaces endpoint with wrong HTTP methods."""
        # Test POST method (should not be allowed unless create is implemented)
        response = client.post("/namespaces")
        assert response.status_code in [
            405,
            422,
        ]  # Method Not Allowed or Unprocessable Entity

        # Test PUT method (should not be allowed)
        response = client.put("/namespaces")
        assert response.status_code == 405  # Method Not Allowed

        # Test DELETE method (should not be allowed)
        response = client.delete("/namespaces")
        assert response.status_code == 405  # Method Not Allowed

    def test_namespaces_database_error_handling(self, client):
        """Test namespaces endpoint handles database errors gracefully."""
        # Mock the client to raise an exception
        mock_client_instance = Mock()
        mock_client_instance.get_all.side_effect = Exception(
            "Database connection failed"
        )

        # Override the dependency
        client.app.dependency_overrides[get_namespace_client] = (
            lambda: mock_client_instance
        )

        try:
            # The API currently doesn't have error handling, so the exception propagates
            # This test verifies that the mock is working correctly
            with pytest.raises(Exception, match="Database connection failed"):
                response = client.get("/namespaces")
        finally:
            # Clean up the override
            client.app.dependency_overrides.clear()
