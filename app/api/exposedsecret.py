from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.core.exposedsecretClient import ExposedsecretClient as db
from app.models.exposedsecret import Exposedsecret

router = APIRouter()

@router.get("/", response_model=List[Exposedsecret])
def list_exposedsecrets(
    namespace: Optional[str] = Query(None), cluster: Optional[str] = Query(None)
):
    """List all exposed secrets in the cluster."""
    return db().get_all(namespace=namespace, cluster=cluster)


@router.get("/{uid}", response_model=Exposedsecret)
def show_exposedsecret(uid: str):
    """Show a specific exposed secret by uid."""
    exposedsecret = db().get_by_uid(uid)
    if exposedsecret is None:
        raise HTTPException(status_code=404, detail="Exposed secret not found")
    return exposedsecret
