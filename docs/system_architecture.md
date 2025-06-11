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
- Storage: PDF and chunked text to disk; vectors in Qdrant
- Embedding Model: OpenAI

## Data Flow
1. Upload PDF
2. Extract & chunk via PyMuPDF
3. Embed + store in Qdrant
4. Section prompts call LangGraph
5. User refines output → final export

## Deployment
- MVP: On-prem backend + Dockerized Qdrant
- Target: Vercel frontend, backend redeployable to cloud

