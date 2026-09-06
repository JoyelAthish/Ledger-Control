import logging
from pathlib import Path
from dotenv import load_dotenv

# Point at the .env file explicitly (finance-controller/.env, one level above
# this file) instead of relying on auto-detection, which can misbehave under
# `uvicorn --reload`'s subprocess/watcher setup on some platforms.
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api import dashboard, exceptions, analytics, transactions, system

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("finance-controller")

app = FastAPI(
    title="Autonomous Finance Controller API",
    description="Backend for the reconciliation + AI exception resolution workstation.",
    version="1.0.0",
)

# CORS: allow the Vite dev server (and configurable origins in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(dashboard.router)
app.include_router(exceptions.router)
app.include_router(analytics.router)
app.include_router(transactions.router)
app.include_router(system.router)


@app.get("/")
def root():
    return {"service": "Autonomous Finance Controller API", "docs": "/docs"}
