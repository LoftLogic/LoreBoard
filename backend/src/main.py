"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router
from src.config import get_settings
from src.telemetry.routes import router as telemetry_router
from src.telemetry.tracer import configure_logging, get_logger

_settings = get_settings()
log = get_logger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    log.info("app.startup", env=_settings.app_env)
    yield
    log.info("app.shutdown")


app = FastAPI(
    title="Loreboard Agent Backend",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")
app.include_router(telemetry_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "env": _settings.app_env}
