from typing import Optional

from fastapi import APIRouter, Query

from app.core.podClient import PodClient as PodClient
from app.core.vulnerabilityClient import VulnerabilityClient as Vulnerabilitydb

router = APIRouter()


@router.get("/sidebar", response_model=dict)
def sidebar(
    cluster: Optional[str] = Query(None),
    namespace: Optional[str] = Query(None),
):
    """List all vulnerabilities in the cluster."""
    return {
        "vulnerability_total": len(
            Vulnerabilitydb().get_all(cluster=cluster, namespace=namespace)
        )
    }


@router.get("/dashboard", response_model=dict)
def dashboard(
    cluster: Optional[str] = Query(None),
    namespace: Optional[str] = Query(None),
):
    """List all vulnerabilities in the cluster."""
    items = Vulnerabilitydb().get_all(cluster=cluster, namespace=namespace)

    pods = PodClient().get_all(cluster=cluster, namespace=namespace)
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
