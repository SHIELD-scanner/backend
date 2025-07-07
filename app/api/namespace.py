from typing import List, Optional

from fastapi import APIRouter, Query

from app.core.namespaceClient import NamespaceClient as db
from app.models.namespace import Namespace

router = APIRouter()


@router.get("/", response_model=List[Namespace])
def list_namespaces(
    cluster: Optional[str] = Query(None),
):
    """List all Kubernetes namespaces in the cluster."""
    return db().get_all(cluster=cluster)
