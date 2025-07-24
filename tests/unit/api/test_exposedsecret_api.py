"""Unit tests for exposedsecret API endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.models.exposedsecret import ExposedSecret


class TestExposedSecretAPI:
    """Test cases for ExposedSecret API endpoints."""

    @pytest.fixture
    def mock_client_dependency(self):
        """Mock the get_exposedsecret_client dependency."""
        mock_client = Mock()
        return mock_client

    def test_list_exposedsecrets_no_filters(self, client, mock_client_dependency):
        """Test GET /exposedsecrets/ with no filters."""
        # Mock data
        mock_secrets = [
            ExposedSecret(uid="uid1", namespace="ns1", cluster="cluster1"),
            ExposedSecret(uid="uid2", namespace="ns2", cluster="cluster2")
        ]
        mock_client_dependency.get_all.return_value = mock_secrets
        
        # Mock the dependency
        with patch('app.api.exposedsecret.get_exposedsecret_client', 
                   return_value=mock_client_dependency):
            response = client.get("/exposedsecrets/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["uid"] == "uid1"
        assert data[1]["uid"] == "uid2"
        mock_client_dependency.get_all.assert_called_once_with(namespace=None, cluster=None)

    def test_list_exposedsecrets_with_namespace_filter(self, client, mock_client_dependency):
        """Test GET /exposedsecrets/ with namespace filter."""
        mock_secrets = [
            ExposedSecret(uid="uid1", namespace="test-ns", cluster="cluster1")
        ]
        mock_client_dependency.get_all.return_value = mock_secrets
        
        with patch('app.api.exposedsecret.get_exposedsecret_client', 
                   return_value=mock_client_dependency):
            response = client.get("/exposedsecrets/?namespace=test-ns")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["namespace"] == "test-ns"
        mock_client_dependency.get_all.assert_called_once_with(namespace="test-ns", cluster=None)

    def test_list_exposedsecrets_with_cluster_filter(self, client, mock_client_dependency):
        """Test GET /exposedsecrets/ with cluster filter."""
        mock_secrets = [
            ExposedSecret(uid="uid1", namespace="ns1", cluster="test-cluster")
        ]
        mock_client_dependency.get_all.return_value = mock_secrets
        
        with patch('app.api.exposedsecret.get_exposedsecret_client', 
                   return_value=mock_client_dependency):
            response = client.get("/exposedsecrets/?cluster=test-cluster")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["cluster"] == "test-cluster"
        mock_client_dependency.get_all.assert_called_once_with(namespace=None, cluster="test-cluster")

    def test_list_exposedsecrets_with_both_filters(self, client, mock_client_dependency):
        """Test GET /exposedsecrets/ with both filters."""
        mock_secrets = [
            ExposedSecret(uid="uid1", namespace="test-ns", cluster="test-cluster")
        ]
        mock_client_dependency.get_all.return_value = mock_secrets
        
        with patch('app.api.exposedsecret.get_exposedsecret_client', 
                   return_value=mock_client_dependency):
            response = client.get("/exposedsecrets/?namespace=test-ns&cluster=test-cluster")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        mock_client_dependency.get_all.assert_called_once_with(
            namespace="test-ns", cluster="test-cluster"
        )

    def test_show_exposedsecret_found(self, client, mock_client_dependency):
        """Test GET /exposedsecrets/{uid} when secret exists."""
        mock_secret = ExposedSecret(uid="test-uid", namespace="test-ns", cluster="test-cluster")
        mock_client_dependency.get_by_uid.return_value = mock_secret
        
        with patch('app.api.exposedsecret.get_exposedsecret_client', 
                   return_value=mock_client_dependency):
            response = client.get("/exposedsecrets/test-uid")
        
        assert response.status_code == 200
        data = response.json()
        assert data["uid"] == "test-uid"
        assert data["namespace"] == "test-ns"
        assert data["cluster"] == "test-cluster"
        mock_client_dependency.get_by_uid.assert_called_once_with("test-uid")

    def test_show_exposedsecret_not_found(self, client, mock_client_dependency):
        """Test GET /exposedsecrets/{uid} when secret doesn't exist."""
        mock_client_dependency.get_by_uid.return_value = None
        
        with patch('app.api.exposedsecret.get_exposedsecret_client', 
                   return_value=mock_client_dependency):
            response = client.get("/exposedsecrets/nonexistent-uid")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Exposed secret not found"
        mock_client_dependency.get_by_uid.assert_called_once_with("nonexistent-uid")

    def test_list_exposedsecrets_empty_result(self, client, mock_client_dependency):
        """Test GET /exposedsecrets/ with empty result."""
        mock_client_dependency.get_all.return_value = []
        
        with patch('app.api.exposedsecret.get_exposedsecret_client', 
                   return_value=mock_client_dependency):
            response = client.get("/exposedsecrets/")
        
        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_dependency_injection_working(self, client):
        """Test that dependency injection is properly configured."""
        # This test verifies that the dependency injection setup is working
        with patch('app.api.exposedsecret.get_exposedsecret_client') as mock_dep:
            mock_client = Mock()
            mock_client.get_all.return_value = []
            mock_dep.return_value = mock_client
            
            response = client.get("/exposedsecrets/")
            
            assert response.status_code == 200
            mock_dep.assert_called_once()
