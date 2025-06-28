#!/bin/bash

# Local Testing Script for Clinical Trial Accelerator
# Run this manually whenever you want to check code quality before pushing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
BACKEND_DIR="backend"
FRONTEND_DIR="frontend"
PARALLEL=${PARALLEL:-false}

# Function to print section headers
print_header() {
    echo ""
    echo -e "${PURPLE}════════════════════════════════════════${NC}"
    echo -e "${PURPLE} $1${NC}"
    echo -e "${PURPLE}════════════════════════════════════════${NC}"
    echo ""
}

# Function to run command with status
run_check() {
    local name="$1"
    local cmd="$2"
    local dir="$3"
    local optional="$4"
    
    echo -e "${BLUE}🔍 $name${NC}"
    echo -e "${CYAN}Command: $cmd${NC}"
    
    if [ -n "$dir" ] && [ -d "$dir" ]; then
        cd "$dir"
    elif [ -n "$dir" ]; then
        if [ "$optional" = "true" ]; then
            echo -e "${YELLOW}⚠️  Directory $dir not found, skipping...${NC}"
            return 0
        else
            echo -e "${RED}❌ Directory $dir not found${NC}"
            return 1
        fi
    fi
    
    local start_time=$(date +%s)
    
    if eval "$cmd"; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        echo -e "${GREEN}✅ $name passed (${duration}s)${NC}"
        local result=0
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        echo -e "${RED}❌ $name failed (${duration}s)${NC}"
        local result=1
    fi
    
    if [ -n "$dir" ]; then
        cd - > /dev/null
    fi
    
    echo ""
    return $result
}

# Function to show usage
show_usage() {
    echo -e "${BLUE}🧪 Local Testing Script${NC}"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo "  $0 [options] [component]"
    echo ""
    echo -e "${YELLOW}Components:${NC}"
    echo "  all        Run all checks (default)"
    echo "  backend    Run only backend checks"
    echo "  frontend   Run only frontend checks"
    echo "  quick      Run only tests (skip linting/formatting)"
    echo "  lint       Run only linting and formatting"
    echo "  types      Run only type checking"
    echo "  tests      Run only tests"
    echo "  coverage   Run tests with coverage"
    echo "  build      Run build checks"
    echo ""
    echo -e "${YELLOW}Options:${NC}"
    echo "  -h, --help     Show this help"
    echo "  -p, --parallel Run backend and frontend checks in parallel"
    echo "  -v, --verbose  Show verbose output"
    echo "  -q, --quiet    Show minimal output"
    echo "  --fix          Auto-fix issues where possible"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0                    # Run all checks"
    echo "  $0 backend            # Backend only"
    echo "  $0 quick              # Just run tests"
    echo "  $0 --fix lint         # Run linting with auto-fix"
    echo "  $0 -p coverage        # Run coverage in parallel"
}

# Function to run backend checks
run_backend_checks() {
    local check_type="$1"
    
    if [ ! -d "$BACKEND_DIR" ]; then
        echo -e "${YELLOW}⚠️  Backend directory not found, skipping...${NC}"
        return 0
    fi
    
    print_header "🐍 BACKEND CHECKS"
    
    local failed=0
    
    case $check_type in
        "lint"|"all")
            run_check "Backend Code Formatting (black)" "uv run black --check ." "$BACKEND_DIR" || failed=1
            run_check "Backend Import Sorting (isort)" "uv run isort --check-only ." "$BACKEND_DIR" || failed=1
            ;;
    esac
    
    case $check_type in
        "types"|"all")
            run_check "Backend Type Checking (mypy)" "uv run mypy app/" "$BACKEND_DIR" || failed=1
            ;;
    esac
    
    case $check_type in
        "tests"|"quick"|"all")
            run_check "Backend Tests (pytest)" "uv run python -m pytest -v" "$BACKEND_DIR" || failed=1
            ;;
    esac
    
    case $check_type in
        "coverage"|"all")
            run_check "Backend Coverage (pytest-cov)" "uv run python -m pytest --cov=app --cov-report=term-missing --cov-fail-under=80" "$BACKEND_DIR" || failed=1
            ;;
    esac
    
    return $failed
}

# Function to run frontend checks
run_frontend_checks() {
    local check_type="$1"
    
    if [ ! -d "$FRONTEND_DIR" ]; then
        echo -e "${YELLOW}⚠️  Frontend directory not found, skipping...${NC}"
        return 0
    fi
    
    print_header "🌐 FRONTEND CHECKS"
    
    local failed=0
    
    case $check_type in
        "lint"|"all")
            run_check "Frontend Linting (eslint)" "npm run lint" "$FRONTEND_DIR" || failed=1
            ;;
    esac
    
    case $check_type in
        "types"|"all")
            run_check "Frontend Type Checking (tsc)" "npm run type-check" "$FRONTEND_DIR" || failed=1
            ;;
    esac
    
    case $check_type in
        "tests"|"quick"|"all")
            run_check "Frontend Tests (jest)" "npm run test" "$FRONTEND_DIR" || failed=1
            ;;
    esac
    
    case $check_type in
        "coverage"|"all")
            run_check "Frontend Coverage (jest)" "npm run test:coverage" "$FRONTEND_DIR" || failed=1
            ;;
    esac
    
    case $check_type in
        "build"|"all")
            run_check "Frontend Build (next)" "npm run build" "$FRONTEND_DIR" || failed=1
            ;;
    esac
    
    return $failed
}

# Function to run auto-fixes
run_fixes() {
    print_header "🔧 AUTO-FIXING ISSUES"
    
    if [ -d "$BACKEND_DIR" ]; then
        echo -e "${BLUE}🐍 Fixing backend issues...${NC}"
        run_check "Fix Backend Formatting" "uv run black ." "$BACKEND_DIR"
        run_check "Fix Backend Imports" "uv run isort ." "$BACKEND_DIR"
    fi
    
    if [ -d "$FRONTEND_DIR" ]; then
        echo -e "${BLUE}🌐 Fixing frontend issues...${NC}"
        run_check "Fix Frontend Linting" "npm run lint -- --fix" "$FRONTEND_DIR"
    fi
}

# Main execution
main() {
    local check_type="all"
    local component="all"
    local fix_mode=false
    local parallel=false
    local verbose=false
    local quiet=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -p|--parallel)
                parallel=true
                shift
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            -q|--quiet)
                quiet=true
                shift
                ;;
            --fix)
                fix_mode=true
                shift
                ;;
            backend|frontend|quick|lint|types|tests|coverage|build|all)
                component="$1"
                shift
                ;;
            *)
                echo -e "${RED}❌ Unknown argument: $1${NC}"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Set check type based on component
    case $component in
        backend|frontend|all)
            check_type="all"
            ;;
        *)
            check_type="$component"
            ;;
    esac
    
    # Show start message
    echo -e "${CYAN}🚀 Clinical Trial Accelerator - Local Quality Checks${NC}"
    echo -e "${CYAN}Component: $component | Type: $check_type${NC}"
    if [ "$fix_mode" = true ]; then
        echo -e "${CYAN}Mode: Auto-fix enabled${NC}"
    fi
    echo ""
    
    local start_time=$(date +%s)
    local total_failed=0
    
    # Run auto-fixes if requested
    if [ "$fix_mode" = true ]; then
        run_fixes
    fi
    
    # Run checks based on component
    case $component in
        "backend")
            run_backend_checks "$check_type" || total_failed=1
            ;;
        "frontend")
            run_frontend_checks "$check_type" || total_failed=1
            ;;
        "all")
            if [ "$parallel" = true ]; then
                echo -e "${BLUE}🔄 Running backend and frontend checks in parallel...${NC}"
                run_backend_checks "$check_type" &
                backend_pid=$!
                run_frontend_checks "$check_type" &
                frontend_pid=$!
                
                wait $backend_pid || total_failed=1
                wait $frontend_pid || total_failed=1
            else
                run_backend_checks "$check_type" || total_failed=1
                run_frontend_checks "$check_type" || total_failed=1
            fi
            ;;
        *)
            # Component is actually a check type, run on both
            run_backend_checks "$component" || total_failed=1
            run_frontend_checks "$component" || total_failed=1
            ;;
    esac
    
    # Summary
    local end_time=$(date +%s)
    local total_duration=$((end_time - start_time))
    
    print_header "📊 SUMMARY"
    
    if [ $total_failed -eq 0 ]; then
        echo -e "${GREEN}🎉 All checks passed! (${total_duration}s)${NC}"
        echo -e "${GREEN}✅ Ready to push to GitHub${NC}"
        echo ""
        echo -e "${BLUE}💡 To push:${NC}"
        echo -e "${CYAN}  git add . && git commit -m \"your message\" && git push origin main${NC}"
    else
        echo -e "${RED}💥 Some checks failed! (${total_duration}s)${NC}"
        echo -e "${YELLOW}🔧 Try running with --fix to auto-fix some issues:${NC}"
        echo -e "${CYAN}  $0 --fix${NC}"
        echo ""
        echo -e "${BLUE}💡 Or fix manually and run again:${NC}"
        echo -e "${CYAN}  $0 $component${NC}"
        exit 1
    fi
}

# Run main function
main "$@"