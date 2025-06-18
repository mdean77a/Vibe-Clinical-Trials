#!/bin/bash

# Git Hooks Setup Script for Single Developer Workflow
# This creates pre-push hooks that run tests before pushing to prevent broken code

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🪝 Setting up Git hooks for local quality gates${NC}"
echo ""

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Not in a git repository. Please run this from the project root.${NC}"
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p .git/hooks

# Create pre-push hook
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash

# Pre-push hook for Clinical Trial Accelerator
# Runs tests and quality checks before allowing push

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 Running pre-push quality checks...${NC}"
echo ""

# Track if any checks fail
FAILED=0

# Function to run command and track failures
run_check() {
    local name="$1"
    local cmd="$2"
    local dir="$3"
    
    echo -e "${BLUE}🔍 $name${NC}"
    
    if [ -n "$dir" ]; then
        cd "$dir"
    fi
    
    if eval "$cmd"; then
        echo -e "${GREEN}✅ $name passed${NC}"
    else
        echo -e "${RED}❌ $name failed${NC}"
        FAILED=1
    fi
    
    if [ -n "$dir" ]; then
        cd - > /dev/null
    fi
    
    echo ""
}

# Run backend checks
if [ -d "backend" ]; then
    echo -e "${YELLOW}🐍 Backend Checks${NC}"
    echo "................................."
    
    run_check "Backend linting (black)" "uv run black --check ." "backend"
    run_check "Backend import sorting (isort)" "uv run isort --check-only ." "backend"
    run_check "Backend type checking (mypy)" "uv run mypy app/" "backend"
    run_check "Backend tests with coverage" "uv run python -m pytest --cov=app --cov-fail-under=80 -q" "backend"
fi

# Run frontend checks  
if [ -d "frontend" ]; then
    echo -e "${YELLOW}🌐 Frontend Checks${NC}"
    echo "................................."
    
    run_check "Frontend linting (eslint)" "npm run lint" "frontend"
    run_check "Frontend type checking (tsc)" "npm run type-check" "frontend" 
    run_check "Frontend tests with coverage" "npm run test:coverage -- --run" "frontend"
    run_check "Frontend build" "npm run build" "frontend"
fi

# Check results
if [ $FAILED -eq 1 ]; then
    echo -e "${RED}💥 Pre-push checks failed!${NC}"
    echo -e "${YELLOW}Please fix the issues above before pushing.${NC}"
    echo ""
    echo -e "${BLUE}💡 Quick fixes:${NC}"
    echo "  Backend formatting: cd backend && uv run black . && uv run isort ."
    echo "  Frontend linting:   cd frontend && npm run lint -- --fix"
    echo "  Run tests:          See specific error messages above"
    echo ""
    echo -e "${YELLOW}To skip these checks (not recommended):${NC}"
    echo "  git push --no-verify"
    exit 1
fi

echo -e "${GREEN}🎉 All pre-push checks passed!${NC}"
echo -e "${BLUE}🚀 Proceeding with push...${NC}"
echo ""
EOF

# Make the hook executable
chmod +x .git/hooks/pre-push

# Create a commit-msg hook for better commit messages
cat > .git/hooks/commit-msg << 'EOF'
#!/bin/bash

# Commit message hook to enforce conventional commit format

commit_regex='^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .{1,50}'

error_msg="Invalid commit message format!

Expected format: <type>[optional scope]: <description>

Types:
  feat:     A new feature
  fix:      A bug fix  
  docs:     Documentation changes
  style:    Code style changes (formatting, etc)
  refactor: Code refactoring
  test:     Adding or updating tests
  chore:    Build process or auxiliary tool changes

Examples:
  feat: add protocol validation
  fix(upload): handle large file uploads
  docs: update API documentation
  test: add integration tests for ICF generation"

if ! grep -qE "$commit_regex" "$1"; then
    echo "$error_msg" >&2
    exit 1
fi
EOF

chmod +x .git/hooks/commit-msg

echo -e "${GREEN}✅ Git hooks installed successfully!${NC}"
echo ""
echo -e "${BLUE}📋 What happens now:${NC}"
echo ""
echo -e "${YELLOW}Before every push:${NC}"
echo "  🔍 Backend linting, type checking, and tests"
echo "  🔍 Frontend linting, type checking, tests, and build"
echo "  🔍 Coverage verification (≥80%)"
echo "  ✅ Push only allowed if all checks pass"
echo ""
echo -e "${YELLOW}Before every commit:${NC}"
echo "  📝 Commit message format validation"
echo "  📝 Enforces conventional commit format"
echo ""
echo -e "${BLUE}💡 Benefits:${NC}"
echo "  ✅ Catch issues before they reach GitHub"
echo "  ✅ Maintain consistent code quality"
echo "  ✅ Prevent broken code on main branch"
echo "  ✅ Faster feedback loop"
echo ""
echo -e "${YELLOW}⚠️  To skip hooks (emergency only):${NC}"
echo "  git push --no-verify"
echo "  git commit --no-verify -m \"emergency fix\""
echo ""
echo -e "${GREEN}🎯 Your local environment now has the same quality gates as CI/CD!${NC}"
EOF

# Make the setup script executable
chmod +x scripts/setup-git-hooks.sh

echo -e "${GREEN}✅ Git hooks setup script created!${NC}"
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo "1. Run: ./scripts/setup-git-hooks.sh"
echo "2. Test with a small commit and push"
echo "3. Enjoy automatic quality checking!"