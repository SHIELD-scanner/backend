"""Unit tests for ExposedsecretClient."""
import pytest
from unittest.mock import Mock, patch, MagicMock
import mongomock
from app.core.exposedsecretClient import ExposedsecretClient
from app.models.exposedsecret import ExposedSecret


class TestExposedsecretClient:
    """Test cases for ExposedsecretClient."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock ExposedsecretClient."""
        with patch('app.core.exposedsecretClient.DatabaseClient.__init__'), \
             patch('app.core.exposedsecretClient.os.getenv', return_value='shield_test'):
            client = ExposedsecretClient()
            client.client = mongomock.MongoClient()
            return client

    def test_get_collection(self, mock_client):
        """Test get_collection method."""
        with patch('app.core.exposedsecretClient.os.getenv', return_value='shield_test'):
            collection = mock_client.get_collection()
            assert collection is not None

    def test_get_all_no_filters(self, mock_client):
        """Test get_all with no filters."""
        # Setup mock data
        mock_data = [
            {"_uid": "uid1", "_namespace": "ns1", "_cluster": "cluster1"},
            {"_uid": "uid2", "_namespace": "ns2", "_cluster": "cluster2"}
        ]
        
        mock_collection = Mock()
        mock_collection.find.return_value = mock_data
        mock_client.get_collection = Mock(return_value=mock_collection)
        
        result = mock_client.get_all()
        
        assert len(result) == 2
        assert isinstance(result[0], ExposedSecret)
        assert result[0].uid == "uid1"
        mock_collection.find.assert_called_once_with({}, {"_id": 0})

    def test_get_all_with_namespace_filter(self, mock_client):
        """Test get_all with namespace filter."""
        mock_data = [
            {"_uid": "uid1", "_namespace": "test-ns", "_cluster": "cluster1"}
        ]
        
        mock_collection = Mock()
        mock_collection.find.return_value = mock_data
        mock_client.get_collection = Mock(return_value=mock_collection)
        
        result = mock_client.get_all(namespace="test-ns")
        
        assert len(result) == 1
        mock_collection.find.assert_called_once_with(
            {"_namespace": "test-ns"}, {"_id": 0}
        )

    def test_get_all_with_cluster_filter(self, mock_client):
        """Test get_all with cluster filter."""
        mock_data = [
            {"_uid": "uid1", "_namespace": "ns1", "_cluster": "test-cluster"}
        ]
        
        mock_collection = Mock()
        mock_collection.find.return_value = mock_data
        mock_client.get_collection = Mock(return_value=mock_collection)
        
        result = mock_client.get_all(cluster="test-cluster")
        
        assert len(result) == 1
        mock_collection.find.assert_called_once_with(
            {"_cluster": "test-cluster"}, {"_id": 0}
        )

    def test_get_all_with_both_filters(self, mock_client):
        """Test get_all with both namespace and cluster filters."""
        mock_data = [
            {"_uid": "uid1", "_namespace": "test-ns", "_cluster": "test-cluster"}
        ]
        
        mock_collection = Mock()
        mock_collection.find.return_value = mock_data
        mock_client.get_collection = Mock(return_value=mock_collection)
        
        result = mock_client.get_all(namespace="test-ns", cluster="test-cluster")
        
        assert len(result) == 1
        mock_collection.find.assert_called_once_with(
            {"_namespace": "test-ns", "_cluster": "test-cluster"}, {"_id": 0}
        )

    def test_get_all_filters_none_items(self, mock_client):
        """Test get_all filters out None items."""
        # Mock _format to return None for some items
        mock_data = [
            {"_uid": "uid1", "_namespace": "ns1", "_cluster": "cluster1"},
            None,  # This should be filtered out
            {"_uid": "uid2", "_namespace": "ns2", "_cluster": "cluster2"}
        ]
        
        mock_collection = Mock()
        mock_collection.find.return_value = mock_data
        mock_client.get_collection = Mock(return_value=mock_collection)
        
        result = mock_client.get_all()
        
        # Should only have 2 items (None items filtered out)
        assert len(result) == 2

    def test_get_by_uid_found(self, mock_client):
        """Test get_by_uid when item is found."""
        mock_data = {"_uid": "test-uid", "_namespace": "ns1", "_cluster": "cluster1"}
        
        mock_collection = Mock()
        mock_collection.find_one.return_value = mock_data
        mock_client.get_collection = Mock(return_value=mock_collection)
        
        result = mock_client.get_by_uid("test-uid")
        
        assert result is not None
        assert isinstance(result, ExposedSecret)
        assert result.uid == "test-uid"
        mock_collection.find_one.assert_called_once_with(
            {"_uid": "test-uid"}, {"_id": 0}
        )

    def test_get_by_uid_not_found(self, mock_client):
        """Test get_by_uid when item is not found."""
        mock_collection = Mock()
        mock_collection.find_one.return_value = None
        mock_client.get_collection = Mock(return_value=mock_collection)
        
        result = mock_client.get_by_uid("nonexistent-uid")
        
        assert result is None
        mock_collection.find_one.assert_called_once_with(
            {"_uid": "nonexistent-uid"}, {"_id": 0}
        )

    def test_format_with_valid_item(self, mock_client):
        """Test _format with valid item."""
        item = {"_uid": "test-uid", "_namespace": "test-ns", "_cluster": "test-cluster"}
        
        result = mock_client._format(item)
        
        assert isinstance(result, ExposedSecret)
        assert result.uid == "test-uid"
        assert result.namespace == "test-ns"
        assert result.cluster == "test-cluster"

    def test_format_with_none_item(self, mock_client):
        """Test _format with None item."""
        result = mock_client._format(None)
        
        assert result is None

    def test_format_with_missing_fields(self, mock_client):
        """Test _format with missing fields uses defaults."""
        item = {"_uid": "test-uid"}  # Missing namespace and cluster
        
        result = mock_client._format(item)
        
        assert isinstance(result, ExposedSecret)
        assert result.uid == "test-uid"
        assert result.namespace == ""  # Default value
        assert result.cluster == ""    # Default value
