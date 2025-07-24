"""Integration tests for database operations."""
import pytest
from unittest.mock import patch
import mongomock
import os

# Set test environment
os.environ["MONGODB_DB"] = "shield_test"

from app.core.exposedsecretClient import ExposedsecretClient
from app.core.sbomClient import SbomClient
from app.core.podClient import PodClient
from app.core.namespaceClient import NamespaceClient
from app.models.exposedsecret import ExposedSecret
from app.models.sbom import SBOM
from app.models.pod import Pod
from app.models.namespace import Namespace


class TestDatabaseIntegration:
    """Integration tests for database operations."""

    @pytest.fixture
    def mock_mongo_client(self):
        """Create a mock MongoDB client with test data."""
        client = mongomock.MongoClient()
        
        # Setup test data for exposed secrets
        exposed_secrets = client["shield_test"]["exposedsecretreports"]
        exposed_secrets.insert_many([
            {"_uid": "secret1", "_namespace": "ns1", "_cluster": "cluster1"},
            {"_uid": "secret2", "_namespace": "ns2", "_cluster": "cluster1"},
            {"_uid": "secret3", "_namespace": "ns1", "_cluster": "cluster2"}
        ])
        
        # Setup test data for SBOMs
        sboms = client["shield_test"]["sbomreports"]
        sboms.insert_many([
            {"_uid": "sbom1", "_namespace": "ns1", "_cluster": "cluster1"},
            {"_uid": "sbom2", "_namespace": "ns2", "_cluster": "cluster1"}
        ])
        
        # Setup test data for pods
        pods = client["shield_test"]["pods"]
        pods.insert_many([
            {"name": "pod1", "namespace": "ns1", "cluster": "cluster1"},
            {"name": "pod2", "namespace": "ns2", "cluster": "cluster1"},
            {"name": "pod3", "namespace": "ns1", "cluster": "cluster2"}
        ])
        
        # Setup test data for namespaces
        namespaces = client["shield_test"]["namespaces"]
        namespaces.insert_many([
            {"_cluster": "cluster1", "_name": "ns1", "_uid": "ns1-uid"},
            {"_cluster": "cluster1", "_name": "ns2", "_uid": "ns2-uid"},
            {"_cluster": "cluster2", "_name": "ns1", "_uid": "ns3-uid"}
        ])
        
        return client

    def test_exposed_secret_client_integration(self, mock_mongo_client):
        """Test ExposedsecretClient with mock database."""
        with patch('app.core.databaseClient.DatabaseClient.__init__'):
            client = ExposedsecretClient()
            client.client = mock_mongo_client
            
            # Test get_all with no filters
            results = client.get_all()
            assert len(results) == 3
            assert all(isinstance(r, ExposedSecret) for r in results)
            
            # Test get_all with namespace filter
            results = client.get_all(namespace="ns1")
            assert len(results) == 2
            assert all(r.namespace == "ns1" for r in results)
            
            # Test get_all with cluster filter
            results = client.get_all(cluster="cluster1")
            assert len(results) == 2
            assert all(r.cluster == "cluster1" for r in results)
            
            # Test get_all with both filters
            results = client.get_all(namespace="ns1", cluster="cluster1")
            assert len(results) == 1
            assert results[0].namespace == "ns1"
            assert results[0].cluster == "cluster1"
            
            # Test get_by_uid
            result = client.get_by_uid("secret1")
            assert result is not None
            assert result.uid == "secret1"
            
            # Test get_by_uid not found
            result = client.get_by_uid("nonexistent")
            assert result is None

    def test_sbom_client_integration(self, mock_mongo_client):
        """Test SbomClient with mock database."""
        with patch('app.core.databaseClient.DatabaseClient.__init__'):
            client = SbomClient()
            client.client = mock_mongo_client
            
            # Test get_all
            results = client.get_all()
            assert len(results) == 2
            assert all(isinstance(r, SBOM) for r in results)
            
            # Test filtering
            results = client.get_all(namespace="ns1")
            assert len(results) == 1
            assert results[0].namespace == "ns1"
            
            # Test get_by_uid
            result = client.get_by_uid("sbom1")
            assert result is not None
            assert result.uid == "sbom1"
            assert isinstance(result, SBOM)  # Verify SBOM acronym naming

    def test_pod_client_integration(self, mock_mongo_client):
        """Test PodClient with mock database."""
        with patch('app.core.databaseClient.DatabaseClient.__init__'):
            client = PodClient()
            client.client = mock_mongo_client
            
            # Test get_all
            results = client.get_all()
            assert len(results) == 3
            assert all(isinstance(r, Pod) for r in results)
            
            # Test get_by_cluster
            results = client.get_by_cluster("cluster1")
            assert len(results) == 2
            assert all(r.cluster == "cluster1" for r in results)
            
            # Test get_by_namespace
            results = client.get_by_namespace("cluster1", "ns1")
            assert len(results) == 1
            assert results[0].namespace == "ns1"
            assert results[0].cluster == "cluster1"
            
            # Test get_by_name
            result = client.get_by_name("cluster1", "ns1", "pod1")
            assert result is not None
            assert result.name == "pod1"

    def test_namespace_client_integration(self, mock_mongo_client):
        """Test NamespaceClient with mock database."""
        with patch('app.core.databaseClient.DatabaseClient.__init__'):
            client = NamespaceClient()
            client.client = mock_mongo_client
            
            # Test get_all
            results = client.get_all()
            assert len(results) == 3
            assert all(isinstance(r, Namespace) for r in results)
            
            # Test cluster filtering
            results = client.get_all(cluster="cluster1")
            assert len(results) == 2
            assert all(r.cluster == "cluster1" for r in results)

    def test_cross_client_data_consistency(self, mock_mongo_client):
        """Test data consistency across different clients."""
        with patch('app.core.databaseClient.DatabaseClient.__init__'):
            # Initialize all clients
            secret_client = ExposedsecretClient()
            secret_client.client = mock_mongo_client
            
            pod_client = PodClient()
            pod_client.client = mock_mongo_client
            
            # Test that the same namespace appears in both
            secrets_ns1 = secret_client.get_all(namespace="ns1")
            pods_ns1 = pod_client.get_all(namespace="ns1")
            
            assert len(secrets_ns1) > 0
            assert len(pods_ns1) > 0
            
            # Verify consistent namespace naming
            assert all(s.namespace == "ns1" for s in secrets_ns1)
            assert all(p.namespace == "ns1" for p in pods_ns1)

    def test_memory_efficiency_with_large_dataset(self, mock_mongo_client):
        """Test memory efficiency with larger datasets."""
        # Add more test data
        exposed_secrets = mock_mongo_client["shield_test"]["exposedsecretreports"]
        large_dataset = [
            {"_uid": f"secret{i}", "_namespace": f"ns{i%5}", "_cluster": f"cluster{i%3}"}
            for i in range(100)
        ]
        exposed_secrets.insert_many(large_dataset)
        
        with patch('app.core.databaseClient.DatabaseClient.__init__'):
            client = ExposedsecretClient()
            client.client = mock_mongo_client
            
            # This should work efficiently with the generator-based approach
            results = client.get_all()
            assert len(results) == 103  # Original 3 + 100 new ones
            
            # Test filtering still works with larger dataset
            ns0_results = client.get_all(namespace="ns0")
            assert len(ns0_results) == 20  # Every 5th item from 0-99

    def test_format_methods_handle_edge_cases(self, mock_mongo_client):
        """Test that format methods handle edge cases properly."""
        with patch('app.core.databaseClient.DatabaseClient.__init__'):
            client = ExposedsecretClient()
            client.client = mock_mongo_client
            
            # Test _format with None
            result = client._format(None)
            assert result is None
            
            # Test _format with missing fields
            incomplete_item = {"_uid": "test"}
            result = client._format(incomplete_item)
            assert result is not None
            assert result.uid == "test"
            assert result.namespace == ""  # Default value
            assert result.cluster == ""    # Default value
