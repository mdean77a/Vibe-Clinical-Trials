# Session: Improve Backend Test Coverage to >80%

**Date**: 2025-10-15 14:27
**Branch**: TBD (will create)
**Goal**: Increase backend test coverage from 44% to >80%

## Session Overview

**Start Time**: 14:27
**Current Coverage**: 44%
**Target Coverage**: >80%
**Gap**: 36 percentage points

## Current Coverage Analysis

### Files with Low Coverage (Priority Targets):
1. **app/api/icf_generation.py** - 37% (127 stmts, 80 miss)
   - Missing: Lines 121-207, 230-339, 362-371, 386-395, 403-418
   - Priority: HIGH - Main API endpoints

2. **app/services/document_generator.py** - 37% (249 stmts, 158 miss)
   - Missing: Lines 98-100, 125-127, 134, 138-141, 145-201, 207-223, 246-259, 263, 268-326, 330-339, 343, 369, 374-539, 546-549, 558, 588
   - Priority: HIGH - Core generation logic

3. **app/services/icf_service.py** - 35% (155 stmts, 100 miss)
   - Missing: Lines 59-208, 212-219, 243-276, 292-312, 423-425, 439-441
   - Priority: HIGH - ICF service logic

4. **app/api/protocols.py** - 32% (65 stmts, 44 miss)
   - Missing: Lines 59-61, 89-198
   - Priority: MEDIUM - Upload endpoint needs coverage

5. **app/services/langchain_qdrant_service.py** - 27% (108 stmts, 79 miss)
   - Missing: Lines 32-33, 54-77, 81-84, 97-128, 137-149, 159-177, 186-194, 200-205, 209-215, 219-229, 234-235, 245-247
   - Priority: MEDIUM - Vector storage

6. **app/services/text_processor.py** - 38% (21 stmts, 13 miss)
   - Missing: Lines 30-31, 47-77
   - Priority: LOW - Small utility

7. **app/handler.py** - 0% (2 stmts, 2 miss)
   - Priority: LOW - Vercel handler, hard to test

8. **app/main.py** - 69% (39 stmts, 12 miss)
   - Missing: Lines 35, 46-58, 100-102
   - Priority: LOW - FastAPI app setup

### Files with Good Coverage (Keep Maintained):
- ✅ **app/models.py** - 100%
- ✅ **app/config.py** - 82%
- ✅ **app/services/qdrant_service.py** - 69%

## Strategy

### Phase 1: Quick Wins (Target: +15%)
- Add tests for `text_processor.py` (small file, easy to test)
- Add tests for `protocols.py` upload endpoint
- Improve `qdrant_service.py` to 85%+

### Phase 2: Core Services (Target: +15%)
- Add comprehensive tests for `langchain_qdrant_service.py`
- Improve `document_generator.py` coverage
- Improve `icf_service.py` coverage

### Phase 3: API Endpoints (Target: +6%)
- Add tests for `icf_generation.py` endpoints
- Integration tests for streaming endpoints

## Goals

1. ⬜ Create new session and feature branch
2. ⬜ Phase 1: Text processor + protocols (target: 59% total)
3. ⬜ Phase 2: LangChain + core services (target: 74% total)
4. ⬜ Phase 3: API endpoints (target: >80% total)
5. ⬜ Verify all tests pass
6. ⬜ Update documentation
7. ⬜ Commit and merge

## Progress

### Step 1: Session Setup
- Created session file: `2025-10-15-1427-improve-backend-test-coverage.md`
- Next: Create feature branch

---

## Notes

- Focus on testing business logic, not just hitting lines
- Use mocks appropriately for external dependencies (Qdrant, OpenAI)
- Ensure tests are maintainable and meaningful
- Don't sacrifice test quality for coverage numbers
