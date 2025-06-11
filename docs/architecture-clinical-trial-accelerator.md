# 🧱 Architecture Document: Clinical Trial Accelerator

## 🔹 Technical Summary

Clinical Trial Accelerator is a monorepo-based, full-stack web application that enables users to upload a clinical trial protocol PDF and generate regulatory document drafts (e.g., Informed Consent, Site Initiation Checklist) using LangGraph for modular and parallel AI flows.

- **Frontend:** React + Vite
- **Backend:** FastAPI (Python)
- **AI Pipeline:** LangGraph with modular parallel nodes
- **Output Engine:** LaTeX-based PDF generation
- **PDF Parsing:** PyMuPDF → Docling (planned)
- **Editable Review Layer:** Per-section editing, notes, approvals

## 🔹 High-Level Overview

- **Architecture Style:** Client–server with frontend/backend separation
- **Deployment:** Monorepo structure; backend and frontend deployed independently via CI/CD
- **Interaction Flow:**
  1. User uploads a protocol PDF
  2. Backend extracts and pre-processes text (PyMuPDF → Docling upgrade planned)
  3. Based on user’s selected document type, LangGraph invokes relevant section prompts
  4. Parallel generation nodes return completed document sections
  5. Frontend renders editable sections with tracking (review state + notes)
  6. User finalizes document → compiled via LaTeX to PDF for export

## 🔹 Architectural / Design Patterns Adopted

- **LangGraph-Orchestrated Parallelism:** Section prompts for documents like Informed Consent run in parallel using LangGraph nodes.
- **Command Pattern for Document Types:** Each document format (e.g., Informed Consent, Checklist) is implemented as a class/module with a known interface.
- **API-First Design:** All frontend-to-backend interaction is via FastAPI routes.
- **Modular Frontend State:** Section-level editing status and notes managed per document type using slice-based global store (e.g., Zustand/Redux).
- **Human-in-the-Loop Design:** Explicit validation points, approval flags, and review controls before document finalization.

## 🔹 Component View

| Component               | Role                                                                 |
|-------------------------|----------------------------------------------------------------------|
| `PDF Upload Service`    | Handles file reception, validation, and text extraction              |
| `Document Generator`    | Entry point for document creation; dispatches LangGraph workflows    |
| `LangGraph Flows`       | Defines prompts and section nodes per document type                  |
| `Section Assembly`      | Combines generated content into structured document objects          |
| `Review Interface`      | Frontend UI for section preview/edit/approve and notes               |
| `LaTeX Compiler`        | Converts reviewed document object to PDF                             |
| `API Layer`             | Routes for upload, generation, editing state, and finalization       |

## 🔹 Project Structure (Monorepo)

```plaintext
clinical-trial-accelerator/
├── backend/
│   ├── app/
│   │   ├── api/                # FastAPI routes
│   │   ├── core/               # Business logic
│   │   ├── langgraph_flows/    # Modular LangGraph definitions
│   │   ├── models/             # Pydantic models
│   │   ├── services/           # PDF parser, generator, LaTeX, etc.
│   │   └── main.py             # FastAPI entrypoint
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── features/
│   │   ├── services/           # API clients
│   │   ├── store/              # State (per section, per doc)
│   │   └── App.tsx
│   └── vite.config.ts
├── docs/
│   └── architecture.md         # This doc, PRD, design notes, etc.
├── scripts/                    # Build, test, deploy
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── .github/workflows/          # CI/CD configs
└── README.md
```

## 🔹 Definitive Tech Stack

| Category             | Technology            | Version       | Purpose                                |
|----------------------|-----------------------|----------------|----------------------------------------|
| Language             | Python                | 3.11.x         | Backend/AI Orchestration               |
|                      | TypeScript            | 5.x            | Frontend                               |
| Framework            | FastAPI               | Latest         | REST API Layer                         |
|                      | React + Vite          | 18.x           | Frontend                               |
| AI Engine            | LangGraph             | Latest         | Multi-agent workflows                  |
| PDF Parser           | PyMuPDF               | Latest         | Initial PDF Parsing                    |
|                      | Docling               | (Planned)      | Semantic markup parser                 |
| Output Engine        | LaTeX (via TeXLive)   | N/A            | PDF generation                         |
| State Management     | Zustand or Redux      | Latest         | Global section/edit state              |
| Infra                | Docker + GitHub Actions | N/A          | CI/CD, deploy                          |
| Security             | JWT (user auth, later) | Planned        | User identity / audit trace (future)   |
| Testing              | Pytest, Playwright    | Latest         | Unit + E2E tests                       |

## 🔹 Infrastructure & Deployment

- **CI/CD Tooling:** GitHub Actions for lint/test/build/deploy
- **Dev/Staging/Prod Environments:** Single-container deploy for MVP (Docker Compose or ECS/Fargate)
- **Deployment Targets:** 
  - Backend → AWS (ECS or Lambda)
  - Frontend → Vercel or S3 + CloudFront
- **Monitoring & Logging:** Standardized structured logging (JSON logs, correlation IDs)
- **Rollback Strategy:** GitHub action to redeploy previous tagged image

## 🔹 Error Handling Strategy

- **LangGraph Errors:** Captured per node, errors surfaced per section
- **External API Failures:** Retry logic w/ exponential backoff (if applicable)
- **Frontend:** All backend errors normalized and displayed clearly to user
- **Logging:** Structured logs (JSON), capture `document_id`, `section_name`, `error_type`

## 🔹 Coding Standards

- **Python:** `black`, `isort`, `mypy`
- **TypeScript:** `eslint`, `prettier`, strict null checks enabled
- **Structure Enforcement:** Modular, clearly named LangGraph flows per document type
- **Testing:** All AI prompt functions must have unit tests and at least one integration test

## 🔒 Security Best Practices

- No PHI allowed in the system
- Editor must approve all generated content before export
- No automatic external integrations (e.g., IRBs) at this stage
- Secrets managed via environment config (not embedded in source)
- User inputs sanitized before template insertion
