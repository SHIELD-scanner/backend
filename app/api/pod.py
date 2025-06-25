from typing import List, Optional

from fastapi import APIRouter, Query

from app.core.podClient import PodClient as db
from app.models.pod import Pod

router = APIRouter()


@router.get("/", response_model=List[Pod])
def list_pods(
    namespace: Optional[str] = Query(None),
    cluster: Optional[str] = Query(None),
):
    """List all vulnerabilities in the cluster."""
    return db().get_all(
        namespace=namespace,
        cluster=cluster,
    )


@router.get("/{cluster}", response_model=List[Pod])
def show_cluster(cluster: str):
    """Show a specific pod by cluster."""
    return db().get_by_cluster(cluster=cluster)


@router.get("/{cluster}/{namespace}", response_model=List[Pod])
def show_namespace(cluster: str, namespace: str):
    """Show a specific pod by namespace."""
    return db().get_by_namespace(cluster=cluster, namespace=namespace)


@router.get("/{cluster}/{namespace}/{name}", response_model=Pod)
def show_name(cluster: str, namespace: str, name: str):
    """Show a specific pod by name."""
    return db().get_by_name(cluster=cluster, namespace=namespace, name=name)
