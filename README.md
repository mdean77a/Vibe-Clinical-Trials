# Clinical Trial Accelerator

An internal web-based tool for automating the generation of clinical trial documents from protocol PDFs. Designed to streamline workflows for academic research organizations and reduce time-to-implementation.  Dummy change to trigger deployment.

---

## 🧩 Overview

This application uses AI to:
- Parse and embed clinical trial protocols
- Generate documents such as informed consent forms (ICFs) and site initiation checklists
- Enable users to regenerate, edit, and approve content in a structured interface

---

## 📁 Project Structure Summary

```
/clinical-trial-accelerator
├── docs/                              # Planning and architecture documents
│   ├── architecture/                  # System architecture diagrams
│   ├── prd/                          # Product requirements documentation
│   ├── architecture.md               # System design documentation
│   ├── prd.md                        # Product requirements document
│   └── deployment-checklist.md       # Production deployment guide
│
├── frontend/                          # React + Next.js + Tailwind frontend
│   ├── app/                          # Next.js app directory (pages & layouts)
│   │   ├── document-selection/        # Document selection pages
│   │   ├── informed-consent/          # ICF generation pages
│   │   ├── site-checklist/           # Site checklist pages
│   │   ├── lib/                      # Shared utilities
│   │   ├── globals.css               # Global styles
│   │   ├── layout.tsx                # Root layout component
│   │   └── page.tsx                  # Home page
│   ├── src/                          # Source code
│   │   ├── components/               # Reusable UI components
│   │   │   ├── __tests__/            # Component tests
│   │   │   ├── icf/                  # ICF-specific components
│   │   │   ├── Button.tsx            # Button component
│   │   │   ├── Card.tsx              # Card component
│   │   │   ├── Input.tsx             # Input component
│   │   │   ├── ProtocolSelector.tsx  # Protocol selection component
│   │   │   ├── ProtocolUpload.tsx    # File upload component
│   │   │   └── Textarea.tsx          # Textarea component
│   │   ├── types/                    # TypeScript type definitions
│   │   ├── utils/                    # Utility functions and API clients
│   │   └── test-utils.tsx            # Testing utilities
│   ├── public/                       # Static assets
│   ├── coverage/                     # Test coverage reports
│   ├── jest.config.js               # Jest testing configuration
│   ├── jest.setup.ts                # Jest setup file
│   ├── next.config.js               # Next.js configuration
│   ├── package.json                 # Dependencies and scripts
│   ├── tailwind.config.js           # Tailwind CSS configuration
│   └── tsconfig.json                # TypeScript configuration
│
├── backend/                          # FastAPI backend using uv and Qdrant
│   ├── app/                         # Main application code
│   │   ├── api/                     # API route handlers
│   │   ├── services/                # Business logic services
│   │   ├── main.py                  # FastAPI application entry point
│   │   ├── models.py                # Pydantic models and schemas
│   │   └── __init__.py              # Package initialization
│   ├── tests/                       # Backend test suite
│   │   ├── test_api_protocols.py    # API endpoint tests
│   │   ├── test_document_generator.py # Document generation tests
│   │   ├── test_icf_service.py      # ICF service tests
│   │   ├── test_models.py           # Model validation tests
│   │   ├── test_qdrant_protocols.py # Qdrant integration tests
│   │   ├── test_qdrant_service.py   # Qdrant service tests
│   │   ├── conftest.py              # Pytest configuration
│   │   └── conftest_qdrant.py       # Qdrant test configuration
│   ├── htmlcov/                     # Coverage HTML reports
│   ├── .env.example                 # Environment variables template
│   ├── pyproject.toml               # Python project configuration
│   ├── uv.lock                      # Dependency lock file
│   └── README.md                    # Backend-specific documentation
│
├── scripts/                          # Development and deployment scripts
├── .env.example                      # Environment variables template
├── .gitignore                        # Git ignore rules
├── package.json                      # Root project configuration
├── README.md                         # This file
├── SETUP.md                          # Detailed setup instructions
└── TESTING.md                        # Testing documentation
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

- **Frontend:** React, Next.js, Tailwind CSS, TypeScript
- **Backend:** FastAPI, uv, PyMuPDF, LangChain, LangGraph
- **Storage:** Qdrant vector DB + local disk
- **Auth:** Lightweight token system (MVP)
- **Testing:** Jest (Frontend), Pytest (Backend)

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.13+**
- **Node.js 22+**
- **API Keys:** OpenAI, Anthropic, Qdrant Cloud

### Initial Setup
1. **Clone and Setup Environment**
   ```bash
   git clone <repository-url>
   cd Vibe-Clinical-Trials
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Backend Setup**
   ```bash
   cd backend
   uv venv --python 3.13
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e ".[dev]"
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

For detailed setup instructions, see [SETUP.md](./SETUP.md).

---

## 🔧 Running the Application

### Development Mode

#### Start Backend (Terminal 1)
```bash
cd backend
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- **Backend URL:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Hot reload:** Enabled for development

#### Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```
- **Frontend URL:** http://localhost:3000
- **Hot reload:** Enabled for development

### Production Mode

#### Backend Production
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Frontend Production
```bash
cd frontend
npm run build
npm start
```
- Builds optimized production bundle
- Starts production server on http://localhost:3000

### Alternative Scripts

#### Frontend Scripts
```bash
npm run dev          # Development server
npm run build        # Production build
npm start            # Production server
npm run lint         # ESLint checking
npm run type-check   # TypeScript checking
```

#### Backend Scripts
```bash
# Development
uvicorn app.main:app --reload

# Production
uvicorn app.main:app --workers 4

# With custom host/port
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

---

## 🧪 Testing

### Frontend Testing

#### Run All Tests
```bash
cd frontend
npm test
```

#### Test Options
```bash
npm run test          # Run all tests once
npm run test:watch    # Run tests in watch mode
npm run test:coverage # Run tests with coverage report
npm run test:e2e      # Run end-to-end tests with Playwright
```

#### Coverage Report
```bash
npm run test:coverage
# Opens HTML coverage report at: frontend/coverage/index.html
```

#### Component-Specific Tests
```bash
# Run specific test file
npm test -- ProtocolUpload.test.tsx

# Run tests matching pattern
npm test -- --testNamePattern="drag and drop"

# Run tests in specific directory
npm test -- src/components/__tests__/
```

### Backend Testing

#### Run All Tests
```bash
cd backend
source .venv/bin/activate
pytest
```

#### Test Options
```bash
pytest                          # Run all tests
pytest -v                       # Verbose output
pytest --cov=app                # With coverage
pytest --cov=app --cov-report=html  # HTML coverage report
pytest tests/test_specific.py   # Run specific test file
pytest -k "test_upload"         # Run tests matching pattern
```

#### Coverage Report
```bash
pytest --cov=app --cov-report=html
# Opens HTML coverage report at: backend/htmlcov/index.html
```

#### Test Categories
```bash
pytest tests/unit/              # Unit tests only
pytest tests/integration/       # Integration tests only
pytest tests/api/               # API endpoint tests
pytest -m "not slow"           # Skip slow tests
```

### Running Tests for Both

#### Quick Test Suite (Fast)
```bash
# Terminal 1 - Frontend
cd frontend && npm test -- --passWithNoTests

# Terminal 2 - Backend  
cd backend && source .venv/bin/activate && pytest -x
```

#### Full Test Suite with Coverage
```bash
# Terminal 1 - Frontend with coverage
cd frontend && npm run test:coverage

# Terminal 2 - Backend with coverage
cd backend && source .venv/bin/activate && pytest --cov=app --cov-report=html
```

---

## 📊 Test Coverage

### Current Test Coverage
- **Frontend Components:** Comprehensive test suite with 40+ tests for ProtocolUpload
- **Backend APIs:** Full endpoint testing with pytest
- **Integration:** End-to-end testing with Playwright

### Viewing Coverage Reports
- **Frontend:** `frontend/coverage/index.html`
- **Backend:** `backend/htmlcov/index.html`

---

## 🐛 Debugging & Troubleshooting

### Common Issues

#### Backend Issues
```bash
# Port already in use
lsof -ti:8000 | xargs kill -9

# Python version issues
python --version  # Should be 3.13+
uv python list    # Check available Python versions

# Dependency issues
uv pip install -e ".[dev]" --force-reinstall
```

#### Frontend Issues
```bash
# Node version issues
node --version    # Should be 22+
nvm use 22       # Switch to Node 22

# Dependency issues
rm -rf node_modules package-lock.json
npm install

# Port already in use
npx kill-port 3000
```

#### Test Issues
```bash
# Clear test cache
npm test -- --clearCache  # Frontend
pytest --cache-clear      # Backend

# Update snapshots
npm test -- --updateSnapshot
```

### Development Tools
- **Backend API:** http://localhost:8000/docs (Swagger UI)
- **Frontend Dev Tools:** React Developer Tools
- **Database:** Qdrant Cloud Dashboard
- **Logs:** Check terminal output for both services

---

## 📚 Additional Resources

### Development Guides
- **Setup:** [SETUP.md](./SETUP.md) - Comprehensive installation guide
- **Testing:** [TESTING.md](./TESTING.md) - Detailed testing strategies
- **Planning:** `docs/` folder - Full project documentation

### Documentation
- ✅ Product Requirements Document (PRD)
- ✅ System Architecture
- ✅ Document Editor UI Design  
- ✅ Sprint-structured Development Task List

To enable docs in Cursor AI:
1. Open a document (e.g., `docs/product_requirements_document.md`)
2. Right-click → **Use in Context**

---

## 💡 Development Tips

### Recommended Workflow
1. **Start services:** Backend first, then frontend
2. **Run tests:** Use watch mode during development
3. **Check coverage:** Regularly review test coverage reports
4. **API testing:** Use Swagger UI at http://localhost:8000/docs
5. **Debugging:** Check browser console and terminal logs

### Performance Monitoring
- **Frontend:** Use React DevTools Profiler
- **Backend:** Monitor FastAPI logs and response times
- **Database:** Monitor Qdrant cluster performance

---

For development questions, review the Sprint Roadmap in `docs/development_task_list.md`.
