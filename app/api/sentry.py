from fastapi import APIRouter

from app.core.mongo_client import MongoDBClient

router = APIRouter()


@router.get("/debug")
def sentry_debug_check():
    division_by_zero = 1 / 0
    return {"status": "ok", "message": "Sentry debug endpoint hit"}
