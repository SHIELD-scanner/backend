import os

import sentry_sdk
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.application import router as application_router
from app.api.exposedsecret import router as exposedsecret_router
from app.api.health import router as health_router
from app.api.namespace import router as namespace_router
from app.api.pod import router as pod_router
from app.api.sbom import router as sbom_router
from app.api.sentry import router as sentry_router
from app.api.user import router as user_router
from app.api.vulnerability import router as vulnerability_router
from app.api.vulnerability_old import router as vulnerability_old_router

# Load environment variables first
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# Initialize Sentry after loading environment variables
sentry_dsn = os.getenv("SENTRY_DSN")
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        # Set a higher sample rate for debugging
        traces_sample_rate=1.0,
        # Add data like request headers and IP for users,
        # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
        send_default_pii=True,
        # Enable debug mode to see what's happening
        debug=True,
    )
    print(f"Sentry initialized with DSN: {sentry_dsn[:50]}...")
else:
    print("Warning: SENTRY_DSN not found in environment variables")

app = FastAPI(title="Trivy Ultimate Backend")

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
    vulnerability_old_router, prefix="/vulnerabilities-old", tags=["vulnerabilities"]
)

app.include_router(
    vulnerability_router, prefix="/vulnerabilities", tags=["vulnerabilities"]
)

app.include_router(sbom_router, prefix="/sbom", tags=["sbom"])
app.include_router(
    exposedsecret_router, prefix="/exposedsecrets", tags=["exposedsecrets"]
)

app.include_router(pod_router, prefix="/pods", tags=["pods"])
app.include_router(application_router, prefix="/application", tags=["application"])
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(sentry_router, prefix="/sentry", tags=["sentry"])
