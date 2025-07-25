"""Unit tests for SBOM model."""
from app.models.sbom import SBOM


class TestSBOM:

    """Test cases for SBOM model."""

    def test_sbom_creation_with_all_fields(self):
        """Test creating SBOM with all fields."""
        sbom = SBOM(
            uid="sbom-uid-123",
            namespace="test-namespace",
            cluster="test-cluster"
        )
        
        assert sbom.uid == "sbom-uid-123"
        assert sbom.namespace == "test-namespace"
        assert sbom.cluster == "test-cluster"

    def test_sbom_creation_with_defaults(self):
        """Test creating SBOM with default values."""
        sbom = SBOM()
        
        assert sbom.uid == ""
        assert sbom.namespace == ""
        assert sbom.cluster == ""

    def test_sbom_creation_partial_fields(self):
        """Test creating SBOM with partial fields."""
        sbom = SBOM(uid="sbom-uid")
        
        assert sbom.uid == "sbom-uid"
        assert sbom.namespace == ""
        assert sbom.cluster == ""

    def test_sbom_field_validation(self):
        """Test that all fields accept string values."""
        sbom = SBOM(
            uid="123",
            namespace="ns-123",
            cluster="cluster-123"
        )
        
        assert isinstance(sbom.uid, str)
        assert isinstance(sbom.namespace, str)
        assert isinstance(sbom.cluster, str)

    def test_sbom_dict_conversion(self):
        """Test converting SBOM to dictionary."""
        sbom = SBOM(
            uid="sbom-uid",
            namespace="test-ns",
            cluster="test-cluster"
        )
        
        sbom_dict = sbom.model_dump()
        expected = {
            "uid": "sbom-uid",
            "namespace": "test-ns", 
            "cluster": "test-cluster"
        }
        
        assert sbom_dict == expected

    def test_sbom_from_dict(self):
        """Test creating SBOM from dictionary."""
        data = {
            "uid": "sbom-uid",
            "namespace": "test-ns",
            "cluster": "test-cluster"
        }
        
        sbom = SBOM(**data)
        
        assert sbom.uid == "sbom-uid"
        assert sbom.namespace == "test-ns"
        assert sbom.cluster == "test-cluster"

    def test_sbom_equality(self):
        """Test SBOM equality comparison."""
        sbom1 = SBOM(uid="test", namespace="ns1", cluster="cluster1")
        sbom2 = SBOM(uid="test", namespace="ns1", cluster="cluster1")
        sbom3 = SBOM(uid="different", namespace="ns1", cluster="cluster1")
        
        assert sbom1 == sbom2
        assert sbom1 != sbom3

    def test_sbom_acronym_naming(self):
        """Test that SBOM follows acronym naming convention."""
        # This test verifies that we're using SBOM (all caps) 
        # as per industry standard for Software Bill of Materials
        sbom = SBOM()
        assert sbom.__class__.__name__ == "SBOM"
