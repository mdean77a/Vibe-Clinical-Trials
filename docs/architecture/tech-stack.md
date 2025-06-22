# Vibe Clinical Trials Tech Stack

This document defines the technology choices for the Clinical Trial Accelerator project based on the PRD specifications.

## Overview

The Clinical Trial Accelerator is an AI-powered web application for generating clinical trial documents from protocol PDFs using RAG (Retrieval-Augmented Generation) and LangGraph workflows.

## Development Environment

- **Local Development**: Initial MVP deployment
- **Cloud Migration Path**: Serverless-compatible architecture for future cloud deployment

## Technology Stack

| Category | Technology | Version/Details | Purpose | Rationale |
| :------- | :--------- | :-------------- | :------ | :-------- |
| **Frontend Framework** | React | 18.x with TypeScript | Web UI framework | Modern, component-based UI development |
| **Frontend Language** | TypeScript | 5.3.3 | Type-safe frontend development | Type safety, better developer experience |
| **UI Styling** | Tailwind CSS | 3.x | Utility-first CSS framework | Rapid UI development, consistent styling |
| **Routing** | React Router | 7.x | Client-side routing | Standard React routing solution |
| **Backend Language** | Python | 3.11+ | Backend API and AI services | AI/ML ecosystem, LangChain/LangGraph support |
| **Backend Framework** | FastAPI | Latest | REST API framework | Modern, async, automatic API documentation |
| **Vector Database** | Qdrant | Cloud/Memory | Vector storage and retrieval | Unified metadata + vector storage, serverless compatible |
| **PDF Processing** | PyMuPDF | Latest | PDF text extraction | Reliable PDF parsing without file persistence |
| **LLM Provider (Primary)** | Anthropic Claude | Sonnet 4 (claude-sonnet-4-20250514) | Document generation | Advanced reasoning, high-quality output |
| **LLM Provider (Fallback)** | OpenAI | GPT-4o | Fallback document generation | Reliability when primary fails |
| **Embeddings** | OpenAI | text-embedding-ada-002 | Text embeddings for RAG | Industry standard, cost-effective |
| **AI Orchestration** | LangGraph | 0.2.0 | AI workflow management | Parallel processing, streaming generation |
| **AI Framework** | LangChain | 0.1.0 | RAG pipeline | Comprehensive AI application framework |
| **Frontend Testing** | Vitest | Latest | Unit testing | Fast, Vite-integrated testing |
| **Test Utilities** | React Testing Library | Latest | Component testing | Best practices for React testing |
| **API Testing** | pytest | Latest | Backend testing | Python standard testing framework |
| **Development Server** | Vite | 5.x | Frontend dev server | Fast HMR, modern build tool |
| **API Documentation** | OpenAPI/Swagger | 3.0 | API specification | Auto-generated from FastAPI |
| **Version Control** | Git | - | Source control | Industry standard |
| **Code Quality** | ESLint + Prettier | Latest | Code formatting and linting | Consistent code style |

## API Architecture

- **Frontend API Module**: Centralized `utils/api.ts` with namespaced endpoints
- **Backend API**: RESTful endpoints with FastAPI
- **Real-time Updates**: Server-Sent Events (SSE) for streaming generation

## Data Storage Strategy

### Qdrant Configuration
- **Development**: In-memory Qdrant for local development
- **Production Path**: Qdrant Cloud for scalability
- **Data Model**:
  ```json
  {
    "study_acronym": "string",
    "protocol_title": "string", 
    "filename": "string",
    "upload_date": "timestamp",
    "status": "processing|completed",
    "document_id": "uuid"
  }
  ```

### No Traditional Database
- **Rationale**: Qdrant provides both vector search and metadata storage
- **Benefits**: Simplified architecture, unified data access

## AI/ML Pipeline

### RAG Pipeline Components
1. **Text Extraction**: PyMuPDF (no file persistence)
2. **Chunking**: 500-1000 token chunks
3. **Embeddings**: OpenAI text-embedding-ada-002 (with mock fallback for dev)
4. **Vector Store**: Qdrant collections per protocol
5. **Retrieval**: Section-specific semantic search
6. **Generation**: LangGraph workflows with streaming

### LangGraph Workflow Features
- **Parallel Section Generation**: True parallel processing
- **Real-time Streaming**: Token-level updates
- **Error Handling**: Automatic retry logic
- **Section Regeneration**: Individual section updates

## Document Types

### Implemented
- ✅ **Informed Consent Form (ICF)**: Fully implemented with streaming
- 🚧 **Site Initiation Checklist**: UI ready, API pending

### Future Phases
- Statistical Analysis Plan (SAP)
- Data Management Plan (DMP)
- Case Report Form (CRF) Templates

## Development Workflow

### Local Development Setup
```bash
# Frontend
npm install
npm run dev

# Backend
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

### Environment Variables
```bash
# Frontend (.env.local)
REACT_APP_API_URL=http://localhost:8000

# Backend (.env)
ANTHROPIC_API_KEY=your_key
OPENAI_API_KEY=your_key
QDRANT_URL=memory://  # or cloud URL
```

## Security Considerations

- **No PHI Storage**: System design prevents patient data storage
- **API Keys**: Environment variables, never committed
- **CORS**: Configured for local development
- **Future**: JWT authentication for multi-user support

## Performance Targets

- **Document Generation**: <5 minutes for complete ICF
- **API Response**: <2 seconds for 95% of requests
- **RAG Retrieval**: <3 seconds per query
- **Upload Size**: 50MB maximum PDF size

## Deployment Strategy

### MVP (Local Deployment)
- Frontend: Vite dev server
- Backend: FastAPI with Uvicorn
- Vector DB: In-memory Qdrant

### Future Production
- Frontend: Static build served via CDN
- Backend: Containerized, serverless-ready
- Vector DB: Qdrant Cloud
- Infrastructure: Cloud provider TBD

## Monitoring and Logging

### Current (MVP)
- Console logging for debugging
- Basic error handling
- LocalStorage fallback for resilience

### Future
- Structured JSON logging
- Application monitoring (TBD)
- Error tracking service (TBD)

## Testing Strategy

- **Unit Tests**: Vitest (frontend), pytest (backend)
- **Integration Tests**: API endpoint testing
- **E2E Tests**: Future phase with Playwright
- **Coverage Target**: 80% for critical paths

## Notes

- All technology choices support serverless deployment
- Architecture designed for future cloud migration
- No traditional database reduces complexity
- Focus on proven, stable technologies for reliability