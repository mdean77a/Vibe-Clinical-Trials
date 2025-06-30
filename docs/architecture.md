# 🧱 Architecture Document: Clinical Trial Accelerator v4.0

## 🔹 Technical Summary

Clinical Trial Accelerator is a monorepo-based, full-stack web application that enables clinical research coordinators to upload clinical trial protocol PDFs and generate multiple types of regulatory document drafts using AI-powered workflows. The system features a unified Qdrant storage architecture, modular LangGraph pipelines, and a human-in-the-loop review interface.

- **Frontend:** React + Vite + TypeScript + Tailwind CSS
- **Backend:** FastAPI (Python 3.11+) with Pydantic v2
- **AI Pipeline:** LangGraph with advanced RAG and real-time streaming
- **Primary LLM:** Claude Sonnet 4 with automatic GPT-4o fallback
- **Vector Database:** Qdrant (unified metadata + embeddings storage)
- **Document Types:** ICF (✅ Implemented), Site Checklist (🚧 UI Ready), SAP, DMP, CRF (Future)
- **PDF Processing:** PyMuPDF (current implementation)
- **Review Interface:** Section-based editing with approval workflows

## 🔹 High-Level Overview

- **Architecture Style:** Event-driven microservices with frontend/backend separation
- **Storage Strategy:** Unified Qdrant database for both protocol metadata and vector embeddings
- **Deployment:** Containerized monorepo; independent service deployment via Docker
- **MVP Workflow:**
  1. **Protocol Selection:** Display processed protocols from Qdrant metadata
  2. **Protocol Upload:** PDF upload → text extraction → Qdrant storage (metadata + vectors)
  3. **Document Type Selection:** Choose between ICF or Site Initiation Checklist
  4. **AI Generation:** RAG retrieval + LangGraph workflows for selected document type
  5. **Review & Edit:** Section-by-section review with approval tracking
  6. **Export:** Protocol-specific document naming and export

## 🔹 Architectural Design Patterns

- **Unified Storage Pattern:** Single Qdrant database handles both metadata queries and vector similarity search
- **RAG Pipeline Pattern:** Retrieval-Augmented Generation with OpenAI embeddings and semantic search
- **Command Pattern for Document Types:** Each document type (ICF, Site Checklist, SAP, DMP, CRF) implemented as modular LangGraph workflows
- **State Machine Pattern:** Document review process with defined states (Draft → Review → Approved → Locked)
- **Repository Pattern:** Abstracted data access layer for Qdrant operations
- **Observer Pattern:** Real-time section status updates and progress tracking
- **Human-in-the-Loop Pattern:** Mandatory review checkpoints with regeneration capabilities

## 🔹 Component Architecture

### Core Components

| Component                    | Responsibility                                                     | Technology Stack |
|------------------------------|-------------------------------------------------------------------|------------------|
| **Protocol Management**      | Upload, processing, metadata extraction, Qdrant storage          | FastAPI, PyMuPDF, Qdrant |
| **RAG Pipeline**             | Text chunking, embeddings, semantic retrieval                    | OpenAI API, Qdrant, LangChain |
| **Document Generation Hub**  | LangGraph workflow orchestration for all document types          | LangGraph, OpenAI GPT-4 |
| **Review Interface**         | Section editing, approval workflows, regeneration                 | React, Zustand, TipTap |
| **Protocol Selector**        | Landing page with processed protocol display                      | React, Qdrant metadata queries |
| **Export Engine**            | Document formatting, protocol-specific naming                    | Python, Jinja2 templates |
| **Session Management**       | Active protocol context, user state                              | FastAPI sessions, Redis (future) |

### Document Type Workflows

| Document Type              | LangGraph Workflow      | Key Sections                                    | Target Persona |
|----------------------------|-------------------------|-------------------------------------------------|----------------|
| **Informed Consent Form**  | `icf_generation.py`     | Study Purpose, Risks/Benefits, Rights, Contact | CRC, PI |
| **Site Initiation Checklist** | `site_checklist.py` | Regulatory, Training, Equipment, Documentation  | CRC |
| **Statistical Analysis Plan** | `sap_generation.py`   | Endpoints, Populations, Methods, Analysis       | Biostatistician |
| **Data Management Plan**   | `dmp_generation.py`     | Database Design, CDISC, Validation Rules       | Data Manager |
| **CRF Templates**          | `crf_generation.py`     | Visit Schedule, Data Collection, eCRF Design    | Data Manager |

## 🔹 Data Architecture

### Unified Qdrant Storage Schema

```python
# Protocol Document Structure in Qdrant
{
    "id": "protocol_uuid",
    "vector": [embedding_array],  # OpenAI text-embedding-ada-002
    "payload": {
        # Metadata fields
        "study_acronym": "STUDY-001",
        "protocol_title": "Phase II Clinical Trial...",
        "filename": "protocol_v2.1.pdf",
        "upload_date": "2024-01-15T10:30:00Z",
        "status": "completed",  # processing → completed
        "document_type": "protocol",
        
        # Content fields
        "chunk_text": "extracted_text_chunk",
        "page_number": 42,
        "section_title": "Primary Endpoints",
        "chunk_index": 156,
        
        # Processing metadata
        "extraction_confidence": 0.95,
        "processing_version": "v4.0"
    }
}
```

### Document Generation Context

```python
# Active Session Context
{
    "session_id": "uuid",
    "active_protocol": {
        "study_acronym": "STUDY-001",
        "protocol_title": "...",
        "qdrant_collection": "protocols_v4"
    },
    "document_context": {
        "document_type": "icf",  # icf | site_checklist | sap | dmp | crf
        "generation_status": "in_progress",
        "sections_completed": ["introduction", "purpose"],
        "sections_pending": ["risks", "benefits", "contact"]
    }
}
```

## 🔹 Project Structure (Enhanced Monorepo)

```plaintext
clinical-trial-accelerator/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── protocols.py          # Protocol CRUD, upload, selection
│   │   │   ├── icf_generation.py     # ICF-specific generation endpoints
│   │   │   ├── site_checklist.py     # Site checklist generation
│   │   │   ├── dcc_documents.py      # SAP, DMP, CRF generation (Phase 2)
│   │   │   └── review.py             # Document review and approval
│   │   ├── core/
│   │   │   ├── qdrant_client.py      # Unified Qdrant operations
│   │   │   ├── rag_pipeline.py       # RAG retrieval and context
│   │   │   └── session_manager.py    # Active protocol context
│   │   ├── services/
│   │   │   ├── pdf_processor.py      # PyMuPDF processing (REMOVED - unused Docling code)
│   │   │   ├── document_generator.py # LangGraph workflow dispatcher
│   │   │   ├── icf_service.py        # ICF-specific business logic
│   │   │   └── qdrant_service.py     # Vector operations, metadata queries
│   │   ├── workflows/                # LangGraph definitions
│   │   │   ├── icf_workflow.py       # ICF generation nodes
│   │   │   ├── site_workflow.py      # Site checklist nodes
│   │   │   ├── sap_workflow.py       # Statistical Analysis Plan
│   │   │   ├── dmp_workflow.py       # Data Management Plan
│   │   │   └── crf_workflow.py       # CRF template generation
│   │   ├── models/
│   │   │   ├── protocol.py           # Protocol metadata models
│   │   │   ├── document.py           # Document section models
│   │   │   └── review.py             # Review state models
│   │   └── main.py
│   ├── tests/
│   │   ├── test_qdrant_service.py
│   │   ├── test_icf_generation.py
│   │   ├── test_rag_pipeline.py
│   │   └── test_workflows/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ProtocolSelector.tsx   # Landing page protocol list
│   │   │   ├── ProtocolUpload.tsx     # New protocol upload
│   │   │   ├── DocumentTypeSelector.tsx # ICF vs Site Checklist choice
│   │   │   └── icf/
│   │   │       ├── ICFGenerationDashboard.tsx
│   │   │       └── ICFSection.tsx     # Section-level editing
│   │   ├── pages/
│   │   │   ├── HomePage.tsx           # Protocol selection landing
│   │   │   ├── DocumentTypeSelection.tsx
│   │   │   ├── InformedConsentPage.tsx
│   │   │   └── SiteChecklistPage.tsx
│   │   ├── services/
│   │   │   ├── api.ts                 # Backend API client
│   │   │   ├── protocolService.ts     # Protocol operations
│   │   │   └── documentService.ts     # Document generation API
│   │   ├── store/
│   │   │   ├── protocolStore.ts       # Active protocol context
│   │   │   ├── documentStore.ts       # Document generation state
│   │   │   └── reviewStore.ts         # Section review state
│   │   ├── utils/
│   │   │   ├── mockData.ts            # Development mock data
│   │   │   └── constants.ts           # Document type definitions
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
├── docs/
│   ├── architecture.md                # This document
│   ├── prd.md                         # Product requirements
│   └── api-documentation.md
├── scripts/
│   ├── setup-qdrant.sh               # Qdrant initialization
│   ├── test-local.sh                 # Local testing
│   └── deploy-local.sh               # Local deployment
└── docker-compose.yml                # Local development stack
```

## 🔹 Technology Stack v4.0

### Core Technologies

| Category                 | Technology                | Version        | Purpose                                    |
|--------------------------|---------------------------|----------------|--------------------------------------------|
| **Backend Language**     | Python                    | 3.11+          | API, AI workflows, data processing         |
| **Frontend Language**    | TypeScript                | 5.x            | Type-safe React development                |
| **Backend Framework**    | FastAPI                   | 0.104+         | High-performance async API                 |
| **Frontend Framework**   | React + Vite              | 18.x + 5.x     | Modern SPA with fast dev server            |
| **AI Orchestration**     | LangGraph                 | Latest         | Multi-node AI workflows with streaming     |
| **Primary LLM**          | Claude Sonnet 4           | 20250514       | Primary document generation                |
| **Fallback LLM**         | OpenAI GPT-4o             | Latest         | Automatic fallback for resilience         |
| **Embeddings**           | OpenAI API                | Latest         | Vector embeddings with mock fallback      |
| **Vector Database**      | Qdrant                    | 1.6+           | **Unified storage** - metadata + vectors  |
| **PDF Processing**       | PyMuPDF                   | 1.23+          | Text extraction and chunking |
| **UI Framework**         | Tailwind CSS              | 3.x            | Utility-first styling                      |
| **State Management**     | Zustand                   | 4.x            | Lightweight React state                    |
| **Rich Text Editor**     | TipTap                    | 2.x            | Section-level content editing              |

### Development & Operations

| Category                 | Technology                | Purpose                                    |
|--------------------------|---------------------------|--------------------------------------------|
| **Containerization**     | Docker + Docker Compose   | Local development environment              |
| **Testing Framework**    | Pytest + Vitest          | Backend + frontend testing                 |
| **E2E Testing**          | Playwright                | End-to-end workflow testing                |
| **Code Quality**         | Black, isort, ESLint      | Code formatting and linting                |
| **Type Checking**        | mypy, TypeScript strict   | Static type validation                     |
| **API Documentation**    | FastAPI OpenAPI           | Auto-generated API docs                    |
| **Monitoring**           | Structured JSON logging   | Application observability                  |

## 🔹 Infrastructure & Deployment v4.0

### Development Environment

```yaml
# docker-compose.yml
version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - QDRANT_URL=http://qdrant:6333
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - qdrant
  
  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000
```

### Deployment Strategy

- **Local Development:** Docker Compose with hot reload
- **MVP Deployment:** Single-server Docker deployment
- **Production Path:** Kubernetes-ready containerization
- **Database:** Memory-based Qdrant (MVP) → Qdrant Cloud (production)
- **Monitoring:** Application logs → Structured logging → Observability platform
- **Scaling:** Horizontal scaling of backend services, Qdrant cluster mode

### Environment Configuration

```python
# backend/app/core/config.py
class Settings(BaseSettings):
    # Core application
    app_name: str = "Clinical Trial Accelerator"
    version: str = "4.0"
    debug: bool = False
    
    # Qdrant configuration
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection_name: str = "protocols_v4"
    qdrant_vector_size: int = 1536  # OpenAI embedding dimension
    
         # LLM configuration
     anthropic_api_key: str
     primary_model: str = "claude-sonnet-4-20250514"
     fallback_model: str = "gpt-4o"
     
     # OpenAI configuration (embeddings + fallback)
     openai_api_key: str
     openai_embedding_model: str = "text-embedding-ada-002"
    
    # Document processing
    max_file_size_mb: int = 50
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # Session management
    session_timeout_hours: int = 4
    max_concurrent_sessions: int = 2
```

## 🔹 Security Architecture v4.0

### Data Protection

- **No PHI Storage:** System designed to handle protocols without patient health information
- **Encryption:** AES-256 encryption for data at rest and in transit
- **Access Control:** Role-based permissions (CRC, PI, Biostatistician, Data Manager, Admin)
- **Audit Logging:** Complete audit trail for all user actions and document generations
- **Session Security:** JWT-based authentication with configurable timeouts

### Compliance Framework

```python
# Security middleware
class SecurityMiddleware:
    def __init__(self):
        self.audit_logger = AuditLogger()
        self.access_control = RoleBasedAccessControl()
    
    async def log_action(self, user_id: str, action: str, resource: str):
        await self.audit_logger.log({
            "timestamp": datetime.utcnow(),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "ip_address": request.client.host,
            "user_agent": request.headers.get("user-agent")
        })
```

## 🔹 Performance & Scalability

### Performance Targets

- **API Response Time:** 95th percentile < 2 seconds
- **Document Generation:** Complete ICF generation < 5 minutes
- **File Upload:** 50MB protocols upload < 60 seconds
- **Concurrent Users:** Support 20 simultaneous users (MVP)
- **Qdrant Queries:** Vector similarity search < 500ms

### Optimization Strategies

- **Async Processing:** FastAPI async/await for all I/O operations
- **Connection Pooling:** Qdrant client connection management
- **Caching Strategy:** Redis for session data and frequent queries
- **Streaming Responses:** Real-time document generation progress
- **Lazy Loading:** Frontend component and data lazy loading

## 🔹 Error Handling & Monitoring

### Error Classification

```python
class ErrorTypes(Enum):
    PROTOCOL_UPLOAD_ERROR = "protocol_upload_error"
    PDF_EXTRACTION_ERROR = "pdf_extraction_error"
    QDRANT_CONNECTION_ERROR = "qdrant_connection_error"
    OPENAI_API_ERROR = "openai_api_error"
    DOCUMENT_GENERATION_ERROR = "document_generation_error"
    VALIDATION_ERROR = "validation_error"
```

### Monitoring Stack

- **Application Metrics:** Custom FastAPI middleware for request/response metrics
- **Health Checks:** `/health` endpoint with dependency checks (Qdrant, OpenAI)
- **Structured Logging:** JSON format with correlation IDs
- **Error Tracking:** Centralized error collection and alerting
- **Performance Monitoring:** Response time percentiles and throughput metrics

## 🔹 Testing Strategy v4.0

### Test Pyramid

```plaintext
                    /\
                   /  \
                  / E2E \     ← Playwright (critical user journeys)
                 /______\
                /        \
               / Integration \   ← API + Qdrant + LangGraph workflows
              /______________\
             /                \
            /   Unit Tests      \  ← Individual components, services, utilities
           /____________________\
```

### Test Coverage Requirements

- **Unit Tests:** 80% code coverage minimum
- **Integration Tests:** All API endpoints and database operations
- **E2E Tests:** Complete user workflows (upload → generate → review → export)
- **AI Pipeline Tests:** LangGraph workflow validation with mock responses
- **Performance Tests:** Load testing for concurrent users and large documents

## 🔹 Current Implementation Status

### **🎯 FIRST MVP - 100% COMPLETE & PRODUCTION READY:**
- **Primary Feature:** ICF Generation with real-time streaming and section editing
- **Protocol Management:** Upload, processing, Qdrant storage, and retrieval
- **RAG Pipeline:** Advanced semantic search with section-specific retrieval
- **LLM Resilience:** Claude Sonnet 4 primary with automatic GPT-4o fallback
- **Frontend:** React application with complete ICF workflow (HomePage → Protocol Selection → ICF Generation)
- **API Infrastructure:** FastAPI with comprehensive error handling

### **📋 FIRST MVP SCOPE:**
- **Core Workflow:** Protocol Upload → Protocol Selection → ICF Generation → Review & Edit → Export
- **Target User:** Clinical Research Coordinator (CRC)
- **Document Type:** Informed Consent Form only
- **Status:** Ready for immediate deployment and user validation

### **🚀 FUTURE PHASES:**
- **Phase 2:** Site Checklist generation + Document type selection interface
- **Phase 3:** Additional document types (SAP, DMP, CRF templates)
- **Phase 4:** Multi-user workflows and advanced features

## 🔹 Migration & Upgrade Path

### v3 → v4 Migration

1. **Database Migration:** Migrate existing data to unified Qdrant schema
2. **API Versioning:** Maintain backward compatibility with v3 endpoints
3. **Frontend Updates:** Gradual migration to new component architecture
4. **Document Types:** Phase rollout of new document generation capabilities

### Future Architecture Evolution

- **v5.0:** Multi-tenant architecture with organization isolation
- **v6.0:** Real-time collaboration features and advanced approval workflows
- **v7.0:** Integration with external clinical trial management systems
- **v8.0:** Advanced AI features (custom model fine-tuning, domain-specific embeddings)

---

**Architecture Document v4.0** - *Updated for enhanced technical specifications, unified Qdrant storage, and comprehensive document generation workflows*
