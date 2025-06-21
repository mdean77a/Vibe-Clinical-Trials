# Qdrant Configuration Guide

## Overview
The application now uses persistent Qdrant storage instead of in-memory storage, solving the serverless persistence issue.

## Configuration Options

### 1. Qdrant Cloud (Recommended for Production)
1. Create account at https://cloud.qdrant.io
2. Create a new cluster
3. Get your cluster URL and API key
4. Set environment variables:
   ```bash
   QDRANT_URL=https://your-cluster-url.qdrant.tech:6333
   QDRANT_API_KEY=your-api-key-here
   ```

### 2. Local Docker Qdrant (Development)
1. Start Qdrant with Docker:
   ```bash
   docker run -p 6333:6333 qdrant/qdrant
   ```
2. Set environment variables:
   ```bash
   QDRANT_URL=http://localhost:6333
   # QDRANT_API_KEY not needed for local Docker
   ```

### 3. In-Memory Fallback (Testing Only)
- Leave both environment variables empty
- Data will not persist between restarts

## Local Development Setup

1. Copy environment file:
   ```bash
   cp .env.example .env
   # or
   cp backend/.env.example backend/.env
   ```

2. Edit `.env` with your Qdrant Cloud credentials:
   ```bash
   QDRANT_URL=https://your-cluster-url.qdrant.tech:6333
   QDRANT_API_KEY=your-api-key-here
   ```

3. Test the connection:
   ```bash
   cd backend
   python -c "from app.services.qdrant_service import QdrantService; QdrantService()"
   ```

## Production Deployment

1. Ensure environment variables are set in your deployment environment:
   - `QDRANT_URL` - Your Qdrant Cloud URL
   - `QDRANT_API_KEY` - Your Qdrant Cloud API key

2. Deploy your application:
   ```bash
   # Build frontend
   cd frontend && npm run build
   
   # Run backend
   cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

## Environment Variable Reference

- `QDRANT_URL`: Full URL to your Qdrant instance
- `QDRANT_API_KEY`: API key for authentication (required for Qdrant Cloud)

## Troubleshooting

### Connection Issues
- Verify URL format includes protocol (https:// or http://)
- Check API key is correct
- Ensure firewall allows outbound connections to Qdrant

### Local Testing
- Use the same cloud instance for both local and production
- Or switch between cloud/local by changing environment variables

### Docker Alternative
```bash
# Start local Qdrant with persistent storage
docker run -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant
```