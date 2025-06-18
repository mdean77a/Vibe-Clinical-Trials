#!/bin/bash

# Branch Protection Setup Script
# This script helps configure branch protection rules for the repository

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔒 Setting up branch protection for Clinical Trial Accelerator${NC}"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) is not installed.${NC}"
    echo "Please install it from: https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}⚠️  You need to authenticate with GitHub CLI first.${NC}"
    echo "Run: gh auth login"
    exit 1
fi

# Get repository information
REPO_OWNER=$(gh repo view --json owner --jq '.owner.login')
REPO_NAME=$(gh repo view --json name --jq '.name')

echo -e "${GREEN}✅ Repository: ${REPO_OWNER}/${REPO_NAME}${NC}"
echo ""

# Function to create branch protection rule
setup_branch_protection() {
    local branch=$1
    
    echo -e "${BLUE}🛡️  Setting up protection for '${branch}' branch...${NC}"
    
    # Create the protection rule
    gh api repos/${REPO_OWNER}/${REPO_NAME}/branches/${branch}/protection \
        --method PUT \
        --field required_status_checks='{"strict":true,"contexts":["Backend Tests (backend-test)","Frontend Tests (frontend-test)","Quality Gate (quality-gate)","Security Scan (security-scan)"]}' \
        --field enforce_admins=true \
        --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true,"require_code_owner_reviews":true,"require_last_push_approval":false}' \
        --field restrictions=null \
        --field allow_force_pushes=false \
        --field allow_deletions=false \
        --field block_creations=false \
        --field required_conversation_resolution=true \
        --field required_linear_history=false \
        --field allow_fork_syncing=true
    
    echo -e "${GREEN}✅ Protection rules applied to '${branch}' branch${NC}"
}

# Setup protection for main branch
echo -e "${YELLOW}📋 Setting up branch protection rules...${NC}"
echo ""

if gh api repos/${REPO_OWNER}/${REPO_NAME}/branches/main &> /dev/null; then
    setup_branch_protection "main"
else
    echo -e "${YELLOW}⚠️  'main' branch not found, skipping...${NC}"
fi

# Setup protection for develop branch if it exists
if gh api repos/${REPO_OWNER}/${REPO_NAME}/branches/develop &> /dev/null; then
    setup_branch_protection "develop"
else
    echo -e "${YELLOW}⚠️  'develop' branch not found, skipping...${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Branch protection setup complete!${NC}"
echo ""
echo -e "${BLUE}📋 Summary of protection rules:${NC}"
echo "  ✅ Require pull request reviews (1 approval minimum)"
echo "  ✅ Dismiss stale reviews when new commits are pushed"
echo "  ✅ Require review from code owners"
echo "  ✅ Require status checks to pass:"
echo "     - Backend Tests"
echo "     - Frontend Tests"
echo "     - Quality Gate"
echo "     - Security Scan"
echo "  ✅ Require branches to be up to date"
echo "  ✅ Require conversation resolution"
echo "  ✅ Include administrators in restrictions"
echo "  ✅ Restrict force pushes"
echo "  ✅ Restrict branch deletions"
echo ""
echo -e "${BLUE}📝 Next steps:${NC}"
echo "1. Set up Codecov token in repository secrets"
echo "2. Configure any additional required status checks"
echo "3. Add CODEOWNERS file for automatic review assignments"
echo "4. Test the CI/CD pipeline with a pull request"
echo ""
echo -e "${GREEN}🚀 Your repository is now protected and ready for collaborative development!${NC}"