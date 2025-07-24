from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from app.core.namespaceClient import NamespaceClient
from app.models.namespace import Namespace

router = APIRouter()


def get_namespace_client() -> NamespaceClient:
    """Dependency to get NamespaceClient instance."""
    return NamespaceClient()


@router.get("/", response_model=List[Namespace])
def list_namespaces(
    cluster: Optional[str] = Query(None),
    db: NamespaceClient = Depends(get_namespace_client),
):
    """List all Kubernetes namespaces in the cluster."""
    return db.get_all(cluster=cluster)
