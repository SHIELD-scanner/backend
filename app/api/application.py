from typing import Optional

from fastapi import APIRouter, Query, Depends

from app.core.old_vulnerabilityClient import VulnerabilityClient
from app.core.podClient import PodClient

router = APIRouter()


def get_vulnerability_client() -> VulnerabilityClient:
    """Dependency to get VulnerabilityClient instance."""
    return VulnerabilityClient()


def get_pod_client() -> PodClient:
    """Dependency to get PodClient instance."""
    return PodClient()


@router.get("/sidebar", response_model=dict)
def sidebar(
    cluster: Optional[str] = Query(None),
    namespace: Optional[str] = Query(None),
    vulnerability_db: VulnerabilityClient = Depends(get_vulnerability_client)
):
    """List all vulnerabilities in the cluster."""
    return {"vulnerability_total": len(vulnerability_db.get_all(cluster=cluster, namespace=namespace))}


@router.get("/dashboard", response_model=dict)
def dashboard(
    cluster: Optional[str] = Query(None),
    namespace: Optional[str] = Query(None),
    vulnerability_db: VulnerabilityClient = Depends(get_vulnerability_client),
    pod_db: PodClient = Depends(get_pod_client)
):
    """List all vulnerabilities in the cluster."""
    items = vulnerability_db.get_all(cluster=cluster, namespace=namespace)

    pods = pod_db.get_all(cluster=cluster, namespace=namespace)
    return {
        "severity_counts": {
            "total": len(items),
            "CRITICAL": len([item for item in items if item.severity == "CRITICAL"]),
            "HIGH": len([item for item in items if item.severity == "HIGH"]),
            "MEDIUM": len([item for item in items if item.severity == "MEDIUM"]),
            "LOW": len([item for item in items if item.severity == "LOW"]),
            "UNKNOWN": len([item for item in items if item.severity == "UNKNOWN"]),
        },
        "pods": {
            "total": len(pods),
            "namespaces": list(set([pod.namespace for pod in pods])),
            "clusters": list(set([pod.cluster for pod in pods])),
        },
    }
