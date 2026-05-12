# Tasks: Durable Loan Persistence

**Input**: Design documents from `/specs/010-durable-loan-persistence/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are REQUIRED by FR-014. Write pytest coverage for each user
story before implementation and keep the final coverage gate at 80% or higher.

**Organization**: Tasks are grouped by user story so each story can be
implemented and tested independently after the shared persistence foundation is
complete.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and does not
  depend on incomplete tasks in the same phase.
- **[Story]**: User story label for story phases only.
- Every task includes exact file paths.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare local persistence structure, ignored database artifacts,
and test fixtures.

- [X] T001 Update `.gitignore` to ignore local SQLite demo artifacts such as `instance/`, `*.sqlite`, `*.sqlite3`, and `*.db`.
- [X] T002 [P] Create repository package marker in `app/repositories/__init__.py`.
- [X] T003 [P] Add temporary SQLite database path fixtures and shared protected-app factory helpers in `tests/conftest.py`.
- [X] T004 [P] Document the planned local database path environment variable in `README.md`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish SQLite schema initialization, repository wiring, and
storage-error response primitives before user stories are implemented.

**CRITICAL**: No user story work should begin until this phase is complete.

- [X] T005 [P] Add SQLite schema initialization and empty-state repository tests in `tests/unit/test_loan_repository.py`.
- [X] T006 Create `SQLiteLoanRepository`, `LoanStorageError`, schema initialization, and connection handling in `app/repositories/loan_repository.py`.
- [X] T007 Update Flask app factory configuration for `LOAN_DATABASE_PATH`, parent directory creation, repository initialization, and `LoanService` injection in `app/__init__.py`.
- [X] T008 Update `LoanService` constructor to accept a repository dependency and remove direct process-local dictionary ownership in `app/services/loan_service.py`.
- [X] T009 Add durable storage unavailable error mapping with `loan_storage_unavailable` JSON response handling in `app/services/loan_service.py` and `app/routes.py`.
- [X] T010 Run foundational tests for `tests/unit/test_loan_repository.py`, `tests/unit/test_loan_service.py`, and `tests/integration/test_health_api.py`.

**Checkpoint**: Persistence foundation is ready; user story implementation can begin.

---

## Phase 3: User Story 1 - Retrieve Loans After Restart (Priority: P1) MVP

**Goal**: Authenticated reviewers can create loans, restart the application,
and still retrieve those loans by loan ID, full listing, and borrower-name
search.

**Independent Test**: Create a loan using one authenticated app instance, create
a second app instance using the same database path, then verify lookup, listing,
and borrower-name search still return the loan.

### Tests for User Story 1

- [X] T011 [P] [US1] Add repository cross-instance create/get/list/search persistence tests in `tests/unit/test_loan_repository.py`.
- [X] T012 [P] [US1] Add authenticated restart persistence integration tests for lookup, listing, and borrower-name search in `tests/integration/test_durable_loan_persistence.py`.

### Implementation for User Story 1

- [X] T013 [US1] Implement durable `create`, `get`, `list_all`, and `list_by_borrower_name` repository methods in `app/repositories/loan_repository.py`.
- [X] T014 [US1] Update `LoanService.create_loan`, `LoanService.get_loan`, `LoanService.list_loans`, and `LoanService.list_loans_by_borrower_name` to use the repository in `app/services/loan_service.py`.
- [X] T015 [US1] Ensure insertion-order listing and borrower-name search ordering are preserved across restarts in `app/repositories/loan_repository.py`.
- [X] T016 [US1] Run targeted US1 tests in `tests/unit/test_loan_repository.py` and `tests/integration/test_durable_loan_persistence.py`.

**Checkpoint**: User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - Preserve Existing Loan Behaviour (Priority: P2)

**Goal**: Existing authenticated API and website success/error behaviours remain
unchanged while using durable storage.

**Independent Test**: Run existing authenticated create, list, borrower-name
search, loan ID lookup, and delete tests against SQLite-backed storage and
verify duplicate, validation, empty, not-found, and deletion responses are
unchanged.

### Tests for User Story 2

- [X] T017 [US2] Update service tests to construct `LoanService` with isolated SQLite repositories in `tests/unit/test_loan_service.py`.
- [X] T018 [P] [US2] Add duplicate-after-restart and invalid-input-no-partial-record tests in `tests/integration/test_durable_loan_persistence.py`.
- [X] T019 [P] [US2] Add delete-persists-absence-after-restart tests in `tests/integration/test_durable_loan_persistence.py`.
- [X] T020 [P] [US2] Update existing authenticated API regression expectations for durable storage in `tests/integration/test_auth_protected_api.py`.

### Implementation for User Story 2

- [X] T021 [US2] Implement durable duplicate detection and duplicate-error mapping in `app/repositories/loan_repository.py` and `app/services/loan_service.py`.
- [X] T022 [US2] Implement durable `delete` repository method and service deletion flow in `app/repositories/loan_repository.py` and `app/services/loan_service.py`.
- [X] T023 [US2] Preserve existing validation, not-found, duplicate, empty-list, and response-shape behaviours in `app/services/loan_service.py` and `app/routes.py`.
- [X] T024 [US2] Run targeted US2 tests in `tests/unit/test_loan_service.py`, `tests/integration/test_auth_protected_api.py`, and `tests/integration/test_durable_loan_persistence.py`.

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Start Cleanly In Local Demo Environments (Priority: P3)

**Goal**: Fresh local environments start with prepared empty durable storage,
and storage failures produce clear service feedback without changing Auth0
behaviour.

**Independent Test**: Start a new app with an unused database path and verify an
empty loan collection is available without manual setup; simulate storage
failure and verify a clear service error is returned for protected loan
workflows.

### Tests for User Story 3

- [X] T025 [P] [US3] Add app-startup initialization tests for unused database paths in `tests/integration/test_durable_loan_persistence.py`.
- [X] T026 [P] [US3] Add storage-unavailable API error tests for create, list, lookup, search, and delete in `tests/integration/test_durable_loan_persistence.py`.
- [X] T027 [P] [US3] Add website JavaScript feedback tests for `loan_storage_unavailable` handling in `tests/integration/test_loan_website.py`.
- [X] T028 [P] [US3] Add documentation example assertions for `LOAN_DATABASE_PATH` and restart verification in `tests/integration/test_documentation_examples.py`.

### Implementation for User Story 3

- [X] T029 [US3] Ensure app startup creates the SQLite parent directory, database file, and loans table automatically in `app/__init__.py` and `app/repositories/loan_repository.py`.
- [X] T030 [US3] Add stable `loan_storage_unavailable` API payloads for repository setup/read/write failures in `app/routes.py`, `app/services/loan_service.py`, and `app/repositories/loan_repository.py`.
- [X] T031 [US3] Update website error handling for `loan_storage_unavailable` without stale success states in `app/static/loan_website.js`.
- [X] T032 [US3] Run targeted US3 tests in `tests/integration/test_durable_loan_persistence.py`, `tests/integration/test_loan_website.py`, and `tests/integration/test_documentation_examples.py`.

**Checkpoint**: All user stories are independently functional.

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, regression coverage, cleanup, and final verification
across the complete feature.

- [X] T033 [P] Update durable persistence setup, reset, restart-demo, and storage trade-off documentation in `README.md`.
- [X] T034 [P] Update final implementation notes in `specs/010-durable-loan-persistence/quickstart.md`.
- [X] T035 [P] Review OpenAPI persistence and storage-error contract alignment in `specs/010-durable-loan-persistence/contracts/openapi.yaml`.
- [X] T036 Update legacy docs/tests that mention process-local or in-memory loan storage in `README.md`, `tests/integration/test_documentation_examples.py`, and older spec quickstarts if required.
- [X] T037 Run full regression suite with `.venv/bin/python -m pytest --cov=app --cov-report=term-missing --cov-fail-under=80` and fix coverage gaps in `app/` and `tests/`.
- [X] T038 Perform final security/scope review to confirm Auth0 behaviour, roles, per-user ownership, public deployment, container registry, Kubernetes, and cloud infrastructure remain unchanged in `app/`, `README.md`, and `specs/010-durable-loan-persistence/`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup** has no dependencies.
- **Phase 2: Foundational** depends on Setup and blocks all user stories.
- **Phase 3: US1** depends on Foundational and is the MVP.
- **Phase 4: US2** depends on Foundational and can be tested after repository CRUD exists.
- **Phase 5: US3** depends on Foundational and validates startup/error surfaces.
- **Final Phase** depends on all desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: No dependency on US2/US3 after Foundational; proves durable retrieval after restart.
- **US2 (P2)**: Builds on durable repository operations from US1 for duplicate/delete regressions, but remains independently testable with seeded durable records.
- **US3 (P3)**: Uses repository setup/error primitives from Foundational and can be validated independently with fresh or failing database paths.

### Within Each User Story

- Write tests before implementation tasks in that story.
- Repository behaviour before service integration.
- Service integration before route/UI feedback.
- Run targeted tests at each checkpoint before moving to the next phase.

---

## Parallel Opportunities

- T002, T003, and T004 can run in parallel after T001 is understood.
- T005 can be written while T006 is being sketched, but implementation should wait for schema expectations.
- T011 and T012 can run in parallel for US1 because they touch different test files.
- T018, T019, and T020 can run in parallel for US2.
- T025, T026, T027, and T028 can run in parallel for US3.
- T033, T034, and T035 can run in parallel during the final phase.

## Parallel Example: User Story 1

```text
Task: "Add repository cross-instance create/get/list/search persistence tests in tests/unit/test_loan_repository.py"
Task: "Add authenticated restart persistence integration tests for lookup, listing, and borrower-name search in tests/integration/test_durable_loan_persistence.py"
```

## Parallel Example: User Story 2

```text
Task: "Add duplicate-after-restart and invalid-input-no-partial-record tests in tests/integration/test_durable_loan_persistence.py"
Task: "Update existing authenticated API regression expectations for durable storage in tests/integration/test_auth_protected_api.py"
```

## Parallel Example: User Story 3

```text
Task: "Add storage-unavailable API error tests for create, list, lookup, search, and delete in tests/integration/test_durable_loan_persistence.py"
Task: "Add website JavaScript feedback tests for loan_storage_unavailable handling in tests/integration/test_loan_website.py"
Task: "Add documentation example assertions for LOAN_DATABASE_PATH and restart verification in tests/integration/test_documentation_examples.py"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: US1.
4. Validate restart retrieval through repository and authenticated API tests.

### Incremental Delivery

1. Add US1 for durable create/retrieve/list/search after restart.
2. Add US2 to preserve duplicate, validation, deletion, empty, and not-found behaviours.
3. Add US3 for fresh startup and storage-unavailable feedback.
4. Finish documentation and full coverage verification.

### Single-Developer Strategy

Work sequentially in priority order: Setup -> Foundational -> US1 -> US2 -> US3
-> Polish. Stop at each checkpoint and run the targeted tests before continuing.

## Notes

- SQLite should use Python standard library `sqlite3`; do not add SQLAlchemy or a managed database for this slice.
- Store monetary values as decimal text internally and preserve existing JSON response numbers.
- Do not silently fall back to in-memory storage if durable storage fails.
- Keep Auth0 authentication, roles, per-user loan ownership, public deployment,
  container registry, Kubernetes, and cloud infrastructure unchanged and out of scope.
