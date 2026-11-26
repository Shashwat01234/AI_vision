"""
AI-Powered Accessibility Assistant API
Main FastAPI Application Entrypoint
"""
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database.database import create_tables
from app.routes import upload, image, document, audio, history, settings as settings_routes
from app.ai_models.model_manager import model_manager

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown events.
    """
    logger.info("Initializing AI Accessibility Assistant Backend...")

    # 1. Ensure storage directories exist
    settings.ensure_directories()
    logger.info("Storage directories initialized.")

    # 2. Initialize database tables synchronously
    try:
        create_tables()
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Database table creation failed: {e}")

    # 3. Initialize model manager
    model_manager.initialise()
    logger.info("Model manager initialized.")

    yield

    logger.info("Shutting down AI Accessibility Assistant Backend...")


# FastAPI instance
app = FastAPI(
    title="AI Accessibility Assistant API",
    description="Multimodal AI Backend for Visually Impaired Students",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS middleware
origins = settings.cors_origins_list
if not origins:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static audio files for direct playback/streaming
audio_dir = settings.get_audio_dir()
app.mount("/static/audio", StaticFiles(directory=str(audio_dir)), name="audio_static")

# Mount upload directory for image previewing
upload_dir = settings.get_upload_dir()
app.mount("/static/uploads", StaticFiles(directory=str(upload_dir)), name="uploads_static")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception processing {request.method} {request.url}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred.",
            "error": str(exc) if settings.DEBUG else None,
        },
    )


# Health check
@app.get("/api/health", tags=["Health"])
@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app": "AI Accessibility Assistant API",
        "version": "1.0.0",
        "models": model_manager.status_report(),
    }


# Include API routers
app.include_router(upload.router, prefix="/api")
app.include_router(image.router, prefix="/api")
app.include_router(document.router, prefix="/api")
app.include_router(audio.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(settings_routes.router, prefix="/api")
