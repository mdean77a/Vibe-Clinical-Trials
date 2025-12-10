"""
Main FastAPI application for Clinical Trial Accelerator.

This module sets up the FastAPI application, includes routers,
and handles application startup/shutdown events.
"""

import logging
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.icf_generation import router as icf_router
from .api.protocols import router as protocols_router
from .services.qdrant_service import get_qdrant_service

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Suppress httpx INFO logs that appear as errors in Vercel
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

import os

if os.getenv("LANGCHAIN_TRACING_V2") == "true":
    logger.info("Langsmith tracing enabled")

else:
    logger.info("Langsmith tracing not enabled")


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """
    Application lifespan manager.

    Handles startup and shutdown events for the FastAPI application.
    """
    # Startup
    logger.info("Starting Clinical Trial Accelerator backend...")
    try:
        # Initialize Qdrant service (replaces SQLite database initialization)
        qdrant_service = get_qdrant_service()
        logger.info("Qdrant service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Qdrant service: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Clinical Trial Accelerator backend...")


# Create FastAPI application
app = FastAPI(
    title="Clinical Trial Accelerator API",
    description="AI-powered clinical trial document generation backend",
    version="0.1.0",
    lifespan=lifespan,
    redoc_url=None,  # Disabled - use /docs for API documentation
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(protocols_router)
app.include_router(icf_router)


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint for health check."""
    return {
        "message": "Clinical Trial Accelerator API",
        "version": "0.1.0",
        "status": "healthy",
    }


@app.get("/api/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
