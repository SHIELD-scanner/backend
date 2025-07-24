"""Tests for namespaceClient module."""

from unittest.mock import Mock

from app.core.namespaceClient import NamespaceClient
from app.models.namespace import Namespace


class TestNamespaceClient:
    """Test class for NamespaceClient."""

    def test_format_to_namespace_method(self):
        """Test the _format_to_namespace method converts MongoDB document to Namespace model."""
        client = NamespaceClient()

        # Mock MongoDB document
        mock_item = {
            "_cluster": "test-cluster",
            "_name": "test-namespace",
            "_uid": "namespace-123",
        }

        result = client._format_to_namespace(mock_item)

        assert isinstance(result, Namespace)
        assert result.cluster == "test-cluster"
        assert result.name == "test-namespace"
        assert result.uid == "namespace-123"

    def test_format_to_namespace_method_with_missing_fields(self):
        """Test _format_to_namespace method with missing fields uses defaults."""
        client = NamespaceClient()

        # MongoDB document with missing fields
        mock_item = {"_cluster": "test-cluster"}

        result = client._format_to_namespace(mock_item)

        assert isinstance(result, Namespace)
        assert result.cluster == "test-cluster"
        assert result.name == ""  # default value
        assert result.uid == ""  # default value

    def test_format_to_namespace_method_with_empty_document(self):
        """Test _format_to_namespace method with empty document."""
        client = NamespaceClient()

        result = client._format_to_namespace({})

        assert isinstance(result, Namespace)
        assert result.cluster == ""
        assert result.name == ""
        assert result.uid == ""

    def test_get_all_method(self):
        """Test get_all method returns list of Namespace objects."""
        client = NamespaceClient()

        # Mock the collection and cursor
        mock_collection = Mock()
        mock_cursor = Mock()
        mock_cursor.__iter__ = Mock(
            return_value=iter(
                [
                    {"_cluster": "cluster1", "_name": "ns1", "_uid": "uid1"},
                    {"_cluster": "cluster2", "_name": "ns2", "_uid": "uid2"},
                ]
            )
        )

        mock_collection.find.return_value = mock_cursor
        client.get_collection = Mock(return_value=mock_collection)

        result = list(client.get_all())

        assert len(result) == 2
        assert all(isinstance(ns, Namespace) for ns in result)
        assert result[0].cluster == "cluster1"
        assert result[1].cluster == "cluster2"

        # Verify the MongoDB query
        mock_collection.find.assert_called_once_with({}, {"_id": 0})

    def test_get_all_empty_collection(self):
        """Test get_all method with empty collection."""
        client = NamespaceClient()

        # Mock empty collection
        mock_collection = Mock()
        mock_cursor = Mock()
        mock_cursor.__iter__ = Mock(return_value=iter([]))

        mock_collection.find.return_value = mock_cursor
        client.get_collection = Mock(return_value=mock_collection)

        result = list(client.get_all())

        assert len(result) == 0
        assert isinstance(result, list)

    def test_collection_name(self):
        """Test that NamespaceClient uses correct collection name."""
        client = NamespaceClient()
        # This would be tested if we had access to the actual collection name
        # For now, we verify the client can be instantiated
        assert client is not None
        assert hasattr(client, "get_collection")
        assert hasattr(client, "_format_to_namespace")
        assert hasattr(client, "get_all")
