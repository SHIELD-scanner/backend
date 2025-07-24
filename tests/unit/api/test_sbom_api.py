"""Unit tests for SBOM API endpoints."""

from unittest.mock import Mock

import pytest

from app.api.sbom import get_sbom_client
from app.models.sbom import SBOM


class TestSBOMAPI:

    """Test cases for SBOM API endpoints."""

    @pytest.fixture
    def mock_client_dependency(self):
        """Mock the get_sbom_client dependency."""
        mock_client = Mock()
        return mock_client

    def test_list_sbom_no_filters(self, client, mock_client_dependency):
        """Test GET /sbom/ with no filters."""
        mock_sboms = [
            SBOM(uid="sbom1", namespace="ns1", cluster="cluster1"),
            SBOM(uid="sbom2", namespace="ns2", cluster="cluster2"),
        ]
        mock_client_dependency.get_all.return_value = mock_sboms

        # Override the dependency
        client.app.dependency_overrides[get_sbom_client] = (
            lambda: mock_client_dependency
        )

        try:
            response = client.get("/sbom/")
        finally:
            # Clean up the override
            client.app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["uid"] == "sbom1"
        assert data[1]["uid"] == "sbom2"
        mock_client_dependency.get_all.assert_called_once_with(
            namespace=None, cluster=None
        )

    def test_list_sbom_with_namespace_filter(self, client, mock_client_dependency):
        """Test GET /sbom/ with namespace filter."""
        mock_sboms = [SBOM(uid="sbom1", namespace="test-ns", cluster="cluster1")]
        mock_client_dependency.get_all.return_value = mock_sboms

        # Override the dependency
        client.app.dependency_overrides[get_sbom_client] = (
            lambda: mock_client_dependency
        )

        try:
            response = client.get("/sbom/?namespace=test-ns")
        finally:
            # Clean up the override
            client.app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["namespace"] == "test-ns"
        mock_client_dependency.get_all.assert_called_once_with(
            namespace="test-ns", cluster=None
        )

    def test_list_sbom_with_cluster_filter(self, client, mock_client_dependency):
        """Test GET /sbom/ with cluster filter."""
        mock_sboms = [SBOM(uid="sbom1", namespace="ns1", cluster="test-cluster")]
        mock_client_dependency.get_all.return_value = mock_sboms

        # Override the dependency
        client.app.dependency_overrides[get_sbom_client] = (
            lambda: mock_client_dependency
        )

        try:
            response = client.get("/sbom/?cluster=test-cluster")
        finally:
            # Clean up the override
            client.app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["cluster"] == "test-cluster"
        mock_client_dependency.get_all.assert_called_once_with(
            namespace=None, cluster="test-cluster"
        )

    def test_show_sbom_found(self, client, mock_client_dependency):
        """Test GET /sbom/{uid} when SBOM exists."""
        mock_sbom = SBOM(uid="test-sbom", namespace="test-ns", cluster="test-cluster")
        mock_client_dependency.get_by_uid.return_value = mock_sbom

        # Override the dependency
        client.app.dependency_overrides[get_sbom_client] = (
            lambda: mock_client_dependency
        )

        try:
            response = client.get("/sbom/test-sbom")
        finally:
            # Clean up the override
            client.app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert data["uid"] == "test-sbom"
        assert data["namespace"] == "test-ns"
        assert data["cluster"] == "test-cluster"
        mock_client_dependency.get_by_uid.assert_called_once_with("test-sbom")

    def test_show_sbom_not_found(self, client, mock_client_dependency):
        """Test GET /sbom/{uid} when SBOM doesn't exist."""
        mock_client_dependency.get_by_uid.return_value = None

        # Override the dependency
        client.app.dependency_overrides[get_sbom_client] = (
            lambda: mock_client_dependency
        )

        try:
            response = client.get("/sbom/nonexistent-sbom")
        finally:
            # Clean up the override
            client.app.dependency_overrides.clear()

        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "SBOM not found"
        mock_client_dependency.get_by_uid.assert_called_once_with("nonexistent-sbom")

    def test_list_sbom_empty_result(self, client, mock_client_dependency):
        """Test GET /sbom/ with empty result."""
        mock_client_dependency.get_all.return_value = []

        # Override the dependency
        client.app.dependency_overrides[get_sbom_client] = (
            lambda: mock_client_dependency
        )

        try:
            response = client.get("/sbom/")
        finally:
            # Clean up the override
            client.app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_sbom_acronym_in_response(self, client, mock_client_dependency):
        """Test that SBOM acronym naming is preserved in API responses."""
        mock_sbom = SBOM(uid="test-sbom", namespace="test-ns", cluster="test-cluster")
        mock_client_dependency.get_by_uid.return_value = mock_sbom

        # Override the dependency
        client.app.dependency_overrides[get_sbom_client] = (
            lambda: mock_client_dependency
        )

        try:
            response = client.get("/sbom/test-sbom")
        finally:
            # Clean up the override
            client.app.dependency_overrides.clear()

        assert response.status_code == 200
        # Verify the response structure matches our SBOM model
        data = response.json()
        assert "uid" in data
        assert "namespace" in data
        assert "cluster" in data

    def test_dependency_injection_working(self, client):
        """Test that dependency injection is properly configured."""
        mock_client = Mock()
        mock_client.get_all.return_value = []

        # Override the dependency
        client.app.dependency_overrides[get_sbom_client] = lambda: mock_client

        try:
            response = client.get("/sbom/")
        finally:
            # Clean up the override
            client.app.dependency_overrides.clear()

        assert response.status_code == 200
        # Verify the mock was called
        mock_client.get_all.assert_called_once()
