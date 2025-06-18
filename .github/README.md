# CI/CD Documentation

This directory contains the GitHub Actions workflows and templates for the Clinical Trial Accelerator project.

## 🔄 Workflows

### [`ci.yml`](./workflows/ci.yml) - Main CI/CD Pipeline

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Jobs:**

1. **Backend Tests** (`backend-test`)
   - Runs on Python 3.11 and 3.12
   - Installs dependencies with `uv`
   - Runs linting (black, isort)
   - Runs type checking (mypy)
   - Runs tests with coverage (≥80% required)
   - Uploads coverage to Codecov

2. **Frontend Tests** (`frontend-test`)
   - Runs on Node.js 18, 20, and 22
   - Installs dependencies with npm
   - Runs linting (eslint)
   - Runs type checking (tsc)
   - Runs tests with coverage (≥80% required)
   - Uploads coverage to Codecov

3. **Security Scan** (`security-scan`)
   - Runs Trivy vulnerability scanner
   - Uploads results to GitHub Security tab

4. **Quality Gate** (`quality-gate`)
   - Ensures all tests pass
   - Verifies coverage thresholds
   - Required for merging

5. **Integration Tests** (`integration-test`)
   - Runs only on pull requests
   - Starts Qdrant service
   - Tests backend health endpoints
   - Builds frontend
   - Runs integration health checks

6. **Deploy** (`deploy`)
   - Runs only on pushes to `main`
   - Deploys to staging environment

### [`dependencies.yml`](./workflows/dependencies.yml) - Dependency Management

**Triggers:**
- Scheduled weekly (Mondays at 9 AM UTC)
- Manual trigger via workflow_dispatch

**Jobs:**

1. **Backend Dependency Updates** (`update-backend-deps`)
   - Updates Python dependencies
   - Runs tests with updated deps
   - Creates PR if successful

2. **Frontend Dependency Updates** (`update-frontend-deps`)
   - Updates npm dependencies
   - Runs tests and build
   - Creates PR if successful

3. **Security Audit** (`security-audit`)
   - Runs security checks on all dependencies
   - Generates security report
   - Uploads report as artifact

## 📝 Templates

### Pull Request Template
[`pull_request_template.md`](./pull_request_template.md)

Comprehensive PR template that includes:
- Change description and type
- Testing checklist (backend + frontend)
- Code quality requirements
- Security and accessibility considerations

### Issue Templates

1. **Bug Report** ([`ISSUE_TEMPLATE/bug_report.md`](./ISSUE_TEMPLATE/bug_report.md))
   - Environment details
   - Reproduction steps
   - Error logs
   - Screenshots

2. **Feature Request** ([`ISSUE_TEMPLATE/feature_request.md`](./ISSUE_TEMPLATE/feature_request.md))
   - Use cases and user stories
   - Implementation details
   - Acceptance criteria
   - Technical considerations

## 🔧 Setup Requirements

### Repository Secrets

Add these secrets to your repository settings:

```
CODECOV_TOKEN=<your-codecov-token>
```

### Branch Protection Rules

Recommended settings for `main` branch:

```yaml
Protection Rules:
  ✅ Require a pull request before merging
  ✅ Require approvals (1 minimum)
  ✅ Dismiss stale PR approvals when new commits are pushed
  ✅ Require review from code owners
  ✅ Require status checks to pass before merging
    Required checks:
      - Backend Tests (backend-test)
      - Frontend Tests (frontend-test)  
      - Quality Gate (quality-gate)
      - Security Scan (security-scan)
  ✅ Require branches to be up to date before merging
  ✅ Require conversation resolution before merging
  ✅ Restrict pushes that create files larger than 100MB
```

## 📊 Coverage Reporting

### Setup Codecov

1. Go to [codecov.io](https://codecov.io)
2. Connect your GitHub repository
3. Copy the upload token
4. Add `CODECOV_TOKEN` to repository secrets

### Coverage Thresholds

- **Backend**: 80% minimum coverage
- **Frontend**: 80% minimum coverage
- **Overall**: 80% minimum coverage

Coverage reports are generated for:
- Lines, branches, functions, statements
- Individual files and overall project
- Diff coverage for PRs

## 🚨 Quality Gates

### Backend Quality Requirements

```bash
# All commands must pass:
uv run black --check .           # Code formatting
uv run isort --check-only .      # Import sorting
uv run mypy app/                 # Type checking
uv run pytest --cov-fail-under=80  # Test coverage
```

### Frontend Quality Requirements

```bash
# All commands must pass:
npm run lint                     # ESLint checks
npm run type-check              # TypeScript checks
npm run test:coverage           # Test coverage ≥80%
npm run build                   # Build successfully
```

## 🔒 Security

### Automated Security Checks

1. **Trivy Scanner**
   - Scans for vulnerabilities in dependencies
   - Scans filesystem for security issues
   - Results uploaded to GitHub Security tab

2. **Dependency Audits**
   - Backend: `safety check` for Python packages
   - Frontend: `npm audit` for npm packages
   - Weekly automated security reports

3. **Supply Chain Security**
   - Dependabot enabled for security updates
   - Pin dependencies to specific versions
   - Regular dependency updates via automation

## 🚀 Deployment

### Staging Deployment

Automatic deployment to staging on every push to `main`:

```yaml
Environment: staging
Trigger: Push to main branch
Platform: Vercel (or configured platform)
Health Checks: Automated post-deployment
```

### Production Deployment

Manual deployment process:
1. Create release tag
2. Manual approval required
3. Deploy to production
4. Run smoke tests
5. Monitor metrics

## 📈 Monitoring

### CI/CD Metrics

Track these metrics:
- **Build Success Rate**: Target >95%
- **Test Duration**: Backend <2min, Frontend <3min
- **Coverage Trends**: Maintain >80%
- **Security Issues**: Target 0 high/critical

### Performance Benchmarks

- **Backend Tests**: Should complete in <2 minutes
- **Frontend Tests**: Should complete in <3 minutes
- **Build Time**: Should complete in <5 minutes
- **Deploy Time**: Should complete in <10 minutes

## 🔧 Troubleshooting

### Common Issues

1. **Coverage Failing**
   ```bash
   # Check coverage locally
   cd backend && uv run pytest --cov=app --cov-report=term-missing
   cd frontend && npm run test:coverage
   ```

2. **Type Checking Errors**
   ```bash
   # Backend
   cd backend && uv run mypy app/
   
   # Frontend  
   cd frontend && npm run type-check
   ```

3. **Linting Failures**
   ```bash
   # Backend
   cd backend && uv run black . && uv run isort .
   
   # Frontend
   cd frontend && npm run lint -- --fix
   ```

### Getting Help

1. Check the [Actions tab](../../actions) for detailed logs
2. Review [Issues](../../issues) for known problems
3. Check [Discussions](../../discussions) for Q&A
4. Contact the development team

## 📚 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Codecov Documentation](https://docs.codecov.com/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Vitest Documentation](https://vitest.dev/)
- [pytest Documentation](https://docs.pytest.org/)