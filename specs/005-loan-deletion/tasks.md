# Tasks: Loan Deletion

**Input**: Design documents from `/specs/005-loan-deletion/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/openapi.yaml`, `quickstart.md`

**Tests**: Tests are REQUIRED. Add pytest coverage for each user story and keep the final coverage gate at 80% or higher.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and has no dependency on an incomplete task.
- **[Story]**: User story label for story-specific tasks only.
- Every task includes at least one exact file path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the current branch and existing project setup are ready for the deletion slice.

- [X] T001 Confirm the active feature metadata is `005-loan-deletion` in `.specify/feature.json`.
- [X] T002 [P] Confirm Flask, pytest, and pytest-cov remain sufficient for this slice in `requirements.txt`.
- [X] T003 [P] Confirm repository guidance references the deletion plan in `AGENTS.md`.
- [X] T004 [P] Confirm the deletion endpoint contract and response shape are captured in `specs/005-loan-deletion/contracts/openapi.yaml`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Verify the existing API, service, model, and test fixture behavior that deletion will reuse.

**Critical**: No user story implementation should begin until these checks are complete.

- [X] T005 Review existing create, list, borrower-name lookup, loan ID lookup, and not-found JSON behavior in `app/routes.py`.
- [X] T006 Review existing trimmed, case-sensitive loan ID normalization and in-memory storage behavior in `app/services/loan_service.py`.
- [X] T007 [P] Review `Loan.to_dict()` field names and amount serialization in `app/models/loan.py`.
- [X] T008 [P] Review app and client fixture isolation for current-session tests in `tests/conftest.py`.

**Checkpoint**: Existing API and storage behavior are understood, and deletion can be added without new infrastructure.

---

## Phase 3: User Story 1 - Delete A Current Loan By Loan ID (Priority: P1) MVP

**Goal**: An API caller can delete one current temporary loan by loan ID and receive the deleted loan record.

**Independent Test**: Create a valid loan, delete it by loan ID, then confirm ID lookup, borrower-name lookup, and full listing no longer return that loan while other loans remain available.

### Tests for User Story 1 (REQUIRED)

Write these tests first and confirm they fail before implementation.

- [X] T009 [P] [US1] Add service tests for successful deletion returning the deleted record, trimming the supplied ID, matching case-sensitively, and preserving non-target loans in `tests/unit/test_loan_service.py`.
- [X] T010 [P] [US1] Add integration tests for `DELETE /loans/{loanId}` returning `200 OK`, the deleted loan JSON, the 2-second local performance target, and encoded surrounding whitespace in `tests/integration/test_delete_loan_api.py`.
- [X] T011 [US1] Add integration tests proving a deleted loan is absent from loan ID lookup, full listing, and borrower-name lookup in `tests/integration/test_delete_loan_api.py`.
- [X] T012 [US1] Add an integration regression test proving non-deleted loans still work through create, loan ID lookup, full listing, and borrower-name lookup in `tests/integration/test_delete_loan_api.py`.

### Implementation for User Story 1

- [X] T013 [US1] Implement `LoanService.delete_loan()` success behavior using trimmed, case-sensitive ID matching and removal from the in-memory store in `app/services/loan_service.py`.
- [X] T014 [US1] Add `DELETE /loans/<path:loan_id>` route handling that returns the deleted loan JSON with `200 OK` in `app/routes.py`.
- [X] T015 [US1] Run focused US1 tests with `pytest tests/unit/test_loan_service.py tests/integration/test_delete_loan_api.py` against `app/services/loan_service.py` and `app/routes.py`.

**Checkpoint**: User Story 1 is functional and independently testable.

---

## Phase 4: User Story 2 - Report Missing Loan Deletions Clearly (Priority: P2)

**Goal**: An API caller receives a clear not-found response when the requested loan ID is absent, already deleted, blank, case-mismatched, or from a previous application session.

**Independent Test**: Request deletion for unknown, already-deleted, blank, case-mismatched, and expired loan IDs; confirm each returns `404 loan_not_found` without changing remaining loans.

### Tests for User Story 2 (REQUIRED)

- [X] T016 [P] [US2] Add service tests for unknown, blank, whitespace-only, case-mismatched, and already-deleted loan IDs raising `LoanNotFoundError` in `tests/unit/test_loan_service.py`.
- [X] T017 [P] [US2] Add integration tests for unknown and blank delete requests returning `404 loan_not_found` within the 2-second local performance target in `tests/integration/test_delete_loan_api.py`.
- [X] T018 [US2] Add an integration test for double deletion returning `404 loan_not_found` on the second delete while preserving remaining loans in `tests/integration/test_delete_loan_api.py`.
- [X] T019 [US2] Add an integration test for deletion after a new app session returning `404 loan_not_found` in `tests/integration/test_delete_loan_api.py`.

### Implementation for User Story 2

- [X] T020 [US2] Complete `LoanService.delete_loan()` not-found behavior for blank, whitespace-only, unknown, case-mismatched, and already-deleted IDs in `app/services/loan_service.py`.
- [X] T021 [US2] Map delete not-found errors to the existing `loan_not_found` JSON response in `app/routes.py`.
- [X] T022 [US2] Run focused US2 tests with `pytest tests/unit/test_loan_service.py tests/integration/test_delete_loan_api.py` against `app/services/loan_service.py` and `app/routes.py`.

**Checkpoint**: User Stories 1 and 2 both work and are independently testable.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Update documentation, contract checks, and full regression coverage.

- [X] T023 [P] Update `README.md` scope and demo sections to include `DELETE /loans/<loanId>` and remove loan deletion from out-of-scope.
- [X] T024 [P] Update documentation smoke test expectations for deletion commands and the 005 quickstart path in `tests/integration/test_documentation_examples.py`.
- [X] T025 [P] Review `specs/005-loan-deletion/quickstart.md` against the implemented route, status codes, and JSON shapes.
- [X] T026 [P] Review `specs/005-loan-deletion/contracts/openapi.yaml` against the implemented route, status codes, and error payloads.
- [X] T027 Run all integration tests with `pytest tests/integration` and fix any deletion regressions in `app/routes.py`, `tests/integration/test_delete_loan_api.py`, or existing integration tests.
- [X] T028 Run the full coverage gate with `pytest --cov=app --cov-report=term-missing --cov-fail-under=80` and update the latest local result in `README.md`.
- [X] T029 Perform final diff cleanup for unrelated or accidental edits in `app/services/loan_service.py`, `app/routes.py`, `README.md`, and `tests/`.
- [X] T030 Validate the local demo flow from `specs/005-loan-deletion/quickstart.md` and adjust `README.md` if any command or response drifts.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks user story implementation.
- **User Story 1 (Phase 3)**: Depends on Foundational completion.
- **User Story 2 (Phase 4)**: Depends on Foundational completion and can be tested independently, but implementation may reuse the same delete method added for US1.
- **Polish (Phase 5)**: Depends on the desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: MVP. Can start after Foundational.
- **User Story 2 (P2)**: Can start after Foundational; shares the same route and service surface as US1.

### Within Each User Story

- Write tests before implementation and confirm they fail.
- Service tests before route behavior when possible.
- Service implementation before route wiring.
- Focused story tests before moving to the next story.

## Parallel Opportunities

- **Setup**: T002, T003, and T004 can run in parallel.
- **Foundational**: T007 and T008 can run in parallel.
- **US1 tests**: T009 and T010 can run in parallel because they touch different files; T011 and T012 should be sequenced with other edits to `tests/integration/test_delete_loan_api.py`.
- **US2 tests**: T016 and T017 can run in parallel because they touch different files; T018 and T019 should be sequenced with other edits to `tests/integration/test_delete_loan_api.py`.
- **Polish**: T023, T024, T025, and T026 can run in parallel because they touch different files.

## Parallel Example: User Story 1

```bash
Task: "Add service tests for successful deletion returning the deleted record, trimming the supplied ID, matching case-sensitively, and preserving non-target loans in tests/unit/test_loan_service.py"
Task: "Add integration tests for DELETE /loans/{loanId} returning 200 OK, the deleted loan JSON, the 2-second local performance target, and encoded surrounding whitespace in tests/integration/test_delete_loan_api.py"
```

## Parallel Example: User Story 2

```bash
Task: "Add service tests for unknown, blank, whitespace-only, case-mismatched, and already-deleted loan IDs raising LoanNotFoundError in tests/unit/test_loan_service.py"
Task: "Add integration tests for unknown and blank delete requests returning 404 loan_not_found within the 2-second local performance target in tests/integration/test_delete_loan_api.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational checks.
3. Complete Phase 3: User Story 1.
4. Stop and validate the focused US1 tests.

### Incremental Delivery

1. Complete Setup and Foundational checks.
2. Add US1 deletion success path and validate it independently.
3. Add US2 not-found behavior and validate it independently.
4. Complete documentation, regression, and coverage tasks.

### Validation Targets

- `pytest tests/unit/test_loan_service.py tests/integration/test_delete_loan_api.py`
- `pytest tests/integration`
- `pytest --cov=app --cov-report=term-missing --cov-fail-under=80`

## Notes

- Keep persistence, authentication, browser UI, public exposure, cloud deployment, and infrastructure changes out of scope.
- Use the existing process-local in-memory store; do not add a database or soft-delete flag.
- Successful deletion returns the deleted loan record with `200 OK`.
- Missing, blank, whitespace-only, case-mismatched, already-deleted, and expired loan IDs return the existing `loan_not_found` response.
