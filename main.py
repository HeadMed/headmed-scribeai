from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    try:
        from app.database.models import User, Patient, MedicalRecord
        from app.database.db import create_tables
        await create_tables()
        logger.info("Database tables created successfully")
        yield
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        yield
    finally:
        logger.info("Application shutdown complete")

app = FastAPI(
    title="HeadMed - Medical Transcription & Records API",
    description="A comprehensive medical records management system with audio transcription capabilities",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "HeadMed API is running",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

try:
    from app.api.v1.routes import router as api_router
    app.include_router(api_router, prefix="/api/v1", tags=["API v1"])
    logger.info("API routes loaded successfully")
except Exception as e:
    logger.error(f"Error loading API routes: {e}")
    from fastapi import APIRouter
    fallback_router = APIRouter()
    
    @fallback_router.get("/health")
    async def health_check():
        return {"status": "OK", "message": "Server is running (fallback mode)"}
    
    app.include_router(fallback_router, prefix="/api/v1")