# Vercel serverless handler for FastAPI
from .main import app as fastapi_app

# This is what Vercel will use
app = fastapi_app
