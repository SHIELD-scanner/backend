from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.sbomClient import SbomClient
from app.models.sbom import SBOM

router = APIRouter()


def get_sbom_client() -> SbomClient:
    """Dependency to get SbomClient instance."""
    return SbomClient()


@router.get("/", response_model=List[SBOM])
def list_sbom(
    namespace: Optional[str] = Query(None),
    cluster: Optional[str] = Query(None),
    db: SbomClient = Depends(get_sbom_client),
):
    """List all sbom in the cluster."""
    return db.get_all(namespace=namespace, cluster=cluster)


@router.get("/{uid}", response_model=SBOM)
def show_sbom(uid: str, db: SbomClient = Depends(get_sbom_client)):
    """Show a specific SBOM by uid."""
    sbom = db.get_by_uid(uid)
    if sbom is None:
        raise HTTPException(status_code=404, detail="SBOM not found")
    return sbom
