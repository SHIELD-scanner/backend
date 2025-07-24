from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.core.sbomClient import SbomClient as db
from app.models.sbom import Sbom

router = APIRouter()


@router.get("/", response_model=List[Sbom])
def list_sbom(
    namespace: Optional[str] = Query(None), cluster: Optional[str] = Query(None)
):
    """List all sbom in the cluster."""
    return db().get_all(namespace=namespace, cluster=cluster)


@router.get("/{uid}", response_model=Sbom)
def show_sbom(uid: str):
    """Show a specific SBOM by uid."""
    sbom = db().get_by_uid(uid)
    if sbom is None:
        raise HTTPException(status_code=404, detail="SBOM not found")
    return sbom
