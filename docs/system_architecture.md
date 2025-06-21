# System Architecture: Clinical Trial Accelerator

## Frontend
- Framework: React + Vite
- Styling: Tailwind CSS
- UI Library: shadcn/ui
- Editor UI: Rich text + regeneration prompts + status icons
- Protocol Viewer: Embedded, searchable
- Authentication: Lightweight email/password

## Backend
- Framework: FastAPI
- Dependency Management: uv
- Document Parsing: PyMuPDF
- RAG Engine: LangChain + LangGraph
- Storage: Unified Qdrant storage (metadata + vectors, no file persistence)
- Embedding Model: OpenAI

## Data Flow
1. Upload PDF (no persistence needed)
2. Extract & chunk via PyMuPDF
3. Unified operation: embed + store metadata in Qdrant
4. Section prompts call LangGraph
5. User refines output → final export

## Deployment
- MVP: Local development with cloud Qdrant
- Target: Local deployment with FastAPI backend and React frontend

