"""Test configuration and fixtures."""
import os
import pytest
from unittest.mock import Mock, MagicMock
from fastapi.testclient import TestClient
import mongomock

# Set test environment variables
os.environ["MONGODB_DB"] = "shield_test"
os.environ["SENTRY_DSN"] = ""

from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_mongo_client():
    """Create a mock MongoDB client."""
    return mongomock.MongoClient()


@pytest.fixture
def mock_database_client(mock_mongo_client):
    """Create a mock database client."""
    mock_client = Mock()
    mock_client.client = mock_mongo_client
    mock_client.get_collection = Mock()
    return mock_client


@pytest.fixture
def sample_exposed_secret():
    """Sample ExposedSecret data for testing."""
    return {
        "_uid": "test-uid-123",
        "_namespace": "test-namespace",
        "_cluster": "test-cluster"
    }


@pytest.fixture
def sample_sbom():
    """Sample SBOM data for testing."""
    return {
        "_uid": "sbom-uid-123",
        "_namespace": "test-namespace", 
        "_cluster": "test-cluster"
    }


@pytest.fixture
def sample_pod():
    """Sample Pod data for testing."""
    return {
        "name": "test-pod",
        "namespace": "test-namespace",
        "cluster": "test-cluster",
        "_uid": "pod-uid-123"
    }


@pytest.fixture
def sample_namespace():
    """Sample Namespace data for testing."""
    return {
        "_cluster": "test-cluster",
        "_name": "test-namespace",
        "_uid": "namespace-uid-123"
    }


@pytest.fixture
def sample_vulnerability():
    """Sample Vulnerability data for testing."""
    return {
        "_namespace": "test-namespace",
        "_cluster": "test-cluster",
        "data": {
            "report": {
                "vulnerabilities": [
                    {
                        "vulnerabilityID": "CVE-2021-1234",
                        "severity": "HIGH",
                        "score": 7.5,
                        "resource": "test-package",
                        "installedVersion": "1.0.0",
                        "fixedVersion": "1.0.1",
                        "title": "Test vulnerability"
                    }
                ],
                "artifact": {
                    "repository": "test-repo"
                }
            },
            "metadata": {
                "uid": "vuln-uid-123"
            }
        }
    }
