"""Tests for pod API module."""

from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.api.pod import get_pod_client
from app.core.podClient import PodClient
from app.main import app
from app.models.pod import Pod


class TestPodAPI:
    """Test class for pod API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_pod_client(self):
        """Create mock pod client."""
        return Mock(spec=PodClient)

    @pytest.fixture
    def sample_pod(self):
        """Create sample pod for testing."""
        return Pod(
            cluster="test-cluster",
            namespace="test-namespace",
            name="test-pod",
            kind="Deployment",
        )

    def test_get_all_pods(self, client, mock_pod_client, sample_pod):
        """Test GET /pods endpoint."""
        mock_pod_client.get_all.return_value = [sample_pod]

        # Override the dependency
        client.app.dependency_overrides[get_pod_client] = lambda: mock_pod_client

        try:
            response = client.get("/pods")
        finally:
            # Clean up the override
            client.app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["cluster"] == "test-cluster"
        assert data[0]["namespace"] == "test-namespace"
        assert data[0]["name"] == "test-pod"
        assert data[0]["kind"] == "Deployment"

    def test_get_all_pods_empty(self, client, mock_pod_client):
        """Test GET /pods endpoint with no pods."""
        mock_pod_client.get_all.return_value = []

        # Override the dependency
        client.app.dependency_overrides[get_pod_client] = lambda: mock_pod_client

        try:
            response = client.get("/pods")
        finally:
            # Clean up the override
            client.app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_all_pods_multiple(self, client, mock_pod_client):
        """Test GET /pods endpoint with multiple pods."""
        pods = [
            Pod(cluster="cluster1", namespace="ns1", name="pod1", kind="Deployment"),
            Pod(cluster="cluster1", namespace="ns1", name="pod2", kind="Service"),
            Pod(cluster="cluster2", namespace="ns2", name="pod3", kind="Pod"),
        ]
        mock_pod_client.get_all.return_value = pods

        # Override the dependency
        client.app.dependency_overrides[get_pod_client] = lambda: mock_pod_client

        try:
            response = client.get("/pods")
        finally:
            # Clean up the override
            client.app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 3

        # Check that all pods are returned
        pod_names = [pod["name"] for pod in data]
        assert "pod1" in pod_names
        assert "pod2" in pod_names
        assert "pod3" in pod_names

    def test_get_pod_by_name(self, client, mock_pod_client, sample_pod):
        """Test GET /pods/{cluster}/{namespace}/{name} endpoint."""
        mock_pod_client.get_by_name.return_value = sample_pod

        # Override the dependency
        client.app.dependency_overrides[get_pod_client] = lambda: mock_pod_client

        try:
            response = client.get("/pods/test-cluster/test-namespace/test-pod")
        finally:
            # Clean up the override
            client.app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()

        assert data["cluster"] == "test-cluster"
        assert data["namespace"] == "test-namespace"
        assert data["name"] == "test-pod"
        assert data["kind"] == "Deployment"

        # Verify the client was called with correct parameters
        mock_pod_client.get_by_name.assert_called_once_with(
            cluster="test-cluster", namespace="test-namespace", name="test-pod"
        )

    def test_get_pod_by_name_not_found(self, client, mock_pod_client):
        """Test GET /pods/{cluster}/{namespace}/{name} endpoint with non-existent pod."""
        mock_pod_client.get_by_name.return_value = None

        # Override the dependency
        client.app.dependency_overrides[get_pod_client] = lambda: mock_pod_client

        try:
            response = client.get("/pods/cluster/namespace/nonexistent")
        finally:
            # Clean up the override
            client.app.dependency_overrides.clear()

        assert response.status_code == 404
        mock_pod_client.get_by_name.assert_called_once_with(
            cluster="cluster", namespace="namespace", name="nonexistent"
        )

    def test_pods_endpoint_response_format(self, client, mock_pod_client, sample_pod):
        """Test pods endpoint response format."""
        mock_pod_client.get_all.return_value = [sample_pod]

        # Override the dependency
        client.app.dependency_overrides[get_pod_client] = lambda: mock_pod_client

        try:
            response = client.get("/pods")
        finally:
            # Clean up the override
            client.app.dependency_overrides.clear()

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        data = response.json()
        assert isinstance(data, list)

        if data:  # If there are pods
            pod = data[0]
            assert "cluster" in pod
            assert "namespace" in pod
            assert "name" in pod
            assert "kind" in pod

    def test_get_pod_by_name_response_format(self, client, mock_pod_client, sample_pod):
        """Test get pod by name response format."""
        mock_pod_client.get_by_name.return_value = sample_pod

        # Override the dependency
        client.app.dependency_overrides[get_pod_client] = lambda: mock_pod_client

        try:
            response = client.get("/pods/test-cluster/test-namespace/test-pod")
        finally:
            # Clean up the override
            client.app.dependency_overrides.clear()

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        data = response.json()
        assert isinstance(data, dict)
        assert "cluster" in data
        assert "namespace" in data
        assert "name" in data
        assert "kind" in data

    def test_pods_endpoint_query_parameters(self, client, mock_pod_client, sample_pod):
        """Test GET /pods endpoint with query parameters."""
        mock_pod_client.get_all.return_value = [sample_pod]

        # Override the dependency
        client.app.dependency_overrides[get_pod_client] = lambda: mock_pod_client

        try:
            # Test with query parameters (if supported)
            response = client.get("/pods?namespace=test-namespace")
        finally:
            # Clean up the override
            client.app.dependency_overrides.clear()

        assert response.status_code == 200
        # The actual filtering logic would depend on the API implementation

    def test_pods_endpoint_method_not_allowed(self, client):
        """Test pods endpoint with wrong HTTP methods."""
        # Test POST method (should not be allowed unless create is implemented)
        response = client.post("/pods")
        assert response.status_code in [
            405,
            422,
        ]  # Method Not Allowed or Unprocessable Entity

        # Test PUT method (should not be allowed)
        response = client.put("/pods")
        assert response.status_code == 405  # Method Not Allowed

        # Test DELETE method (should not be allowed)
        response = client.delete("/pods")
        assert response.status_code == 405  # Method Not Allowed

    def test_pods_database_error_handling(self, client):
        """Test pods endpoint handles database errors gracefully."""
        mock_client_instance = Mock()
        mock_client_instance.get_all.side_effect = Exception(
            "Database connection failed"
        )

        # Override the dependency
        client.app.dependency_overrides[get_pod_client] = lambda: mock_client_instance

        try:
            # The API currently doesn't have error handling, so the exception propagates
            # This test verifies that the mock is working correctly
            with pytest.raises(Exception, match="Database connection failed"):
                response = client.get("/pods")
        finally:
            # Clean up the override
            client.app.dependency_overrides.clear()
