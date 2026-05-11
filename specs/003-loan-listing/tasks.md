# Tasks: Loan Listing

**Input**: Design documents from `/specs/003-loan-listing/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are REQUIRED. Include pytest tasks for each user story and a final coverage gate of at least 80%.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Flask app**: `app/`, `app/models/`, `app/services/`, and `tests/` at repository root
- **Documentation**: `README.md` plus `specs/003-loan-listing/quickstart.md`
- **Contract**: `specs/003-loan-listing/contracts/openapi.yaml`
- Paths shown below follow the plan in `specs/003-loan-listing/plan.md`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the existing create/lookup baseline and Spec Kit pointers are ready for the listing slice.

- [X] T001 Verify `.specify/feature.json` points to `specs/003-loan-listing`
- [X] T002 [P] Verify existing Flask, pytest, and pytest-cov dependencies remain sufficient in `requirements.txt`
- [X] T003 [P] Verify `AGENTS.md` points to `specs/003-loan-listing/plan.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Existing app structure that MUST be available before listing user stories can be implemented.

**CRITICAL**: No listing user story work can begin until this phase is complete.

- [X] T004 Verify create-loan seeding remains available for listing tests in `app/routes.py`
- [X] T005 Verify `Loan.to_dict()` returns the listed loan response shape in `app/models/loan.py`
- [X] T006 Verify `LoanService` keeps current loans in one process-local store in `app/services/loan_service.py`
- [X] T007 [P] Verify Flask app/client fixtures isolate in-memory app sessions in `tests/conftest.py`

**Checkpoint**: Foundation ready - listing user story implementation can now begin.

---

## Phase 3: User Story 1 - View Current Loans (Priority: P1) MVP

**Goal**: Caller can retrieve all loans currently stored in the active application session.

**Independent Test**: Create more than one valid loan, request the current loan collection, and confirm every stored loan is returned exactly once.

### Tests for User Story 1 (REQUIRED)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T008 [P] [US1] Add service test for listing all current loans with trimmed stored values and case-sensitive distinct IDs in `tests/unit/test_loan_service.py`
- [X] T009 [P] [US1] Add integration test for successful `GET /loans` after multiple `POST /loans` requests in `tests/integration/test_list_loans_api.py`
- [X] T010 [P] [US1] Add integration test proving rejected validation and duplicate create attempts do not appear in `tests/integration/test_list_loans_api.py`

### Implementation for User Story 1

- [X] T011 [US1] Implement `LoanService.list_loans()` non-empty path returning current loan dictionaries in `app/services/loan_service.py`
- [X] T012 [US1] Wire successful `GET /loans` JSON response with `loans` collection in `app/routes.py`
- [X] T013 [US1] Run User Story 1 service and integration tests covering `tests/unit/test_loan_service.py` and `tests/integration/test_list_loans_api.py`

**Checkpoint**: User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - Understand an Empty Session (Priority: P2)

**Goal**: Caller receives a successful empty collection when no loans exist in the current application session.

**Independent Test**: Start a fresh app session, request the current loan collection before creating any loans, and confirm `loans` is empty.

### Tests for User Story 2 (REQUIRED)

- [X] T014 [P] [US2] Add service test for an empty loan collection in a new `LoanService` in `tests/unit/test_loan_service.py`
- [X] T015 [P] [US2] Add integration test for `GET /loans` returning `{"loans": []}` in a fresh app session in `tests/integration/test_list_loans_api.py`
- [X] T016 [P] [US2] Add integration test proving restart-session listing returns `{"loans": []}` in `tests/integration/test_list_loans_api.py`

### Implementation for User Story 2

- [X] T017 [US2] Ensure `LoanService.list_loans()` returns an empty list when no loans exist in `app/services/loan_service.py`
- [X] T018 [US2] Ensure `GET /loans` returns `200 OK` with `{"loans": []}` for an empty store in `app/routes.py`
- [X] T019 [US2] Run User Story 2 service and integration tests covering `tests/unit/test_loan_service.py` and `tests/integration/test_list_loans_api.py`

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, contract consistency, and final verification across the listing slice.

- [X] T020 [P] Update listing demo, empty-list demo, restart behaviour, and coverage result in `README.md`
- [X] T021 [P] Update listing setup, seed, list, empty-list, restart, and test instructions in `specs/003-loan-listing/quickstart.md`
- [X] T022 [P] Update documentation smoke checks for listing examples in `tests/integration/test_documentation_examples.py`
- [X] T023 Review listing response contract consistency in `specs/003-loan-listing/contracts/openapi.yaml`
- [X] T024 Run full test suite with `pytest --cov=app --cov-report=term-missing --cov-fail-under=80` and record result in `README.md`
- [X] T025 Run quickstart listing validation against the local app using `specs/003-loan-listing/quickstart.md`
- [X] T026 Remove dead code, unused imports, and unrelated scaffolding from `app/` and `tests/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS listing user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion
- **User Story 2 (Phase 4)**: Depends on Foundational completion and can be implemented after or alongside US1 with shared file coordination
- **Polish (Phase 5)**: Depends on desired listing user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: MVP; depends on existing create-loan seeding from prior features
- **User Story 2 (P2)**: Depends on the listing route/service shape from User Story 1 but remains independently testable through fresh-session requests

### Within Each User Story

- Tests MUST be written and fail before implementation
- Service behaviour before route integration
- Route integration before documentation validation
- Story complete before moving to final polish

### Parallel Opportunities

- T002 and T003 can run in parallel after T001
- T007 can run in parallel with T004, T005, and T006
- T008, T009, and T010 can be written in parallel after Foundational
- T014, T015, and T016 can be written in parallel after Foundational
- T020, T021, and T022 can run in parallel after listing behaviour is implemented

---

## Parallel Example: User Story 1

```bash
# Launch User Story 1 test tasks together:
Task: "Add service test for listing all current loans with trimmed stored values and case-sensitive distinct IDs in tests/unit/test_loan_service.py"
Task: "Add integration test for successful GET /loans after multiple POST /loans requests in tests/integration/test_list_loans_api.py"
Task: "Add integration test proving rejected validation and duplicate create attempts do not appear in tests/integration/test_list_loans_api.py"
```

---

## Parallel Example: User Story 2

```bash
# Launch User Story 2 test tasks together:
Task: "Add service test for an empty loan collection in a new LoanService in tests/unit/test_loan_service.py"
Task: "Add integration test for GET /loans returning {\"loans\": []} in a fresh app session in tests/integration/test_list_loans_api.py"
Task: "Add integration test proving restart-session listing returns {\"loans\": []} in tests/integration/test_list_loans_api.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Stop and validate `GET /loans` for a non-empty current loan collection
5. Run the coverage command and confirm the listing slice remains usable

### Incremental Delivery

1. Complete Setup + Foundational
2. Add User Story 1 -> test non-empty loan listing
3. Add User Story 2 -> test empty and restart-session listing
4. Complete Polish -> contract consistency, quickstart validation, and coverage gate

### Single-Developer Strategy

1. Write failing listing service and API tests first
2. Implement the smallest service and route code to pass non-empty listing
3. Add empty-list and restart tests and behaviour
4. Update documentation and run quickstart manually
5. Run the full coverage command before implementation review

---

## Notes

- [P] tasks = different files, no dependencies
- [US1] and [US2] labels map tasks to the user stories in `specs/003-loan-listing/spec.md`
- Listing tasks build on the prior create-loan and lookup workflows but must not add deletion, filtering, searching, sorting controls, pagination, persistence, browser UI, authentication, public exposure, or cloud deployment
- Verify tests fail before implementing each story
- Keep the final solution explainable in under 40 minutes
