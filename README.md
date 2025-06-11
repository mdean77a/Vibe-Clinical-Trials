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
- On-prem MVP with future deployment to Vercel

---

## 🧠 Tech Stack

- **Frontend:** React, Vite, Tailwind CSS, shadcn/ui
- **Backend:** FastAPI, uv, PyMuPDF, LangChain, LangGraph
- **Storage:** Qdrant vector DB + local disk
- **Auth:** Lightweight token system (MVP)

---

## 🛠 Getting Started

Coming soon with full install and run instructions.

---

For any development questions, review the Sprint Roadmap in `docs/development_task_list.md`.
