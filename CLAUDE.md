# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Clinical Trial Accelerator is an AI-powered web application that processes clinical trial protocol PDFs and generates regulatory documents (Informed Consent Forms, site checklists) using LangGraph workflows. Recently migrated from Vite to Next.js 15 with App Router.

## Architecture

**Frontend**: Next.js 15 with App Router + TypeScript + Tailwind CSS  
**Backend**: FastAPI + Python 3.13+ managed with `uv`  
**Storage**: Qdrant vector database (unified metadata + embeddings)  
**AI Stack**: LangGraph workflows, Claude Sonnet 4 primary, OpenAI GPT-4o fallback  
**Testing**: Jest (frontend), pytest (backend), Playwright (E2E)

## Development Commands

### Root Level (use these primarily)
```bash
npm test                # Full test suite
npm run test:quick      # Fast tests without linting  
npm run test:backend    # Backend tests only
npm run test:frontend   # Frontend tests only
npm run test:coverage   # Coverage reports
npm run lint            # Run all linting
npm run lint:fix        # Auto-fix linting issues
npm run dev:backend     # Start backend dev server (port 8000)
npm run dev:frontend    # Start frontend dev server (port 3000)
npm run build           # Build both services
```

### Frontend Specific
```bash
cd frontend
npm run type-check      # TypeScript checking
npm run test:watch      # Jest in watch mode
npm run test:e2e        # Playwright E2E tests
```

### Backend Specific  
```bash
cd backend
uv run pytest          # Run tests directly
uv run black .          # Format code
uv run isort .          # Sort imports
uv run mypy app/        # Type checking
```

## Key Implementation Patterns

### Unified Storage Strategy
- **Single Qdrant database** handles both metadata queries and vector similarity search
- No traditional SQL database - everything stored in Qdrant collections
- Protocol documents stored as chunks with embeddings and metadata

### AI Pipeline Architecture
- **RAG Pipeline**: Retrieval-Augmented Generation with semantic search
- **LangGraph Workflows**: Modular, parallelized document generation with streaming
- **Fallback Strategy**: Automatic Claude → OpenAI switching for reliability

### Frontend-Backend Integration
- **Streaming Generation**: Real-time token updates from FastAPI to Next.js frontend
- **API Client**: Centralized in `frontend/src/utils/api.ts`
- **Type Safety**: Shared TypeScript interfaces between frontend and FastAPI Pydantic models

## Directory Structure

```
/
├── frontend/           # Next.js 15 App Router
│   ├── app/           # Route pages (page.tsx files)
│   ├── src/
│   │   ├── components/ # Reusable React components
│   │   ├── types/     # TypeScript definitions
│   │   └── utils/     # API client + utilities
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── api/       # Route handlers
│   │   ├── services/  # Business logic
│   │   └── models.py  # Pydantic data models
├── docs/              # Architecture documentation (auto-included in Cursor context)
└── scripts/           # Development automation
```

## Configuration Details

**Python**: Requires 3.13+, uses `uv` for dependency management  
**Node**: Requires 22.x  
**TypeScript**: Strict mode enabled with `@/*` path aliasing  
**Code Quality**: Black + isort (Python), ESLint + TypeScript (frontend)  
**Testing Coverage**: Target 80%+ with pytest-cov and Jest coverage

## Development Workflow

1. **Protocol Upload**: PDF → PyMuPDF text extraction → Qdrant embedding storage
2. **Document Generation**: RAG retrieval + LangGraph workflows → streaming generation
3. **Frontend Interface**: React components with real-time updates and human-in-the-loop editing

## Git Branch Management

**IMPORTANT**: When merging branches, ALWAYS preserve commit history using `git merge --no-ff` to maintain a complete development record. Never use fast-forward merges that lose branch context.

## Environment Setup

Copy `.env.example` to `.env` and configure:
- `ANTHROPIC_API_KEY` (primary LLM)
- `OPENAI_API_KEY` (fallback + embeddings)  
- `QDRANT_URL` and `QDRANT_API_KEY`

## Vercel Deployment

**Production Setup**: Hybrid Next.js + Python serverless deployment
- **Frontend**: Next.js 15 deployed to Vercel edge functions
- **Backend**: Python serverless functions in `/api/index.py` (custom HTTP handler)
- **PDF Processing**: Client-side extraction using PDF.js to avoid 250MB serverless limit
- **Streaming**: Full Server-Sent Events (SSE) support for both full and section regeneration

### Deployment Architecture
- **Local Dev**: FastAPI backend (port 8000) + Next.js frontend (port 3000)
- **Vercel Production**: Unified deployment with serverless functions handling all backend logic
- **Dependencies**: Synchronized between `pyproject.toml` and `requirements.txt`
- **Key Files**: `/api/index.py`, `/vercel.json`, `/requirements.txt`

## Recent Updates (Latest Session)

### ✅ Embedding Strategy Consolidation (Completed)
- **Problem**: Redundant embedding implementations in `qdrant_service.py` and `langchain_qdrant_service.py`
- **Solution**: Unified all embedding operations through LangChain with centralized configuration
- **Key Changes**:
  - Created `backend/app/config.py` with centralized `EMBEDDING_MODEL = "text-embedding-3-small"`
  - Removed duplicate `get_embeddings()` and `search_protocol_documents()` methods from `qdrant_service.py`
  - Updated all services to use centralized config constants
  - Fixed Vercel serverless function (`/api/index.py`) that was missed initially
- **Result**: Single embedding model configuration, no redundancy, all new documents use `text-embedding-3-small`
- **Tests**: All 76 backend + 153 frontend tests passing
- **Files Updated**:
  - `backend/app/config.py` - New centralized configuration
  - `backend/app/services/qdrant_service.py` - Removed redundant embedding code
  - `backend/app/services/langchain_qdrant_service.py` - Uses centralized config
  - `backend/app/api/protocols.py` - Uses centralized config
  - `/api/index.py` - Fixed Vercel function to use centralized config
  - Test files updated to remove obsolete embedding tests

### ✅ Repository Cleanup (Completed)
- **Branch Management**: Cleaned up merged feature branches
- **Deleted Branches**: `cleanupEmbeddings`, `cleanupQdrant`, `feature/regeneration-comments`
- **Current State**: Clean repository with only `main` branch (local + remote)
- **Merge Strategy**: Used `--no-ff` merges to preserve development history
- **Ready**: All changes committed and ready for team collaboration

## Current Status

**✅ Fully Implemented**: ICF generation with streaming, protocol upload system, complete React interface, streaming section regeneration  
**✅ Production Ready**: Vercel deployment configuration complete, all tests passing
**🚧 In Progress**: Site checklist generation (UI complete, API pending)  
**📋 Future**: Statistical Analysis Plans, Data Management Plans, CRF templates

## Testing Status

**Frontend**: 153/153 tests passing ✅  
**Backend**: 98/98 functional tests passing ✅  
**E2E**: Ready for Playwright testing on Vercel deployment  
**Coverage**: Frontend >80%, Backend functional coverage complete