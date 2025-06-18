# 🧪 Local Testing Guide

Quick reference for running tests and quality checks locally before pushing to GitHub.

## 🚀 **Quick Commands**

```bash
# Test everything (recommended before pushing)
npm test

# Quick test run (just run tests, skip linting)
npm run test:quick

# Test just backend or frontend
npm run test:backend
npm run test:frontend

# Check test coverage
npm run test:coverage

# Run linting checks
npm run lint

# Auto-fix linting issues
npm run lint:fix

# Auto-fix all fixable issues
npm run fix
```

## 🎯 **Recommended Workflow**

### **Before Pushing (Full Check)**
```bash
# Run this before git push to catch issues early
npm test
```

### **During Development (Quick Check)**
```bash
# Run this frequently while coding
npm run test:quick
```

### **Before Committing (Linting)**
```bash
# Clean up code formatting
npm run fix
```

## 📋 **What Each Command Does**

### **`npm test` (Full Quality Check)**
```bash
✅ Backend linting (black, isort)
✅ Backend type checking (mypy)
✅ Backend tests + coverage (119 tests, ≥80%)
✅ Frontend linting (eslint)
✅ Frontend type checking (tsc)
✅ Frontend tests + coverage (258 tests, ≥80%)
✅ Frontend build verification

⏱️  Duration: ~2-5 minutes
🎯 Use: Before pushing to GitHub
```

### **`npm run test:quick` (Fast Development Check)**
```bash
✅ Backend tests (no coverage calculation)
✅ Frontend tests (no coverage calculation)
❌ Skips linting, type checking, build

⏱️  Duration: ~30 seconds
🎯 Use: During active development
```

### **`npm run lint:fix` (Code Cleanup)**
```bash
✅ Auto-fix backend formatting (black, isort)
✅ Auto-fix frontend linting (eslint --fix)

⏱️  Duration: ~5 seconds
🎯 Use: Before committing
```

## 🔧 **Advanced Usage**

### **Parallel Execution (Faster)**
```bash
# Run backend and frontend checks simultaneously
./scripts/test-local.sh --parallel

# With npm script
npm run test:parallel
```

### **Specific Check Types**
```bash
./scripts/test-local.sh lint      # Only linting
./scripts/test-local.sh types     # Only type checking
./scripts/test-local.sh tests     # Only tests
./scripts/test-local.sh coverage  # Only coverage
./scripts/test-local.sh build     # Only build
```

### **Component-Specific**
```bash
./scripts/test-local.sh backend   # Backend only
./scripts/test-local.sh frontend  # Frontend only
```

### **Help and Options**
```bash
./scripts/test-local.sh --help    # Show all options
./scripts/test-local.sh --fix     # Auto-fix issues
./scripts/test-local.sh -v        # Verbose output
./scripts/test-local.sh -p        # Parallel execution
```

## 💡 **Development Tips**

### **Daily Workflow**
```bash
# Start development
npm run dev:backend    # Terminal 1
npm run dev:frontend   # Terminal 2

# While coding (run frequently)
npm run test:quick

# Before committing
npm run fix
git add . && git commit -m "feat: new feature"

# Before pushing
npm test
git push origin main
```

### **Fixing Common Issues**

**Backend Formatting:**
```bash
cd backend
uv run black .
uv run isort .
```

**Frontend Linting:**
```bash
cd frontend
npm run lint -- --fix
```

**Type Errors:**
```bash
# Backend
cd backend && uv run mypy app/

# Frontend  
cd frontend && npm run type-check
```

**Test Failures:**
```bash
# Run specific test file
cd backend && uv run pytest tests/test_specific.py -v
cd frontend && npm test -- src/components/SpecificComponent.test.tsx
```

## 🔍 **Understanding Output**

### **Success Example**
```bash
$ npm test

🐍 BACKEND CHECKS
════════════════════════════════════════
✅ Backend Code Formatting (black) passed (1s)
✅ Backend Import Sorting (isort) passed (1s)
✅ Backend Type Checking (mypy) passed (3s)
✅ Backend Tests (pytest) passed (15s)
✅ Backend Coverage (pytest-cov) passed (18s)

🌐 FRONTEND CHECKS
════════════════════════════════════════
✅ Frontend Linting (eslint) passed (2s)
✅ Frontend Type Checking (tsc) passed (4s)
✅ Frontend Tests (vitest) passed (8s)
✅ Frontend Coverage (vitest) passed (12s)
✅ Frontend Build (vite) passed (6s)

📊 SUMMARY
════════════════════════════════════════
🎉 All checks passed! (70s)
✅ Ready to push to GitHub

💡 To push:
  git add . && git commit -m "your message" && git push origin main
```

### **Failure Example**
```bash
$ npm test

❌ Backend Tests (pytest) failed (15s)
❌ Frontend Type Checking (tsc) failed (4s)

💥 Some checks failed! (45s)
🔧 Try running with --fix to auto-fix some issues:
  ./scripts/test-local.sh --fix

💡 Or fix manually and run again:
  npm test
```

## ⚡ **Performance Tips**

### **Speed Up Tests**
```bash
# Skip coverage calculation during development
npm run test:quick

# Run only changed files (if your tests support it)
cd backend && uv run pytest --lf  # Last failed
cd frontend && npm test -- --changed

# Use parallel execution
npm run test:parallel
```

### **VS Code Integration**
Add to your VS Code settings:
```json
{
  "npm.packageManager": "npm",
  "terminal.integrated.defaultProfile.osx": "bash",
  "tasks.version": "2.0.0",
  "tasks.tasks": [
    {
      "label": "Test All",
      "type": "shell", 
      "command": "npm test",
      "group": "test"
    },
    {
      "label": "Test Quick",
      "type": "shell",
      "command": "npm run test:quick", 
      "group": "test"
    }
  ]
}
```

## 🎯 **When to Run What**

| Scenario | Command | Duration | Purpose |
|----------|---------|----------|---------|
| **Active coding** | `npm run test:quick` | ~30s | Fast feedback |
| **Before commit** | `npm run fix` | ~5s | Clean up code |
| **Before push** | `npm test` | ~2-5min | Full validation |
| **CI/CD failed** | `npm test` | ~2-5min | Reproduce CI issues |
| **Code review** | `npm run test:coverage` | ~1-2min | Check coverage |

---

**💡 The goal is to catch issues locally before they reach GitHub, making development faster and more reliable!**