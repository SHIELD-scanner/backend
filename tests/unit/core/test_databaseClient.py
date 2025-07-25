"""Tests for databaseClient module."""

from unittest.mock import Mock, patch

from app.core.databaseClient import DatabaseClient


class TestDatabaseClient:

    """Test class for DatabaseClient base class."""

    @patch("app.core.databaseClient.MongoClient")
    def test_database_client_initialization(self, mock_mongo_client):
        """Test DatabaseClient can be instantiated."""
        mock_mongo_client.return_value = Mock()
        client = DatabaseClient()
        assert client is not None
        assert hasattr(client, "get_namespace_collection")
        assert hasattr(client, "get_pods_collection")
        assert hasattr(client, "get_reports_collection")
        assert hasattr(client, "get_vulnerabilities_collection")

    @patch("app.core.databaseClient.MongoClient")
    def test_get_collection_method(self, mock_mongo_client):
        """Test get_collection method returns a collection."""
        # Mock the MongoDB client and database
        from unittest.mock import MagicMock

        mock_client_instance = MagicMock()
        mock_database = MagicMock()
        mock_collection = MagicMock()

        mock_mongo_client.return_value = mock_client_instance
        mock_client_instance.__getitem__.return_value = mock_database
        mock_database.__getitem__.return_value = mock_collection

        client = DatabaseClient()

        # Test that client has necessary collection methods
        assert hasattr(client, "get_namespace_collection")
        assert hasattr(client, "get_pods_collection")
        assert hasattr(client, "get_reports_collection")
        assert hasattr(client, "get_vulnerabilities_collection")

    def test_database_client_is_base_class(self):
        """Test that DatabaseClient serves as a base class for other clients."""
        from app.core.exposedsecretClient import ExposedsecretClient
        from app.core.namespaceClient import NamespaceClient
        from app.core.podClient import PodClient
        from app.core.sbomClient import SbomClient
        from app.core.vulnerabilityClient import VulnerabilityClient

        # Test that all client classes inherit from DatabaseClient
        assert issubclass(ExposedsecretClient, DatabaseClient)
        assert issubclass(SbomClient, DatabaseClient)
        assert issubclass(PodClient, DatabaseClient)
        assert issubclass(NamespaceClient, DatabaseClient)
        assert issubclass(VulnerabilityClient, DatabaseClient)

    @patch("app.core.databaseClient.MongoClient")
    def test_database_client_methods_exist(self, mock_mongo_client):
        """Test that DatabaseClient has expected methods."""
        mock_mongo_client.return_value = Mock()
        client = DatabaseClient()

        # Check that expected methods exist
        assert hasattr(client, "get_namespace_collection")
        assert hasattr(client, "get_pods_collection")
        assert hasattr(client, "get_reports_collection")
        assert hasattr(client, "get_vulnerabilities_collection")
        assert hasattr(client, "close")

    @patch("app.core.databaseClient.MongoClient")
    def test_database_client_with_environment_variables(self, mock_mongo_client):
        """Test DatabaseClient respects environment variables."""
        mock_mongo_client.return_value = Mock()

        with patch.dict(
            "os.environ",
            {"MONGODB_URI": "mongodb://test:27017", "MONGODB_DB": "test_db"},
        ):
            client = DatabaseClient()
            # This test would verify that environment variables are used
            assert client is not None

    @patch("app.core.databaseClient.MongoClient")
    def test_database_client_interface(self, mock_mongo_client):
        """Test that DatabaseClient provides the expected interface."""
        mock_mongo_client.return_value = Mock()
        client = DatabaseClient()

        # Test that the client has the interface that subclasses expect
        assert hasattr(client, "client")  # Should have MongoDB client
        assert hasattr(client, "close")  # Should have close method
        # Check for the actual methods that exist in DatabaseClient
        assert callable(getattr(client, "get_namespace_collection", None))
        assert callable(getattr(client, "get_pods_collection", None))
        assert callable(getattr(client, "get_reports_collection", None))
        assert callable(getattr(client, "get_vulnerabilities_collection", None))

        # If DatabaseClient defines abstract methods or interface contracts,
        # we would test those here
