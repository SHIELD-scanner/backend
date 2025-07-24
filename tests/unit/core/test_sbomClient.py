"""Unit tests for SbomClient."""

from unittest.mock import Mock, patch

import mongomock
import pytest

from app.core.sbomClient import SbomClient
from app.models.sbom import SBOM


class TestSbomClient:
    """Test cases for SbomClient."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock SbomClient."""
        with (
            patch("app.core.sbomClient.DatabaseClient.__init__"),
            patch("app.core.sbomClient.os.getenv", return_value="shield_test"),
        ):
            client = SbomClient()
            client.client = mongomock.MongoClient()
            return client

    def test_get_collection(self, mock_client):
        """Test get_collection method."""
        with patch("app.core.sbomClient.os.getenv", return_value="shield_test"):
            collection = mock_client.get_collection()
            assert collection is not None

    def test_get_all_no_filters(self, mock_client):
        """Test get_all with no filters."""
        mock_data = [
            {"_uid": "sbom1", "_namespace": "ns1", "_cluster": "cluster1"},
            {"_uid": "sbom2", "_namespace": "ns2", "_cluster": "cluster2"},
        ]

        mock_collection = Mock()
        mock_collection.find.return_value = mock_data
        mock_client.get_collection = Mock(return_value=mock_collection)

        result = mock_client.get_all()

        assert len(result) == 2
        assert isinstance(result[0], SBOM)
        assert result[0].uid == "sbom1"
        mock_collection.find.assert_called_once_with({}, {"_id": 0})

    def test_get_all_with_namespace_filter(self, mock_client):
        """Test get_all with namespace filter."""
        mock_data = [{"_uid": "sbom1", "_namespace": "test-ns", "_cluster": "cluster1"}]

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
        mock_data = [{"_uid": "sbom1", "_namespace": "ns1", "_cluster": "test-cluster"}]

        mock_collection = Mock()
        mock_collection.find.return_value = mock_data
        mock_client.get_collection = Mock(return_value=mock_collection)

        result = mock_client.get_all(cluster="test-cluster")

        assert len(result) == 1
        mock_collection.find.assert_called_once_with(
            {"_cluster": "test-cluster"}, {"_id": 0}
        )

    def test_get_by_uid_found(self, mock_client):
        """Test get_by_uid when item is found."""
        mock_data = {"_uid": "test-sbom", "_namespace": "ns1", "_cluster": "cluster1"}

        mock_collection = Mock()
        mock_collection.find_one.return_value = mock_data
        mock_client.get_collection = Mock(return_value=mock_collection)

        result = mock_client.get_by_uid("test-sbom")

        assert result is not None
        assert isinstance(result, SBOM)
        assert result.uid == "test-sbom"
        mock_collection.find_one.assert_called_once_with(
            {"_uid": "test-sbom"}, {"_id": 0}
        )

    def test_get_by_uid_not_found(self, mock_client):
        """Test get_by_uid when item is not found."""
        mock_collection = Mock()
        mock_collection.find_one.return_value = None
        mock_client.get_collection = Mock(return_value=mock_collection)

        result = mock_client.get_by_uid("nonexistent-sbom")

        assert result is None

    def test_format_with_valid_item(self, mock_client):
        """Test _format with valid item."""
        item = {
            "_uid": "test-sbom",
            "_namespace": "test-ns",
            "_cluster": "test-cluster",
        }

        result = mock_client._format(item)

        assert isinstance(result, SBOM)
        assert result.uid == "test-sbom"
        assert result.namespace == "test-ns"
        assert result.cluster == "test-cluster"

    def test_format_with_none_item(self, mock_client):
        """Test _format with None item."""
        result = mock_client._format(None)

        assert result is None

    def test_format_with_missing_fields(self, mock_client):
        """Test _format with missing fields uses defaults."""
        item = {"_uid": "test-sbom"}

        result = mock_client._format(item)

        assert isinstance(result, SBOM)
        assert result.uid == "test-sbom"
        assert result.namespace == ""
        assert result.cluster == ""

    def test_sbom_class_naming_convention(self, mock_client):
        """Test that SBOM class follows acronym naming convention."""
        item = {
            "_uid": "test-sbom",
            "_namespace": "test-ns",
            "_cluster": "test-cluster",
        }
        result = mock_client._format(item)

        # Verify we're using SBOM (all caps) not Sbom
        assert result.__class__.__name__ == "SBOM"
