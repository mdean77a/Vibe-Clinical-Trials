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

## 🚀 Sprint 2: Editor Wireframe UI & PDF Viewer

### Frontend
- [ ] Implement `EditorWireframe` with 3-column layout (Sidebar, Editor, Viewer)
- [ ] Add status indicators (Badges with color codes: Draft, Approved, etc.)
- [ ] Maintain active section selection in React state
- [ ] Create a read-only scrollable panel displaying text
- [ ] Add an `Input` to filter or search text
- [ ] Highlight segments matching current section or search term

---

## 🚀 Sprint 3: Backend API & Upload Flow

### Backend
- [ ] `POST /upload-protocol`
  - Accepts multipart PDF
  - Parses text, stores PDF to disk
  - Returns protocol ID
- [ ] Use PyMuPDF to extract full text and page layout from uploaded PDFs
- [ ] Save PDFs in `/uploads` directory with unique IDs
- [ ] Chunk extracted text into logical sections

---

## 🚀 Sprint 4: Embedding & Retrieval Engine

### Backend
- [ ] Embed each chunk using OpenAI embedding model and store vectors in Qdrant
- [ ] `GET /sections`
  - Accepts protocol ID
  - Returns embedded section metadata and text chunks

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

## 🚀 Sprint 7: Authentication System

### Backend
- [ ] Create login form with email + password (no registration for MVP)
- [ ] Generate and return JWT token on successful login
- [ ] Attach token in frontend API requests via Authorization header
- [ ] Add FastAPI dependency to validate token on protected endpoints

---

## 🚀 Sprint 8: Final Integration & Deployment Prep

### Backend
- [ ] Run Qdrant as a local Docker container on standard port (6333)

### Frontend
- [ ] Create production build script for frontend to deploy to Vercel

---

This sprint plan structures the development roadmap into 8 focused phases, aligning with your MVP scope.

