# Vercel serverless handler for FastAPI
from .main import app

# This is what Vercel will use
handler = app