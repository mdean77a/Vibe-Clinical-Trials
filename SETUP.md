# Development Environment Setup Guide

## Overview

This guide provides comprehensive setup instructions for the Clinical Trial Accelerator project. The application consists of a React frontend and FastAPI backend with Qdrant vector database integration.

## System Requirements

### Required Versions
- **Python**: 3.13+ (3.13.x recommended)
- **Node.js**: 22.x+ (22.x LTS recommended)
- **npm**: 9.x+ (comes with Node 22)

### Supported Platforms
- macOS (Intel/Apple Silicon)
- Linux (Ubuntu 20.04+, RHEL 8+)
- Windows 10/11 (with WSL2 recommended)

## Prerequisites Installation

### Python 3.13 Installation

#### macOS (Homebrew)
```bash
brew install python@3.13
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.13 python3.13-venv python3.13-dev
```

#### Windows
Download Python 3.13 from [python.org](https://www.python.org/downloads/) or use Windows Package Manager:
```powershell
winget install Python.Python.3.13
```

### Node.js 22+ Installation

#### Using Node Version Manager (Recommended)

**macOS/Linux:**
```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc

# Install and use Node 22
nvm install 22
nvm use 22
nvm alias default 22
```

**Windows:**
```powershell
# Install nvm-windows from: https://github.com/coreybutler/nvm-windows
nvm install 22.0.0
nvm use 22.0.0
```

#### Direct Installation
- Download from [nodejs.org](https://nodejs.org/)
- Use package managers: `brew install node@22`, `apt install nodejs npm`

## Environment Variables

### Required Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# API Keys (Required)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Qdrant Configuration (Required)
QDRANT_URL=your_qdrant_cloud_url_here
QDRANT_API_KEY=your_qdrant_api_key_here

# Backend Configuration
FASTAPI_HOST=localhost
FASTAPI_PORT=8000
ENVIRONMENT=development

# Frontend Configuration
VITE_API_BASE_URL=http://localhost:8000
```

### API Key Setup Instructions

#### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create new API key
3. Copy and paste into `.env` file

#### Anthropic API Key
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Create new API key
3. Copy and paste into `.env` file

#### Qdrant Cloud Setup (Required)
1. Visit [Qdrant Cloud](https://cloud.qdrant.io/)
2. Create free cluster
3. Copy cluster URL and API key
4. Add to `.env` file

**Note**: Qdrant cloud credentials are required for both development and production.

## Project Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd Vibe-Clinical-Trials
```

### 2. Backend Setup

#### Install uv (Python Package Manager)
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Alternative: pip install
pip install uv
```

#### Setup Backend Environment
```bash
cd backend

# Create virtual environment with Python 3.13
uv venv --python 3.13

# Activate virtual environment
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Install dependencies
uv pip install -e .
uv pip install -e ".[dev]"

# Verify installation
python --version  # Should show Python 3.13.x
uv pip list       # Should show all dependencies
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Verify installation
node --version    # Should show v22.x.x
npm --version     # Should show 9.x.x or higher
```

## Development Servers

### Start Backend Server
```bash
cd backend
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000
API documentation: http://localhost:8000/docs

### Start Frontend Server
```bash
cd frontend
npm run dev
```

Frontend will be available at: http://localhost:5173

## Development Workflow

### Code Quality Tools

#### Backend (Python)
```bash
cd backend

# Type checking
npm run type-check  # or: mypy app/

# Code formatting
black .

# Import sorting
isort .

# Linting
# Note: Add pylint/flake8 if needed

# Run tests
pytest
pytest --coverage
```

#### Frontend (TypeScript/React)
```bash
cd frontend

# Type checking
npm run type-check

# Linting
npm run lint

# Testing
npm run test           # Unit tests
npm run test:coverage  # With coverage
npm run test:e2e       # End-to-end tests
```

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes, commit
git add .
git commit -m "feat: implement feature description"

# Push and create PR
git push origin feature/your-feature-name
```

## Testing

### Backend Tests
```bash
cd backend
pytest                          # Run all tests
pytest tests/test_models.py     # Run specific test file
pytest --cov=app --cov-report=html  # Coverage report
```

### Frontend Tests
```bash
cd frontend
npm run test                    # Unit tests with Vitest
npm run test:ui                 # Interactive test runner
npm run test:coverage           # Coverage report
npm run test:e2e                # Playwright e2e tests
```

## Common Issues & Troubleshooting

### Python Version Issues
```bash
# Check Python version
python --version

# If wrong version, ensure correct activation
which python  # Should point to .venv/bin/python

# Recreate environment if needed
rm -rf .venv
uv venv --python 3.13
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### Node Version Issues
```bash
# Check Node version
node --version

# Switch to correct version (with nvm)
nvm use 22

# Clear npm cache if needed
npm cache clean --force
```

### API Key Issues
- Verify `.env` file exists in project root
- Check API keys are valid and have sufficient credits
- Ensure no spaces around `=` in `.env` file

### Port Conflicts
- Backend default: 8000 (change with `--port` flag)
- Frontend default: 5173 (Vite will auto-increment if busy)

### Dependency Issues
```bash
# Backend: Clear and reinstall
cd backend
rm -rf .venv
uv venv --python 3.13
source .venv/bin/activate
uv pip install -e ".[dev]"

# Frontend: Clear and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Production Deployment

### Environment Variables
- Set all required environment variables
- Use production Qdrant cluster URL
- Set `ENVIRONMENT=production`

### Backend Deployment
```bash
cd backend
uv pip install --no-dev -e .
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Deployment
```bash
cd frontend
npm run build
# Serve dist/ directory with nginx, Apache, or static hosting
```

## Additional Resources

- [Project Documentation](./docs/)
- [API Documentation](http://localhost:8000/docs) (when backend running)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)

## Getting Help

1. Check this setup guide for common solutions
2. Review project documentation in `docs/` directory
3. Check existing GitHub issues
4. Create new issue with:
   - Operating system and versions
   - Full error message
   - Steps to reproduce