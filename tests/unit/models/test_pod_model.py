"""Unit tests for Pod model."""
from app.models.pod import Pod


class TestPod:

    """Test cases for Pod model."""

    def test_pod_creation_with_minimal_fields(self):
        """Test creating Pod with minimal required fields."""
        pod = Pod(
            name="test-pod",
            namespace="test-namespace",
            cluster="test-cluster"
        )
        
        assert pod.name == "test-pod"
        assert pod.namespace == "test-namespace"
        assert pod.cluster == "test-cluster"

    def test_pod_field_validation(self):
        """Test that pod fields accept appropriate values."""
        pod_data = {
            "name": "test-pod",
            "namespace": "test-namespace",
            "cluster": "test-cluster",
            "_uid": "pod-uid-123"
        }
        
        pod = Pod(**pod_data)
        
        assert isinstance(pod.name, str)
        assert isinstance(pod.namespace, str)
        assert isinstance(pod.cluster, str)

    def test_pod_dict_conversion(self):
        """Test converting Pod to dictionary."""
        pod_data = {
            "name": "test-pod",
            "namespace": "test-ns",
            "cluster": "test-cluster",
            "_uid": "pod-uid"
        }
        
        pod = Pod(**pod_data)
        pod_dict = pod.model_dump()
        
        assert "name" in pod_dict
        assert "namespace" in pod_dict
        assert "cluster" in pod_dict
        assert pod_dict["name"] == "test-pod"

    def test_pod_from_dict(self):
        """Test creating Pod from dictionary."""
        data = {
            "name": "test-pod",
            "namespace": "test-ns",
            "cluster": "test-cluster"
        }
        
        pod = Pod(**data)
        
        assert pod.name == "test-pod"
        assert pod.namespace == "test-ns"
        assert pod.cluster == "test-cluster"

    def test_pod_equality(self):
        """Test Pod equality comparison."""
        pod1 = Pod(name="pod1", namespace="ns1", cluster="cluster1")
        pod2 = Pod(name="pod1", namespace="ns1", cluster="cluster1")
        pod3 = Pod(name="pod2", namespace="ns1", cluster="cluster1")
        
        assert pod1 == pod2
        assert pod1 != pod3
