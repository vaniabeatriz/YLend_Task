# Tasks: Loan Lookup

**Input**: Design documents from `/specs/002-loan-lookup/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are REQUIRED. Include pytest tasks for each user story and a final coverage gate of at least 80%.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Flask app**: `app/`, `app/models/`, `app/services/`, and `tests/` at repository root
- **Documentation**: `README.md` plus `specs/002-loan-lookup/quickstart.md`
- **Contract**: `specs/002-loan-lookup/contracts/openapi.yaml`
- Paths shown below follow the plan in `specs/002-loan-lookup/plan.md`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the existing create-loan baseline and Spec Kit pointers are ready for the lookup slice.

- [X] T001 Verify `.specify/feature.json` points to `specs/002-loan-lookup`
- [X] T002 [P] Verify existing Flask, pytest, and pytest-cov dependencies remain sufficient in `requirements.txt`
- [X] T003 [P] Verify `AGENTS.md` points to `specs/002-loan-lookup/plan.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Existing app structure that MUST be available before lookup user stories can be implemented.

**CRITICAL**: No lookup user story work can begin until this phase is complete.

- [X] T004 Verify create-loan seeding remains available for lookup tests in `app/routes.py`
- [X] T005 Verify `Loan.to_dict()` returns the contract response shape in `app/models/loan.py`
- [X] T006 [P] Verify Flask app/client fixtures isolate in-memory app sessions in `tests/conftest.py`
- [X] T007 Verify shared JSON error helper can return lookup not-found errors in `app/routes.py`

**Checkpoint**: Foundation ready - lookup user story implementation can now begin.

---

## Phase 3: User Story 1 - Retrieve a Current Loan (Priority: P1) MVP

**Goal**: Caller can retrieve one current loan by loan ID and receive the stored loan record.

**Independent Test**: Create a valid loan, request the same loan ID, and confirm the returned record matches the stored loan.

### Tests for User Story 1 (REQUIRED)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T008 [P] [US1] Add service test for returning an existing loan after trimming lookup ID in `tests/unit/test_loan_service.py`
- [X] T009 [P] [US1] Add integration test for successful `GET /loans/<loanId>` after `POST /loans` in `tests/integration/test_get_loan_api.py`

### Implementation for User Story 1

- [X] T010 [US1] Implement `LoanService.get_loan()` success path using trimmed case-sensitive IDs in `app/services/loan_service.py`
- [X] T011 [US1] Wire successful `GET /loans/<loan_id>` JSON response in `app/routes.py`
- [X] T012 [US1] Run User Story 1 service and integration tests covering `tests/unit/test_loan_service.py` and `tests/integration/test_get_loan_api.py`

**Checkpoint**: User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - Explain Missing Lookup Results (Priority: P2)

**Goal**: Caller receives a clear not-found response when no current loan exists for the requested loan ID.

**Independent Test**: Request an unknown, blank, expired, or case-mismatched loan ID and confirm a clear not-found response.

### Tests for User Story 2 (REQUIRED)

- [X] T013 [P] [US2] Add service tests for unknown, blank, whitespace-only, and case-mismatched lookup IDs in `tests/unit/test_loan_service.py`
- [X] T014 [P] [US2] Add integration test for `404 loan_not_found` on unknown `GET /loans/<loanId>` in `tests/integration/test_get_loan_api.py`
- [X] T015 [P] [US2] Add integration test proving restart-session lookup returns not found in `tests/integration/test_get_loan_api.py`

### Implementation for User Story 2

- [X] T016 [US2] Add `LoanNotFoundError` and missing-ID lookup behaviour in `app/services/loan_service.py`
- [X] T017 [US2] Wire `404 loan_not_found` JSON response for lookup misses in `app/routes.py`
- [X] T018 [US2] Run User Story 2 service and integration tests covering `tests/unit/test_loan_service.py` and `tests/integration/test_get_loan_api.py`

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, contract consistency, and final verification across the lookup slice.

- [X] T019 [P] Update lookup demo, missing-loan demo, and coverage result in `README.md`
- [X] T020 [P] Update lookup setup, demo, missing-loan, restart, and test instructions in `specs/002-loan-lookup/quickstart.md`
- [X] T021 [P] Update documentation smoke checks for lookup examples in `tests/integration/test_documentation_examples.py`
- [X] T022 Review lookup response and error contract consistency in `specs/002-loan-lookup/contracts/openapi.yaml`
- [X] T023 Run full test suite with `pytest --cov=app --cov-report=term-missing --cov-fail-under=80` and record result in `README.md`
- [X] T024 Run quickstart lookup validation against the local app using `specs/002-loan-lookup/quickstart.md`
- [X] T025 Remove dead code, unused imports, and unrelated scaffolding from `app/` and `tests/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS lookup user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion
- **User Story 2 (Phase 4)**: Depends on Foundational completion and can be implemented after or alongside US1 with shared file coordination
- **Polish (Phase 5)**: Depends on desired lookup user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: MVP; depends on existing create-loan seeding from the prior feature
- **User Story 2 (P2)**: Depends on the lookup route/service shape from User Story 1 but remains independently testable through missing-ID requests

### Within Each User Story

- Tests MUST be written and fail before implementation
- Service behaviour before route integration
- Route integration before documentation validation
- Story complete before moving to final polish

### Parallel Opportunities

- T002 and T003 can run in parallel after T001
- T006 can run in parallel with T004, T005, and T007
- T008 and T009 can be written in parallel after Foundational
- T013, T014, and T015 can be written in parallel after Foundational
- T019, T020, and T021 can run in parallel after lookup behaviour is implemented

---

## Parallel Example: User Story 1

```bash
# Launch User Story 1 test tasks together:
Task: "Add service test for returning an existing loan after trimming lookup ID in tests/unit/test_loan_service.py"
Task: "Add integration test for successful GET /loans/<loanId> after POST /loans in tests/integration/test_get_loan_api.py"
```

---

## Parallel Example: User Story 2

```bash
# Launch User Story 2 test tasks together:
Task: "Add service tests for unknown, blank, whitespace-only, and case-mismatched lookup IDs in tests/unit/test_loan_service.py"
Task: "Add integration test for 404 loan_not_found on unknown GET /loans/<loanId> in tests/integration/test_get_loan_api.py"
Task: "Add integration test proving restart-session lookup returns not found in tests/integration/test_get_loan_api.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Stop and validate `GET /loans/<loanId>` for an existing current loan
5. Run the coverage command and confirm the lookup slice remains usable

### Incremental Delivery

1. Complete Setup + Foundational
2. Add User Story 1 -> test successful single-loan lookup
3. Add User Story 2 -> test not-found, case-mismatch, blank, and restart behaviour
4. Complete Polish -> contract consistency, quickstart validation, and coverage gate

### Single-Developer Strategy

1. Write failing lookup service and API tests first
2. Implement the smallest service and route code to pass successful lookup
3. Add not-found tests and error handling
4. Update documentation and run quickstart manually
5. Run the full coverage command before implementation review

---

## Notes

- [P] tasks = different files, no dependencies
- [US1] and [US2] labels map tasks to the user stories in `specs/002-loan-lookup/spec.md`
- Lookup tasks build on the prior create-loan workflow but must not add listing, deletion, persistence, browser UI, authentication, public exposure, or cloud deployment
- Verify tests fail before implementing each story
- Keep the final solution explainable in under 40 minutes
