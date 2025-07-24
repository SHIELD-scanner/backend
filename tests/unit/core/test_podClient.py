"""Unit tests for PodClient."""
import pytest
from unittest.mock import Mock, patch, MagicMock
import mongomock
from app.core.podClient import PodClient
from app.models.pod import Pod


class TestPodClient:
    """Test cases for PodClient."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock PodClient."""
        with patch('app.core.podClient.DatabaseClient.__init__'), \
             patch('app.core.podClient.os.getenv', return_value='shield_test'):
            client = PodClient()
            client.client = mongomock.MongoClient()
            return client

    def test_get_collection(self, mock_client):
        """Test get_collection method."""
        with patch('app.core.podClient.os.getenv', return_value='shield_test'):
            collection = mock_client.get_collection()
            assert collection is not None

    def test_get_all_no_filters(self, mock_client):
        """Test get_all with no filters."""
        mock_data = [
            {"name": "pod1", "namespace": "ns1", "cluster": "cluster1"},
            {"name": "pod2", "namespace": "ns2", "cluster": "cluster2"}
        ]
        
        mock_collection = Mock()
        mock_collection.find.return_value = mock_data
        mock_client.get_collection = Mock(return_value=mock_collection)
        
        result = mock_client.get_all()
        
        assert len(result) == 2
        assert isinstance(result[0], Pod)
        assert result[0].name == "pod1"
        mock_collection.find.assert_called_once_with({}, {"_id": 0})

    def test_get_all_with_namespace_filter(self, mock_client):
        """Test get_all with namespace filter."""
        mock_data = [
            {"name": "pod1", "namespace": "test-ns", "cluster": "cluster1"}
        ]
        
        mock_collection = Mock()
        mock_collection.find.return_value = mock_data
        mock_client.get_collection = Mock(return_value=mock_collection)
        
        result = mock_client.get_all(namespace="test-ns")
        
        assert len(result) == 1
        mock_collection.find.assert_called_once_with(
            {"namespace": "test-ns"}, {"_id": 0}
        )

    def test_get_all_with_cluster_filter(self, mock_client):
        """Test get_all with cluster filter."""
        mock_data = [
            {"name": "pod1", "namespace": "ns1", "cluster": "test-cluster"}
        ]
        
        mock_collection = Mock()
        mock_collection.find.return_value = mock_data
        mock_client.get_collection = Mock(return_value=mock_collection)
        
        result = mock_client.get_all(cluster="test-cluster")
        
        assert len(result) == 1
        mock_collection.find.assert_called_once_with(
            {"cluster": "test-cluster"}, {"_id": 0}
        )

    def test_get_by_name(self, mock_client):
        """Test get_by_name method."""
        mock_data = {"name": "test-pod", "namespace": "test-ns", "cluster": "test-cluster"}
        
        mock_collection = Mock()
        mock_collection.find_one.return_value = mock_data
        mock_client.get_collection = Mock(return_value=mock_collection)
        
        result = mock_client.get_by_name("test-cluster", "test-ns", "test-pod")
        
        assert result is not None
        assert isinstance(result, Pod)
        assert result.name == "test-pod"
        mock_collection.find_one.assert_called_once_with(
            {"name": "test-pod", "namespace": "test-ns", "cluster": "test-cluster"},
            {"_id": 0}
        )

    def test_get_by_namespace(self, mock_client):
        """Test get_by_namespace method."""
        mock_data = [
            {"name": "pod1", "namespace": "test-ns", "cluster": "test-cluster"},
            {"name": "pod2", "namespace": "test-ns", "cluster": "test-cluster"}
        ]
        
        mock_collection = Mock()
        mock_collection.find.return_value = mock_data
        mock_client.get_collection = Mock(return_value=mock_collection)
        
        result = mock_client.get_by_namespace("test-cluster", "test-ns")
        
        assert len(result) == 2
        mock_collection.find.assert_called_once_with(
            {"namespace": "test-ns", "cluster": "test-cluster"}, {"_id": 0}
        )

    def test_get_by_cluster(self, mock_client):
        """Test get_by_cluster method."""
        mock_data = [
            {"name": "pod1", "namespace": "ns1", "cluster": "test-cluster"},
            {"name": "pod2", "namespace": "ns2", "cluster": "test-cluster"}
        ]
        
        mock_collection = Mock()
        mock_collection.find.return_value = mock_data
        mock_client.get_collection = Mock(return_value=mock_collection)
        
        result = mock_client.get_by_cluster("test-cluster")
        
        assert len(result) == 2
        mock_collection.find.assert_called_once_with(
            {"cluster": "test-cluster"}, {"_id": 0}
        )

    def test_format_to_pod_with_valid_item(self, mock_client):
        """Test _format_to_pod with valid item."""
        item = {"name": "test-pod", "namespace": "test-ns", "cluster": "test-cluster"}
        
        result = mock_client._format_to_pod(item)
        
        assert isinstance(result, Pod)
        assert result.name == "test-pod"
        assert result.namespace == "test-ns"
        assert result.cluster == "test-cluster"

    def test_format_to_pod_with_none_item(self, mock_client):
        """Test _format_to_pod with None item."""
        result = mock_client._format_to_pod(None)
        
        assert result is None

    def test_format_to_pod_with_id_field(self, mock_client):
        """Test _format_to_pod handles _id field conversion."""
        from bson import ObjectId
        item = {
            "name": "test-pod",
            "namespace": "test-ns", 
            "cluster": "test-cluster",
            "_id": ObjectId()
        }
        
        result = mock_client._format_to_pod(item)
        
        assert isinstance(result, Pod)
        assert isinstance(item["_id"], str)  # Should be converted to string
