"""Unit tests for Namespace model."""
import pytest
from pydantic import ValidationError
from app.models.namespace import Namespace


class TestNamespace:
    """Test cases for Namespace model."""

    def test_namespace_creation_with_all_fields(self):
        """Test creating Namespace with all fields."""
        namespace = Namespace(
            cluster="test-cluster",
            name="test-namespace",
            uid="namespace-uid-123"
        )

        assert namespace.cluster == "test-cluster"
        assert namespace.name == "test-namespace"
        assert namespace.uid == "namespace-uid-123"

    def test_namespace_field_validation(self):
        """Test that namespace fields accept appropriate values."""
        namespace_data = {
            "cluster": "test-cluster",
            "name": "test-namespace",
            "uid": "namespace-uid"
        }

        namespace = Namespace(**namespace_data)

        assert isinstance(namespace.cluster, str)
        assert isinstance(namespace.name, str)
        assert isinstance(namespace.uid, str)

    def test_namespace_dict_conversion(self):
        """Test converting Namespace to dictionary."""
        namespace = Namespace(
            cluster="test-cluster",
            name="test-ns",
            uid="ns-uid"
        )

        namespace_dict = namespace.model_dump()

        assert "cluster" in namespace_dict
        assert "name" in namespace_dict
        assert "uid" in namespace_dict
        assert namespace_dict["cluster"] == "test-cluster"

    def test_namespace_from_dict(self):
        """Test creating Namespace from dictionary."""
        data = {
            "cluster": "test-cluster",
            "name": "test-ns",
            "uid": "ns-uid"
        }

        namespace = Namespace(**data)

        assert namespace.cluster == "test-cluster"
        assert namespace.name == "test-ns"
        assert namespace.uid == "ns-uid"

    def test_namespace_equality(self):
        """Test Namespace equality comparison."""
        ns1 = Namespace(cluster="cluster1", name="ns1", _uid="uid1")
        ns2 = Namespace(cluster="cluster1", name="ns1", _uid="uid1")
        ns3 = Namespace(cluster="cluster2", name="ns1", _uid="uid1")
        
        assert ns1 == ns2
        assert ns1 != ns3
