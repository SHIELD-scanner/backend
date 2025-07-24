"""Unit tests for ExposedSecret model."""
import pytest
from pydantic import ValidationError
from app.models.exposedsecret import ExposedSecret


class TestExposedSecret:
    """Test cases for ExposedSecret model."""

    def test_exposed_secret_creation_with_all_fields(self):
        """Test creating ExposedSecret with all fields."""
        secret = ExposedSecret(
            uid="test-uid-123",
            namespace="test-namespace",
            cluster="test-cluster"
        )
        
        assert secret.uid == "test-uid-123"
        assert secret.namespace == "test-namespace"
        assert secret.cluster == "test-cluster"

    def test_exposed_secret_creation_with_defaults(self):
        """Test creating ExposedSecret with default values."""
        secret = ExposedSecret()
        
        assert secret.uid == ""
        assert secret.namespace == ""
        assert secret.cluster == ""

    def test_exposed_secret_creation_partial_fields(self):
        """Test creating ExposedSecret with partial fields."""
        secret = ExposedSecret(uid="test-uid")
        
        assert secret.uid == "test-uid"
        assert secret.namespace == ""
        assert secret.cluster == ""

    def test_exposed_secret_field_validation(self):
        """Test that all fields accept string values."""
        secret = ExposedSecret(
            uid="123",
            namespace="ns-123",
            cluster="cluster-123"
        )
        
        assert isinstance(secret.uid, str)
        assert isinstance(secret.namespace, str)
        assert isinstance(secret.cluster, str)

    def test_exposed_secret_dict_conversion(self):
        """Test converting ExposedSecret to dictionary."""
        secret = ExposedSecret(
            uid="test-uid",
            namespace="test-ns",
            cluster="test-cluster"
        )
        
        secret_dict = secret.model_dump()
        expected = {
            "uid": "test-uid",
            "namespace": "test-ns", 
            "cluster": "test-cluster"
        }
        
        assert secret_dict == expected

    def test_exposed_secret_from_dict(self):
        """Test creating ExposedSecret from dictionary."""
        data = {
            "uid": "test-uid",
            "namespace": "test-ns",
            "cluster": "test-cluster"
        }
        
        secret = ExposedSecret(**data)
        
        assert secret.uid == "test-uid"
        assert secret.namespace == "test-ns"
        assert secret.cluster == "test-cluster"

    def test_exposed_secret_equality(self):
        """Test ExposedSecret equality comparison."""
        secret1 = ExposedSecret(uid="test", namespace="ns1", cluster="cluster1")
        secret2 = ExposedSecret(uid="test", namespace="ns1", cluster="cluster1")
        secret3 = ExposedSecret(uid="different", namespace="ns1", cluster="cluster1")
        
        assert secret1 == secret2
        assert secret1 != secret3
