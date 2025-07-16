import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.application import router as application_router
from app.api.health import router as health_router
from app.api.namespace import router as namespace_router
from app.api.pod import router as pod_router
from app.api.vulnerability import router as vulnerability_router
from app.api.vulnerability_old import router as vulnerability_old_router

import sentry_sdk

sentry_dsn = os.getenv("DSN")
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        # Add data like request headers and IP for users,
        # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
        send_default_pii=True,
    )

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
    vulnerability_old_router, prefix="/vulnerabilities-old", tags=["vulnerabilities"]
)

app.include_router(
    vulnerability_router, prefix="/vulnerabilities", tags=["vulnerabilities"]
)

app.include_router(pod_router, prefix="/pods", tags=["pods"])
app.include_router(application_router, prefix="/application", tags=["application"])
app.include_router(health_router, prefix="/health", tags=["health"])

# @app.get("/sentry-debug")
# async def trigger_error():
#     division_by_zero = 1 / 0