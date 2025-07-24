"""Tests for namespace API module."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app
from app.models.namespace import Namespace
from app.core.namespaceClient import NamespaceClient


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
            cluster="test-cluster",
            name="test-namespace",
            uid="namespace-123"
        )

    def test_get_all_namespaces(self, client, mock_namespace_client, sample_namespace):
        """Test GET /namespaces endpoint."""
        # Mock the dependency
        mock_namespace_client.get_all.return_value = [sample_namespace]
        
        with patch('app.api.namespace.NamespaceClient', return_value=mock_namespace_client):
            response = client.get("/namespaces")
        
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
        
        with patch('app.api.namespace.NamespaceClient', return_value=mock_namespace_client):
            response = client.get("/namespaces")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_all_namespaces_multiple(self, client, mock_namespace_client):
        """Test GET /namespaces endpoint with multiple namespaces."""
        namespaces = [
            Namespace(cluster="cluster1", name="ns1", uid="uid1"),
            Namespace(cluster="cluster1", name="ns2", uid="uid2"),
            Namespace(cluster="cluster2", name="ns1", uid="uid3")
        ]
        mock_namespace_client.get_all.return_value = namespaces
        
        with patch('app.api.namespace.NamespaceClient', return_value=mock_namespace_client):
            response = client.get("/namespaces")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 3
        
        # Check that all namespaces are returned
        cluster_names = [ns["cluster"] for ns in data]
        assert "cluster1" in cluster_names
        assert "cluster2" in cluster_names

    def test_get_all_namespaces_query_parameters(self, client, mock_namespace_client, sample_namespace):
        """Test GET /namespaces endpoint with query parameters."""
        mock_namespace_client.get_all.return_value = [sample_namespace]
        
        with patch('app.api.namespace.NamespaceClient', return_value=mock_namespace_client):
            # Test with query parameters (if supported)
            response = client.get("/namespaces?cluster=test-cluster")
        
        assert response.status_code == 200
        # The actual filtering logic would depend on the API implementation

    def test_namespaces_endpoint_response_format(self, client, mock_namespace_client, sample_namespace):
        """Test namespaces endpoint response format."""
        mock_namespace_client.get_all.return_value = [sample_namespace]
        
        with patch('app.api.namespace.NamespaceClient', return_value=mock_namespace_client):
            response = client.get("/namespaces")
        
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
        assert response.status_code in [405, 422]  # Method Not Allowed or Unprocessable Entity
        
        # Test PUT method (should not be allowed)
        response = client.put("/namespaces")
        assert response.status_code == 405  # Method Not Allowed
        
        # Test DELETE method (should not be allowed)
        response = client.delete("/namespaces")
        assert response.status_code == 405  # Method Not Allowed

    @patch('app.api.namespace.NamespaceClient')
    def test_namespaces_database_error_handling(self, mock_client_class, client):
        """Test namespaces endpoint handles database errors gracefully."""
        # Mock the client to raise an exception
        mock_client_instance = Mock()
        mock_client_instance.get_all.side_effect = Exception("Database connection failed")
        mock_client_class.return_value = mock_client_instance
        
        response = client.get("/namespaces")
        
        # The actual error handling would depend on the API implementation
        # This test verifies that errors don't crash the application
        assert response.status_code in [200, 500, 503]  # Various possible error responses
