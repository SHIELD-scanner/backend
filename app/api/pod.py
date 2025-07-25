from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.podClient import PodClient
from app.models.pod import Pod

router = APIRouter()


def get_pod_client() -> PodClient:
    """Dependency to get PodClient instance."""
    return PodClient()


@router.get("/", response_model=List[Pod])
def list_pods(
    namespace: Optional[str] = Query(None),
    cluster: Optional[str] = Query(None),
    db: PodClient = Depends(get_pod_client),
):
    """List all vulnerabilities in the cluster."""
    return db.get_all(
        namespace=namespace,
        cluster=cluster,
    )


@router.get("/{cluster}", response_model=List[Pod])
def show_cluster(cluster: str, db: PodClient = Depends(get_pod_client)):
    """Show a specific pod by cluster."""
    return db.get_by_cluster(cluster=cluster)


@router.get("/{cluster}/{namespace}", response_model=List[Pod])
def show_namespace(
    cluster: str, namespace: str, db: PodClient = Depends(get_pod_client)
):
    """Show a specific pod by namespace."""
    return db.get_by_namespace(cluster=cluster, namespace=namespace)


@router.get("/{cluster}/{namespace}/{name}", response_model=Pod)
def show_name(
    cluster: str, namespace: str, name: str, db: PodClient = Depends(get_pod_client)
):
    """Show a specific pod by name."""
    pod = db.get_by_name(cluster=cluster, namespace=namespace, name=name)
    if pod is None:
        raise HTTPException(status_code=404, detail="Pod not found")
    return pod
