from fastapi import APIRouter, Depends

from app.core.mongo_client import MongoDBClient

router = APIRouter()


def get_database_client() -> MongoDBClient:
    """Dependency to get MongoDBClient instance."""
    return MongoDBClient()


@router.get("/")
def health_check(db: MongoDBClient = Depends(get_database_client)):
    try:
        # Test database connection
        db.client.list_database_names()
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    
    return {
        "status": "ok", 
        "message": "API is running smoothly", 
        "version": "1.0.0",
        "database": db_status
    }
