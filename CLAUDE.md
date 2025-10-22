# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

On startup, check with the user to see if they want to start a new session using the /session-start command.

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

**IMPORTANT**:  When starting a new feature always create a new branch from main.

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

### ✅ Backend Test Coverage Increased to 83% (Completed - 2025-10-22)
- **Goal**: Increase backend test coverage from 77% to 80%+
- **Achievement**: Reached **83% coverage** (+6 percentage points, exceeded target by 3%)
- **Test Statistics**:
  - Total tests: 198 (was 160)
  - New tests added: 38
  - All tests passing in 2.08 seconds ✅
  - Zero production code changes (test-only improvements)

#### Module-Specific Coverage Improvements
- **main.py**: 0% → 97% (+97%) - NEW test file with 12 tests
- **qdrant_service.py**: 71% → 99% (+28%) - Added 18 edge case tests
- **document_generator.py**: 78% → 86% (+8%) - Added 8 workflow tests
- **Overall backend**: 77% → 83% (+6%)

#### New Test Files Created
**tests/test_main.py** (12 tests, 274 lines):
- Application lifespan manager (startup/shutdown)
- Root and health check endpoints
- CORS middleware and router configuration
- Confirmed lifespan manager is active code (not dead code)

#### Enhanced Test Files
**tests/test_qdrant_service.py** (+18 tests, +341 lines):
- Protocol retrieval by collection (raw and LangChain metadata)
- Collection name lookup and deletion
- Protocol collection pattern validation
- Edge cases: empty collections, read errors, connection failures

**tests/test_document_generator.py** (+8 tests, +226 lines):
- Workflow invoke edge cases (messages without .content)
- Missing section error handling
- StreamingICFWorkflow section branches (all 7 sections)
- Streaming fallback on error

#### Testing Strategy
- Mock-based unit tests (no external dependencies)
- FastAPI dependency override pattern
- Comprehensive edge case coverage
- Both success and failure path testing

#### Files Modified (Test-Only)
- `backend/tests/test_main.py` (NEW)
- `backend/tests/test_qdrant_service.py` (ENHANCED)
- `backend/tests/test_document_generator.py` (ENHANCED)
- **No production code touched** ✅

#### Branch Management
- Branch: `increaseCoverage`
- Merged to main with `--no-ff` (preserves commit history)
- Commits: 2 comprehensive commits
- Merge commit: d6fc24b
- Branch cleaned up (deleted locally and remotely)

#### Acceptable Gaps
- **icf_service.py** (43%): Complex async streaming (integration-tested)
- **handler.py** (0%): Vercel serverless entry point (deployment-tested)

---

## Previous Sessions

### ✅ LLM Configuration Consolidation (Completed)
- **Problem**: LLM model names and configurations scattered across multiple files with redundant fallback logic
- **Solution**: Centralized all LLM configurations and implemented proper working model pattern
- **Key Changes**:
  - Added centralized LLM constants to `backend/app/config.py`:
    - `PRIMARY_LLM_MODEL = "gpt-4o-mini"` (OpenAI primary model)
    - `FALLBACK_LLM_MODEL = "claude-sonnet-4-20250514"` (Anthropic fallback model)
    - `LLM_MAX_TOKENS = 8192`, `LLM_TEMPERATURE = 0.1`
  - Implemented proper working model initialization in `document_generator.py`:
    - Try PRIMARY_LLM_MODEL first, then FALLBACK_LLM_MODEL
    - Smart provider detection based on model name prefixes ("gpt", "o1", "claude")
    - Clear error handling when both models fail to initialize
    - Single working model used throughout the session
  - Removed ~100 lines of redundant fallback logic from generation functions:
    - Eliminated complex streaming fallback code
    - Simplified `_generate_section_with_llm` to use working model only
    - No more runtime fallback attempts during text generation
  - Updated `icf_service.py` to use centralized config constants instead of hardcoded values
- **Result**: Clean, logical LLM configuration strategy with single source of truth
- **Tests**: All 76 backend + 153 frontend tests passing
- **Files Updated**:
  - `backend/app/config.py` - Added LLM configuration constants
  - `backend/app/services/document_generator.py` - Implemented working model pattern, removed redundant fallbacks
  - `backend/app/services/icf_service.py` - Uses centralized config
- **Branch**: Merged `feature/llm-config-consolidation` to main with `--no-ff` to preserve history

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
- **Deleted Branches**: `cleanupEmbeddings`, `cleanupQdrant`, `feature/regeneration-comments`, `feature/llm-config-consolidation`
- **Current State**: Clean repository with only `main` branch (local)
- **Merge Strategy**: Used `--no-ff` merges to preserve development history
- **Ready**: All changes committed and ready for team collaboration

### ✅ Unused Protocol Routes Cleanup (Completed)
- **Problem**: 3 unused API endpoints and their client methods cluttering the codebase
- **Solution**: Removed unused routes and simplified protocol upload architecture
- **Removed Endpoints**:
  - `POST /api/protocols/` - `create_new_protocol()` - replaced by `upload_protocol_text()`
  - `GET /api/protocols/{protocol_id}` - `get_protocol()` - never called by frontend
  - `GET /api/protocols/collection/{collection_name}` - `get_protocol_by_collection()` - never called by frontend
- **Key Changes**:
  - Removed unused backend endpoints from `backend/app/api/protocols.py` (~135 lines)
  - Removed unused imports: `ProtocolCreate`, `QdrantError`
  - Removed unused frontend API client methods from `frontend/src/utils/api.ts` (~80 lines)
  - Simplified `ProtocolUpload.tsx` by removing conditional upload fallback logic
  - Removed test classes for deleted endpoints from `backend/tests/test_api_protocols.py`
- **Result**: Cleaner API surface area, ~215 lines of dead code removed, simplified upload flow
- **Tests**: All 56 backend + 153 frontend tests passing ✅
- **Files Updated**:
  - `backend/app/api/protocols.py` - Removed 3 endpoints and unused imports
  - `frontend/src/utils/api.ts` - Removed 5 unused client methods
  - `frontend/src/components/ProtocolUpload.tsx` - Simplified upload logic
  - `backend/tests/test_api_protocols.py` - Removed tests for deleted endpoints
- **Branch**: Merged `unusedRoutes` to main with `--no-ff` to preserve history

## Current Status

**✅ Fully Implemented**: ICF generation with streaming, protocol upload system, complete React interface, streaming section regeneration  
**✅ Production Ready**: Vercel deployment configuration complete, all tests passing
**🚧 In Progress**: Site checklist generation (UI complete, API pending)  
**📋 Future**: Statistical Analysis Plans, Data Management Plans, CRF templates

## Testing Status

**Frontend**: 153/153 tests passing ✅
**Backend**: 198/198 tests passing ✅
**E2E**: Ready for Playwright testing on Vercel deployment
**Coverage**:
- Frontend: >80% ✅
- Backend: 83% (exceeded 80% target) ✅
  - main.py: 97%
  - qdrant_service.py: 99%
  - langchain_qdrant_service.py: 96%
  - document_generator.py: 86%
  - icf_generation.py: 89%
  - protocols.py: 82%