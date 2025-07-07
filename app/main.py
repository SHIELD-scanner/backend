from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.application import router as application_router
from app.api.health import router as health_router
from app.api.namespace import router as namespace_router
from app.api.pod import router as pod_router
from app.api.vulnerability import router as vulnerability_router

app = FastAPI(title="Trivy Ultimate Backend")

load_dotenv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": "Welcome to the Trivy Ultimate Backend API. Visit /docs for API documentation."
    }


app.include_router(namespace_router, prefix="/namespaces", tags=["namespaces"])
app.include_router(
    vulnerability_router, prefix="/vulnerabilities-old", tags=["vulnerabilities"]
)
app.include_router(pod_router, prefix="/pods", tags=["pods"])
app.include_router(application_router, prefix="/application", tags=["application"])
app.include_router(health_router, prefix="/health", tags=["health"])
