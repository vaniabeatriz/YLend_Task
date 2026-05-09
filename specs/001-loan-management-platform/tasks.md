# Tasks: Create Loan

**Input**: Design documents from `/specs/001-loan-management-platform/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are REQUIRED. Include pytest tasks for each user story and a final coverage gate of at least 80%.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Flask app**: `app/`, `app/models/`, `app/services/`, `tests/` at repository root
- **Documentation**: `README.md` plus `specs/001-loan-management-platform/quickstart.md`
- Paths shown below follow the plan in `specs/001-loan-management-platform/plan.md`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directories in app/, app/models/, app/services/, tests/unit/, and tests/integration/
- [X] T002 Create dependency file with Flask, pytest, and pytest-cov in requirements.txt
- [X] T003 [P] Configure pytest defaults and coverage options in pyproject.toml
- [X] T004 [P] Create package marker files in app/__init__.py, app/models/__init__.py, and app/services/__init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create Flask application factory skeleton in app/__init__.py
- [X] T006 Create shared API error response helper in app/routes.py
- [X] T007 [P] Create test fixture skeleton for Flask app/client isolation in tests/conftest.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Create Loan Records (Priority: P1) MVP

**Goal**: API caller can create a valid temporary loan record and receives the stored loan record back.

**Independent Test**: Create a valid loan through the API and confirm the response returns the stored loan record; invalid fields and duplicate loan IDs return clear errors.

### Tests for User Story 1 (REQUIRED)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T008 [P] [US1] Add unit tests for required fields, trimming, positive amounts, and duplicate case-sensitive loan IDs in tests/unit/test_loan_service.py
- [X] T009 [P] [US1] Add integration test for successful POST /loans returning stored loan in tests/integration/test_create_loan_api.py
- [X] T010 [US1] Add integration tests for POST /loans validation errors and duplicate loan ID conflicts in tests/integration/test_create_loan_api.py

### Implementation for User Story 1

- [X] T011 [P] [US1] Create Loan data model with serialization helpers in app/models/loan.py
- [X] T012 [US1] Implement loan validation, normalization, Decimal parsing, duplicate checks, and in-memory store in app/services/loan_service.py
- [X] T013 [US1] Wire POST /loans request parsing, service call, and JSON responses in app/routes.py
- [X] T014 [US1] Register Create Loan route blueprint or route setup from app/routes.py in app/__init__.py
- [X] T015 [US1] Run US1 unit and integration tests and confirm they pass in tests/unit/test_loan_service.py and tests/integration/test_create_loan_api.py

**Checkpoint**: User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - Validate Delivery Readiness (Priority: P2)

**Goal**: Reviewer can run, test, and evaluate the API slice from concise documentation without hidden setup knowledge.

**Independent Test**: From a fresh checkout, follow README/quickstart commands to install dependencies, run the app, check health, create a loan, trigger validation/duplicate errors, and run coverage.

### Tests for User Story 2 (REQUIRED)

- [X] T016 [P] [US2] Add integration test for GET /health returning status ok in tests/integration/test_health_api.py
- [X] T017 [P] [US2] Add documentation command smoke checks for README examples in tests/integration/test_documentation_examples.py

### Implementation for User Story 2

- [X] T018 [US2] Implement GET /health JSON response in app/routes.py
- [X] T019 [P] [US2] Create concise setup, run, test, demo, architecture, trade-off, and assumption documentation in README.md
- [X] T020 [P] [US2] Update specs/001-loan-management-platform/quickstart.md to match final commands and response examples
- [X] T021 [US2] Verify documented setup, health, create-loan, duplicate, validation, and coverage commands in README.md and specs/001-loan-management-platform/quickstart.md

**Checkpoint**: Reviewer readiness story is complete and independently verifiable through documentation and tests.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T022 [P] Add .gitignore entries for .venv/, __pycache__/, .pytest_cache/, and coverage artifacts in .gitignore
- [X] T023 [P] Add .editorconfig with Python and Markdown defaults in .editorconfig
- [X] T024 Review OpenAPI contract consistency against implemented responses in specs/001-loan-management-platform/contracts/openapi.yaml
- [X] T025 Run full test suite with pytest --cov=app --cov-report=term-missing --cov-fail-under=80 and record result in README.md
- [X] T026 Run quickstart validation against the local app using specs/001-loan-management-platform/quickstart.md
- [X] T027 Remove dead code, unused imports, and unrelated scaffolding from app/ and tests/

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion
- **User Story 2 (Phase 4)**: Depends on Foundational completion and can run after US1 route structure exists
- **Polish (Phase 5)**: Depends on desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: MVP; no dependency on User Story 2
- **User Story 2 (P2)**: Depends on app structure from Foundational and uses the implemented API from User Story 1 for documentation validation

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Data model before service
- Service before route integration
- Route integration before documentation validation
- Story complete before moving to final polish

### Parallel Opportunities

- T003 and T004 can run in parallel after T001
- T007 can run in parallel with T005 and T006 after T001-T004
- T008 and T009 can be written in parallel after Foundational; T010 continues in the same integration test file after T009
- T016 and T017 can be written in parallel after Foundational
- T019 and T020 can run in parallel after US1 behaviour is implemented
- T022 and T023 can run in parallel during Polish

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Add unit tests for required fields, trimming, positive amounts, and duplicate case-sensitive loan IDs in tests/unit/test_loan_service.py"
Task: "Add integration test for successful POST /loans returning stored loan in tests/integration/test_create_loan_api.py"
Task: "Add integration tests for POST /loans validation errors and duplicate loan ID conflicts in tests/integration/test_create_loan_api.py"
```

---

## Parallel Example: User Story 2

```bash
# Launch readiness tests and documentation updates together:
Task: "Add integration test for GET /health returning status ok in tests/integration/test_health_api.py"
Task: "Add documentation command smoke checks for README examples in tests/integration/test_documentation_examples.py"
Task: "Create concise setup, run, test, demo, architecture, trade-off, and assumption documentation in README.md"
Task: "Update specs/001-loan-management-platform/quickstart.md to match final commands and response examples"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Stop and validate `POST /loans` independently with unit and integration tests
5. Run the coverage command and confirm the Create Loan API slice is usable

### Incremental Delivery

1. Complete Setup + Foundational
2. Add User Story 1 -> test create-loan success, validation, and duplicate handling
3. Add User Story 2 -> test health/readiness and validate documentation commands
4. Complete Polish -> contract consistency, quickstart validation, and coverage gate

### Single-Developer Strategy

1. Write failing US1 service and API tests first
2. Implement the smallest service and route code to pass US1
3. Add health/documentation readiness tests for US2
4. Update documentation and run quickstart manually
5. Run the full coverage command before moving to implementation review

---

## Notes

- [P] tasks = different files, no dependencies
- [US1] and [US2] labels map tasks to the user stories in spec.md
- All API behaviour tasks must stay inside the Create Loan slice
- Do not implement browser UI, lookup, listing, deletion, authentication, public exposure, or cloud deployment in this task set
- Verify tests fail before implementing each story
- Keep the final solution explainable in under 40 minutes
