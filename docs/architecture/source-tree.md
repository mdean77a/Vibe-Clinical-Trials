# Vibe Clinical Trials Source Tree

This document defines the project structure for the Clinical Trial Accelerator. The project uses a simple two-part architecture with a React frontend and Python FastAPI backend.

## Project Structure

```plaintext
vibe-clinical-trials/
├── .github/                        # GitHub configuration
│   ├── workflows/                  # CI/CD workflows
│   │   └── ci.yml                 # Continuous integration
│   └── dependabot.yml             # Dependency updates
├── .vscode/                       # VSCode workspace settings
│   ├── settings.json              # Editor configuration
│   └── extensions.json            # Recommended extensions
├── frontend/                      # React frontend application
│   ├── public/                    # Static assets
│   │   ├── index.html            # HTML template
│   │   └── favicon.ico           # App icon
│   ├── src/                      # Source code
│   │   ├── components/           # React components
│   │   │   ├── Button.tsx        # Reusable UI components
│   │   │   ├── Card.tsx
│   │   │   └── icf/              # ICF-specific components
│   │   ├── pages/                # Page components
│   │   │   ├── HomePage.tsx      # Protocol selection page
│   │   │   ├── DocumentSelection.tsx
│   │   │   ├── ICFGeneration.tsx
│   │   │   └── SiteChecklist.tsx
│   │   ├── utils/                # Utility functions
│   │   │   ├── api.ts           # Centralized API module
│   │   │   └── helpers.ts       # Helper functions
│   │   ├── hooks/               # Custom React hooks
│   │   ├── types/               # TypeScript type definitions
│   │   │   └── index.ts         # Shared types
│   │   ├── styles/              # Global styles
│   │   │   └── globals.css      # Tailwind imports
│   │   ├── test/                # Test utilities
│   │   │   └── setup.ts         # Test configuration
│   │   ├── App.tsx              # Main app component
│   │   ├── main.tsx             # Entry point
│   │   └── vite-env.d.ts        # Vite types
│   ├── __tests__/               # Test files
│   │   ├── components/          # Component tests
│   │   └── utils/               # Utility tests
│   ├── .env.example             # Environment template
│   ├── .eslintrc.json           # ESLint configuration
│   ├── .prettierrc              # Prettier configuration
│   ├── index.html               # Vite entry HTML
│   ├── package.json             # Frontend dependencies
│   ├── tailwind.config.js       # Tailwind configuration
│   ├── tsconfig.json            # TypeScript configuration
│   ├── vite.config.ts           # Vite configuration
│   └── vitest.config.ts         # Vitest configuration
├── backend/                     # Python FastAPI backend
│   ├── app/                     # Application code
│   │   ├── api/                 # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── protocols.py     # Protocol management endpoints
│   │   │   ├── icf.py          # ICF generation endpoints
│   │   │   ├── site_checklist.py # Site checklist endpoints
│   │   │   └── health.py        # Health check endpoints
│   │   ├── core/                # Core functionality
│   │   │   ├── __init__.py
│   │   │   ├── config.py        # Configuration management
│   │   │   ├── qdrant.py        # Qdrant client and operations
│   │   │   └── pdf_processor.py # PyMuPDF processing
│   │   ├── services/            # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── rag_pipeline.py  # RAG implementation
│   │   │   ├── embeddings.py    # OpenAI embeddings
│   │   │   └── document_generator.py # Document generation
│   │   ├── workflows/           # LangGraph workflows
│   │   │   ├── __init__.py
│   │   │   ├── icf_workflow.py  # ICF generation workflow
│   │   │   └── checklist_workflow.py # Site checklist workflow
│   │   ├── models/              # Pydantic models
│   │   │   ├── __init__.py
│   │   │   ├── protocol.py      # Protocol data models
│   │   │   └── document.py      # Document models
│   │   ├── prompts/             # AI prompts
│   │   │   ├── __init__.py
│   │   │   ├── icf_prompts.py   # ICF section prompts
│   │   │   └── checklist_prompts.py # Checklist prompts
│   │   └── main.py              # FastAPI app initialization
│   ├── tests/                   # Backend tests
│   │   ├── __init__.py
│   │   ├── test_api/            # API endpoint tests
│   │   ├── test_services/       # Service tests
│   │   └── conftest.py          # pytest configuration
│   ├── .env.example             # Environment template
│   ├── .gitignore               # Python gitignore
│   ├── requirements.txt         # Python dependencies
│   ├── requirements-dev.txt     # Development dependencies
│   └── pytest.ini               # pytest configuration
├── docs/                        # Project documentation
│   ├── architecture/            # Architecture documents
│   │   ├── coding-standards.md
│   │   ├── tech-stack.md
│   │   └── source-tree.md
│   ├── prd.md                   # Product requirements
│   └── deployment-checklist.md  # Deployment guide
├── scripts/                     # Utility scripts
│   ├── setup.sh                 # Initial setup script
│   └── start-dev.sh            # Start development servers
├── .bmad-core/                  # BMAD framework files
│   ├── checklists/
│   ├── tasks/
│   ├── templates/
│   └── utils/
├── .gitignore                   # Root gitignore
├── README.md                    # Project documentation
└── docker-compose.yml           # Docker configuration (future)
```

## Key Directories Explained

### `/frontend`
React application with TypeScript:
- **src/components**: Reusable React components
- **src/pages**: Page-level components for routing
- **src/utils/api.ts**: Centralized API module with namespaced endpoints
- **src/types**: TypeScript type definitions
- **__tests__**: Test files in dedicated folders

### `/backend`
Python FastAPI application:
- **app/api**: REST API endpoints
- **app/core**: Core functionality (config, Qdrant, PDF processing)
- **app/services**: Business logic (RAG, embeddings, generation)
- **app/workflows**: LangGraph workflows for document generation
- **app/models**: Pydantic data models
- **app/prompts**: AI prompt templates

### `/docs`
Project documentation:
- Architecture documents
- Product requirements document (PRD)
- Deployment guides

## File Naming Conventions

### Frontend (TypeScript/React)
- **Components**: `PascalCase.tsx` (e.g., `Button.tsx`, `ICFGenerationDashboard.tsx`)
- **Pages**: `PascalCase.tsx` (e.g., `HomePage.tsx`)
- **Utilities**: `camelCase.ts` (e.g., `api.ts`, `helpers.ts`)
- **Tests**: `ComponentName.test.tsx` in `__tests__` folders
- **Types**: `camelCase.ts` or `index.ts` for exports

### Backend (Python)
- **Python files**: `snake_case.py` (e.g., `rag_pipeline.py`)
- **API endpoints**: `snake_case.py` matching resource names
- **Classes**: `PascalCase` in Python code
- **Functions**: `snake_case` in Python code

## Import Organization

### Frontend (@/ alias configured in tsconfig.json)
```typescript
// React
import React from 'react';

// External
import { useNavigate } from 'react-router-dom';

// Internal with @ alias
import { protocolsApi } from '@/utils/api';
import Button from '@/components/Button';

// Types
import type { Protocol } from '@/types';
```

### Backend (Python)
```python
# Standard library
import os
from typing import List, Optional

# External packages
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Internal imports
from app.core.qdrant import QdrantClient
from app.services.rag_pipeline import RAGPipeline
from app.models.protocol import Protocol
```

## API Structure

### Frontend API Module (`src/utils/api.ts`)
- Centralized API configuration
- Namespaced API calls (protocolsApi, icfApi, healthApi)
- Error handling with localStorage fallback
- Type-safe request/response handling

### Backend API Routes
- `/api/protocols` - Protocol management
- `/api/icf` - ICF generation
- `/api/site-checklist` - Site checklist generation
- `/api/health` - Health checks

## Environment Files

### Frontend (.env.local)
```
REACT_APP_API_URL=http://localhost:8000
```

### Backend (.env)
```
ANTHROPIC_API_KEY=your_key
OPENAI_API_KEY=your_key
QDRANT_URL=memory://
```

## Development Scripts

### Start Development
```bash
# Frontend (from /frontend)
npm install
npm run dev

# Backend (from /backend)
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### Run Tests
```bash
# Frontend
npm test

# Backend
pytest
```

## Build Outputs (git-ignored)

- `frontend/dist/` - Vite build output
- `frontend/node_modules/` - Node dependencies
- `backend/__pycache__/` - Python bytecode
- `backend/.pytest_cache/` - pytest cache
- `.env.local`, `.env` - Environment files

## Notes

- No monorepo tooling needed for this simple structure
- Frontend and backend are separate but co-located
- Qdrant handles all data storage (no traditional database)
- All paths support future containerization
- Structure optimized for local MVP development