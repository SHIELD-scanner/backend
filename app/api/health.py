from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.mongo_client import MongoDBClient

router = APIRouter()

@router.get("/")
def health_check():
    client = MongoDBClient()
    print(client.client.list_database_names())
    content = {"status": "ok", "message": "API is running smoothly", "version": "1.0.0"}
    return JSONResponse(status_code=418, content=content)