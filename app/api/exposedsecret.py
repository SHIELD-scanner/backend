from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.exposedsecretClient import ExposedsecretClient
from app.models.exposedsecret import ExposedSecret

router = APIRouter()


def get_exposedsecret_client() -> ExposedsecretClient:
    """Dependency to get ExposedsecretClient instance."""
    return ExposedsecretClient()


@router.get("/", response_model=List[ExposedSecret])
def list_exposedsecrets(
    namespace: Optional[str] = Query(None),
    cluster: Optional[str] = Query(None),
    db: ExposedsecretClient = Depends(get_exposedsecret_client),
):
    """List all exposed secrets in the cluster."""
    return db.get_all(namespace=namespace, cluster=cluster)


@router.get("/{uid}", response_model=ExposedSecret)
def show_exposedsecret(
    uid: str, db: ExposedsecretClient = Depends(get_exposedsecret_client)
):
    """Show a specific exposed secret by uid."""
    exposedsecret = db.get_by_uid(uid)
    if exposedsecret is None:
        raise HTTPException(status_code=404, detail="Exposed secret not found")
    return exposedsecret
