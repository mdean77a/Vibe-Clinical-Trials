"""
Main FastAPI application for Clinical Trial Accelerator.

This module sets up the FastAPI application, includes routers,
and handles application startup/shutdown events.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.icf_generation import router as icf_router
from .api.protocols import router as protocols_router
from .services.qdrant_service import get_qdrant_service

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

import os

if os.getenv("LANGCHAIN_TRACING_V2") == "true":
    logger.info("Langsmith tracing enabled")

else:
    logger.info("Langsmith tracing not enabled")


@asynccontextmanager
async def lifespan(app: FastAPI):
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
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(protocols_router)
app.include_router(icf_router)


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "message": "Clinical Trial Accelerator API",
        "version": "0.1.0",
        "status": "healthy",
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
