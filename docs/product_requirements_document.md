# Product Requirements Document (PRD)
## Project: Clinical Trial Accelerator

### Overview
An internal web application to accelerate implementation of clinical trials by generating bespoke trial documents from protocol PDFs using AI-assisted workflows.

### Goals
- Drastically reduce document preparation time for trial startup.
- Streamline investigator workflows via bespoke, section-based document generation.
- Human-in-the-loop refinement for document accuracy.

### MVP Scope
- Upload PDF protocol
- Generate two types of documents: Informed Consent Form (ICF) and Site Initiation Checklist
- Use PyMuPDF, Qdrant, OpenAI, LangChain, LangGraph
- Review/edit/approve workflow
- Minimal auth for MVP; on-prem deployment initially

---

## Features

### Core
- Upload protocol (PDF only)
- Parse, embed, and index via RAG pipeline
- Regenerate content per section
- Approve and export documents
- Track protocol versioning (via external DCC tools)

### Future
- Upload NIH grant → generate protocol
- REDCap schema support
- SSO integration
- Additional document types

---

## Metrics
- Time from protocol upload to first draft generation
- Number of sections edited vs. regenerated
- User satisfaction during testing
