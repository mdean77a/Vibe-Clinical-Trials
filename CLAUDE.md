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

### ✅ Streaming Section Regeneration (Completed)
- **Feature**: Real-time token streaming for individual ICF section regeneration
- **Implementation**: Added `sections_filter` parameter to `generate_icf_streaming()` method
- **UX Improvement**: Users now see immediate feedback instead of waiting without visual progress
- **Technical**: Uses existing SSE infrastructure for consistency with full generation
- **Files Updated**: 
  - `backend/app/services/icf_service.py` - Added sections filtering support
  - `backend/app/api/icf_generation.py` - Modified `/regenerate-section` to use streaming
  - `frontend/src/utils/api.ts` - Updated `regenerateSection` to consume SSE stream
  - `frontend/src/components/icf/ICFGenerationDashboard.tsx` - Added streaming UI handling

### ✅ Test Suite Fixes (Completed)
- **Frontend Tests**: Fixed all 153 tests passing (was 13 failing due to PDF extractor mocking)
- **Backend Tests**: Updated 98 tests passing (improved LangChain service mocking)
- **Key Issues Resolved**: 
  - `import.meta` compatibility in Jest environment
  - Async/await handling in React Testing Library
  - PDF extractor module mocking for CI/CD reliability
- **Files Updated**: `frontend/src/components/__tests__/ProtocolUpload.test.tsx`

### ✅ Git History Management (Completed)
- **Merged**: 16 commits from `frontendPdf` branch into `main` using `--no-ff` merge
- **Preserved**: Complete development history showing Vercel deployment journey
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