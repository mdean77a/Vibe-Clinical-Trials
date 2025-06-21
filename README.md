# Clinical Trial Accelerator

An internal web-based tool for automating the generation of clinical trial documents from protocol PDFs. Designed to streamline workflows for academic research organizations and reduce time-to-implementation.

---

## 🧩 Overview

This application uses AI to:
- Parse and embed clinical trial protocols
- Generate documents such as informed consent forms (ICFs) and site initiation checklists
- Enable users to regenerate, edit, and approve content in a structured interface

---

## 📁 Project Structure

```
/clinical-trial-accelerator
├── docs/                    # Planning and architecture documents
│   ├── product_requirements_document.md
│   ├── system_architecture.md
│   ├── editor_ui_design.md
│   └── development_task_list.md
├── frontend/                # React + Vite + Tailwind frontend
├── backend/                 # FastAPI backend using uv and Qdrant
└── README.md
```

---

## 📚 Planning & Context

This project is built using the BMAD methodology and has full planning documents available in the `docs/` folder. To enable them in Cursor AI:

1. Open a document (e.g., `docs/product_requirements_document.md`)
2. Right-click → **Use in Context**

These documents include:
- ✅ Product Requirements Document (PRD)
- ✅ System Architecture
- ✅ Document Editor UI Design
- ✅ Sprint-structured Development Task List

---

## 🚀 MVP Goals

- Upload PDF protocol
- Generate ICF and site initiation checklist
- Support manual edits, approval flow
- Backend powered by FastAPI + Qdrant + LangGraph
- Local deployment MVP

---

## 🧠 Tech Stack

- **Frontend:** React, Vite, Tailwind CSS, shadcn/ui
- **Backend:** FastAPI, uv, PyMuPDF, LangChain, LangGraph
- **Storage:** Qdrant vector DB + local disk
- **Auth:** Lightweight token system (MVP)

---

## 🛠 Getting Started

### Quick Start
1. **Prerequisites**: Python 3.13+, Node.js 22+
2. **Setup**: See [SETUP.md](./SETUP.md) for comprehensive installation guide
3. **Environment**: Copy `.env.example` to `.env` and add your API keys
4. **Backend**: `cd backend && uv venv --python 3.13 && source .venv/bin/activate && uv pip install -e ".[dev]"`
5. **Frontend**: `cd frontend && npm install`
6. **Run**: Start backend (`uvicorn app.main:app --reload`) and frontend (`npm run dev`)

For detailed setup instructions, troubleshooting, and deployment guides, see [SETUP.md](./SETUP.md).

---

For any development questions, review the Sprint Roadmap in `docs/development_task_list.md`.
