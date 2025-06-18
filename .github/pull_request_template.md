# Pull Request

## Description
<!-- Provide a brief description of the changes in this PR -->

## Type of Change
<!-- Mark with an `x` all that apply -->

- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 Documentation update
- [ ] 🧪 Test improvements
- [ ] 🔧 Build/CI improvements
- [ ] ♻️ Code refactoring

## Related Issues
<!-- Link to related issues -->
Fixes #(issue number)

## Changes Made
<!-- List the specific changes made -->

- 
- 
- 

## Testing
<!-- Describe the tests you ran to verify your changes -->

### Backend Tests
- [ ] All backend tests pass (`uv run python -m pytest`)
- [ ] Backend coverage meets threshold (≥80%)
- [ ] Type checking passes (`uv run mypy app/`)
- [ ] Linting passes (`uv run black . && uv run isort .`)

### Frontend Tests  
- [ ] All frontend tests pass (`npm run test:coverage`)
- [ ] Frontend coverage meets threshold (≥80%)
- [ ] Type checking passes (`npm run type-check`)
- [ ] Linting passes (`npm run lint`)

### Manual Testing
- [ ] Tested locally (backend + frontend)
- [ ] Verified user workflows work end-to-end
- [ ] Tested on multiple browsers (if UI changes)
- [ ] Tested responsiveness (if UI changes)

## Screenshots (if applicable)
<!-- Add screenshots for UI changes -->

## Checklist
<!-- Mark with an `x` all that apply -->

### Code Quality
- [ ] My code follows the project's coding standards
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation

### Testing
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] I have checked that my changes don't break existing functionality

### Security & Performance
- [ ] My changes don't introduce security vulnerabilities
- [ ] My changes don't negatively impact performance
- [ ] I have considered the impact on users with disabilities (accessibility)

### Dependencies
- [ ] I have not added unnecessary dependencies
- [ ] If I added dependencies, I have justified their necessity
- [ ] All dependencies are properly licensed and secure

## Additional Notes
<!-- Add any additional information that reviewers should know -->

## Deployment Notes
<!-- Add any special deployment considerations -->

---

**For Reviewers:**
- Please verify all automated checks pass
- Test the changes locally if possible
- Ensure documentation is updated if needed
- Check for potential security implications