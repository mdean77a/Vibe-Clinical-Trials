"""
Vercel serverless function entry point for FastAPI backend.
Simplified version without lifespan events for serverless compatibility.
"""

import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Import routers directly
from app.api.protocols import router as protocols_router
from app.api.icf_generation import router as icf_router

# Create simplified FastAPI app without lifespan events
app = FastAPI(
    title="Clinical Trial Accelerator API",
    description="AI-powered clinical trial document generation backend",
    version="0.1.0",
    # No lifespan for serverless
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(protocols_router)
app.include_router(icf_router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Clinical Trial Accelerator API", 
        "version": "0.1.0",
        "environment": "serverless"
    }

# Health check endpoint
@app.get("/api/health")
async def health():
    return {"status": "healthy", "environment": "serverless"}

# Wrap FastAPI with Mangum for ASGI compatibility
handler = Mangum(app, lifespan="off")