**Development Task List: Clinical Trial Editor UI (Sprint Breakdown)**

---

## 🚀 Sprint 1: Project Setup & Foundational UI

### Frontend
- [ ] Initialize a Vite project using the React + TypeScript template
- [ ] Integrate Tailwind CSS with the Vite project following official setup
- [ ] Configure module aliasing in `vite.config.ts` to support `@/components/...`
- [ ] Build reusable UI components using shadcn/ui:
  - `Button`, `Input`, `Textarea`, `Card`

### Backend
- [ ] Use `uv` to manage Python virtual environment and dependencies
- [ ] Serve FastAPI backend directly via `uvicorn` for development
- [ ] Include `.env` file to manage config (model keys, ports, etc.)

---

## 🚀 Sprint 2: Editor Wireframe UI & Protocol Viewer

### Frontend
- [ ] Implement `EditorWireframe` with 3-column layout (Sidebar, Editor, Viewer)
- [ ] Add status indicators (Badges with color codes: Draft, Approved, etc.)
- [ ] Maintain active section selection in React state
- [ ] Create a read-only scrollable panel displaying protocol context
- [ ] Add protocol search functionality for reference during editing
- [ ] Highlight relevant protocol segments for current section

---

## 🚀 Sprint 3: Backend API & Upload Flow

### Backend
- [ ] `POST /upload-protocol`
  - Accepts multipart PDF and user-provided study acronym
  - Parses text using PyMuPDF (no file persistence)
  - Returns protocol processing status
- [ ] Extract full text and page layout from uploaded PDFs
- [ ] Chunk extracted text into optimal segments for RAG
- [ ] Store protocol metadata in Qdrant document metadata fields

---

## 🚀 Sprint 4: Unified Qdrant Processing

### Backend
- [ ] Single operation: embed chunks + store metadata in Qdrant
- [ ] Set up cloud-based Qdrant connection
- [ ] `GET /protocols`
  - Returns list of processed protocols from Qdrant metadata
  - Includes study_acronym, protocol_title, status, upload_date
- [ ] Protocol selection and context retrieval for RAG

---

## 🚀 Sprint 5: RAG Pipeline & Regeneration

### Backend
- [ ] `POST /regenerate-section`
  - Accepts section ID and prompt
  - Performs RAG and returns regenerated content

### LangGraph
- [ ] Define LangGraph nodes for ICF sections (Title, Purpose, Risks, etc.)
- [ ] Each node receives embedded context from Qdrant
- [ ] Generate section content using LangChain + RAG strategy

---

## 🚀 Sprint 6: Document Interaction Features

### Frontend
- [ ] Allow editable text areas to update local state on input
- [ ] On "Regenerate", call API with user-supplied prompt and current section
- [ ] On "Undo", revert to last saved draft
- [ ] On "Approve", change status and disable further editing

---

## 🚀 Sprint 7: Authentication System (Future Phase)

### Backend
- [ ] Create login form with email + password (no registration for MVP)
- [ ] Generate and return JWT token on successful login
- [ ] Attach token in frontend API requests via Authorization header
- [ ] Add FastAPI dependency to validate token on protected endpoints
**Note**: Authentication deferred for MVP - single user assumption

---

## 🚀 Sprint 8: Final Integration & Deployment

### Backend
- [ ] Configure cloud-based Qdrant for MVP deployment
- [ ] Implement cloud Qdrant URL configuration for production upgrade
- [ ] FastAPI endpoint optimization and testing

### Frontend
- [ ] Production build optimization for local deployment
- [ ] Environment-aware API configuration (local vs. production)

---

This sprint plan structures the development roadmap into 8 focused phases, aligning with your MVP scope.

