import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database.base import Base
from app.database.session import engine
import app.models  # noqa: F401 — registers all models with Base.metadata
from app.api.auth import router as auth_router
from app.api.clothing import router as clothing_router
from app.api.outfits import router as outfits_router

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure upload directory exists before the server starts accepting requests
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    # Startup: create all DB tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Using AI provider: %s", settings.AI_PROVIDER)
    yield
    # Shutdown: release connection pool
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(clothing_router)
app.include_router(outfits_router)

# StaticFiles constructor checks the directory at import time, so we must
# create it here — not only inside lifespan.
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.get("/health")
async def health_check() -> dict[str, Any]:
    return {"status": "ok", "app": settings.APP_NAME}
