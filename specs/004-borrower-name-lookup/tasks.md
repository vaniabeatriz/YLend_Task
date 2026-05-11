# Tasks: Borrower Name Loan Lookup

**Input**: Design documents from `/specs/004-borrower-name-lookup/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are REQUIRED. Include pytest tasks for each user story and a final coverage gate of at least 80%.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Flask app**: `app/`, `app/models/`, `app/services/`, and `tests/` at repository root
- **Documentation**: `README.md` plus `specs/004-borrower-name-lookup/quickstart.md`
- **Contract**: `specs/004-borrower-name-lookup/contracts/openapi.yaml`
- Paths shown below follow the plan in `specs/004-borrower-name-lookup/plan.md`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm Spec Kit pointers and existing Flask test dependencies are ready for the borrower-name lookup slice.

- [X] T001 Verify `.specify/feature.json` points to `specs/004-borrower-name-lookup`
- [X] T002 [P] Verify existing Flask, pytest, and pytest-cov dependencies remain sufficient in `requirements.txt`
- [X] T003 [P] Verify `AGENTS.md` points to `specs/004-borrower-name-lookup/plan.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Existing app behavior that MUST remain available while adding borrower-name lookup.

**CRITICAL**: No borrower-name lookup user story work can begin until this phase is complete.

- [X] T004 Verify create-loan seeding remains available for borrower-name lookup tests in `app/routes.py`
- [X] T005 Verify full listing on `GET /loans` remains available before adding borrower-name query handling in `app/routes.py`
- [X] T006 Verify loan ID lookup on `GET /loans/<loanId>` remains available and route order remains safe in `app/routes.py`
- [X] T007 [P] Verify `Loan.to_dict()` returns the borrower-name lookup response shape in `app/models/loan.py`
- [X] T008 Verify `LoanService` keeps current loans in one process-local store in `app/services/loan_service.py`
- [X] T009 [P] Verify Flask app/client fixtures isolate in-memory app sessions in `tests/conftest.py`

**Checkpoint**: Foundation ready - borrower-name lookup user story implementation can now begin.

---

## Phase 3: User Story 1 - Find Current Loans By Borrower Name (Priority: P1) MVP

**Goal**: Caller can retrieve all current loans whose stored borrower name matches the supplied borrower-name search term.

**Independent Test**: Create multiple valid loans, including two with the same borrower name and one with a different borrower name, search for the shared borrower name, and confirm only matching current loans are returned exactly once.

### Tests for User Story 1 (REQUIRED)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T010 [P] [US1] Add service test for borrower-name lookup returning all matching loans with trimmed search term and case-sensitive matching in `tests/unit/test_loan_service.py`
- [X] T011 [P] [US1] Add integration test for successful `GET /loans?borrowerName=Jane%20Smith` after multiple `POST /loans` requests in `tests/integration/test_borrower_name_lookup_api.py`
- [X] T012 [P] [US1] Add integration regression test proving `GET /loans` still returns the full collection and `GET /loans/<loanId>` still returns one loan in `tests/integration/test_borrower_name_lookup_api.py`

### Implementation for User Story 1

- [X] T013 [US1] Implement `LoanService.list_loans_by_borrower_name()` matching stored borrower names exactly after trimming the search term in `app/services/loan_service.py`
- [X] T014 [US1] Update `GET /loans` route to branch to borrower-name lookup only when `borrowerName` query parameter is present in `app/routes.py`
- [X] T015 [US1] Ensure borrower-name lookup response uses the existing `{"loans": [...]}` envelope in `app/routes.py`
- [X] T016 [US1] Run User Story 1 service and integration tests covering `tests/unit/test_loan_service.py` and `tests/integration/test_borrower_name_lookup_api.py`

**Checkpoint**: User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - Understand No Borrower Matches (Priority: P2)

**Goal**: Caller receives a successful empty collection when no current loans match the searched borrower name.

**Independent Test**: Search for a borrower name that has no current matching loans and confirm the response is `{"loans": []}` without changing full listing or loan ID lookup behavior.

### Tests for User Story 2 (REQUIRED)

- [X] T017 [P] [US2] Add service test for borrower-name lookup returning an empty list when no stored borrower name matches in `tests/unit/test_loan_service.py`
- [X] T018 [P] [US2] Add integration test for unknown borrower-name lookup returning `200 OK` with `{"loans": []}` in `tests/integration/test_borrower_name_lookup_api.py`
- [X] T019 [P] [US2] Add integration test proving restart-session borrower-name lookup returns `{"loans": []}` in `tests/integration/test_borrower_name_lookup_api.py`

### Implementation for User Story 2

- [X] T020 [US2] Ensure `LoanService.list_loans_by_borrower_name()` returns an empty list when no current loans match in `app/services/loan_service.py`
- [X] T021 [US2] Ensure `GET /loans?borrowerName=<unknown>` returns `200 OK` with `{"loans": []}` in `app/routes.py`
- [X] T022 [US2] Run User Story 2 service and integration tests covering `tests/unit/test_loan_service.py` and `tests/integration/test_borrower_name_lookup_api.py`

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Reject Invalid Borrower Search Terms (Priority: P3)

**Goal**: Caller receives clear validation feedback when borrower-name lookup is requested with an empty or whitespace-only search term.

**Independent Test**: Request borrower-name lookup with an empty and whitespace-only borrower name and confirm the request is rejected with a clear borrowerName-required message.

### Tests for User Story 3 (REQUIRED)

- [X] T023 [P] [US3] Add service test for blank and whitespace-only borrower-name search terms raising clear validation details in `tests/unit/test_loan_service.py`
- [X] T024 [P] [US3] Add integration test for `GET /loans?borrowerName=` returning `400 Bad Request` with borrowerName validation details in `tests/integration/test_borrower_name_lookup_api.py`
- [X] T025 [P] [US3] Add integration test for whitespace-only `borrowerName` query returning `400 Bad Request` with borrowerName validation details in `tests/integration/test_borrower_name_lookup_api.py`

### Implementation for User Story 3

- [X] T026 [US3] Add borrower-name lookup validation error handling in `app/services/loan_service.py`
- [X] T027 [US3] Map borrower-name lookup validation failures to the existing validation error JSON shape in `app/routes.py`
- [X] T028 [US3] Ensure missing `borrowerName` query parameter still performs full listing while present blank `borrowerName` is rejected in `app/routes.py`
- [X] T029 [US3] Run User Story 3 service and integration tests covering `tests/unit/test_loan_service.py` and `tests/integration/test_borrower_name_lookup_api.py`

**Checkpoint**: All borrower-name lookup user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, contract consistency, regression coverage, and final verification across the borrower-name lookup slice.

- [X] T030 [P] Update borrower-name lookup demo, no-match demo, blank-term validation demo, restart behavior, and coverage result in `README.md`
- [X] T031 [P] Review and update setup, seed, borrower lookup, no-match, blank-term, restart, and test instructions in `specs/004-borrower-name-lookup/quickstart.md`
- [X] T032 [P] Update documentation smoke checks for borrower-name lookup examples in `tests/integration/test_documentation_examples.py`
- [X] T033 Review borrower-name lookup response and validation contract consistency in `specs/004-borrower-name-lookup/contracts/openapi.yaml`
- [X] T034 Run existing create, loan ID lookup, full listing, health, and documentation regression tests in `tests/integration/`
- [X] T035 Run full test suite with `pytest --cov=app --cov-report=term-missing --cov-fail-under=80` and record result in `README.md`
- [X] T036 Run quickstart borrower-name lookup validation against the local app using `specs/004-borrower-name-lookup/quickstart.md`
- [X] T037 Remove dead code, unused imports, and unrelated scaffolding from `app/` and `tests/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS borrower-name lookup user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion
- **User Story 2 (Phase 4)**: Depends on Foundational completion and can be implemented after or alongside US1 with shared file coordination
- **User Story 3 (Phase 5)**: Depends on Foundational completion and can be implemented after or alongside US1/US2 with shared file coordination
- **Polish (Phase 6)**: Depends on desired borrower-name lookup user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: MVP; depends on existing create-loan seeding and current loan storage
- **User Story 2 (P2)**: Depends on the borrower-name lookup route/service shape from User Story 1 but remains independently testable through no-match and restart-session requests
- **User Story 3 (P3)**: Depends on the borrower-name lookup route/service shape from User Story 1 but remains independently testable through invalid search requests

### Within Each User Story

- Tests MUST be written and fail before implementation
- Service behavior before route integration
- Route integration before documentation validation
- Story complete before moving to final polish

### Parallel Opportunities

- T002 and T003 can run in parallel after T001
- T007 and T009 can run in parallel with T004, T005, T006, and T008
- T010, T011, and T012 can be written in parallel after Foundational
- T017, T018, and T019 can be written in parallel after Foundational
- T023, T024, and T025 can be written in parallel after Foundational
- T030, T031, and T032 can run in parallel after borrower-name lookup behavior is implemented

---

## Parallel Example: User Story 1

```bash
# Launch User Story 1 test tasks together:
Task: "Add service test for borrower-name lookup returning all matching loans with trimmed search term and case-sensitive matching in tests/unit/test_loan_service.py"
Task: "Add integration test for successful GET /loans?borrowerName=Jane%20Smith after multiple POST /loans requests in tests/integration/test_borrower_name_lookup_api.py"
Task: "Add integration regression test proving GET /loans still returns the full collection and GET /loans/<loanId> still returns one loan in tests/integration/test_borrower_name_lookup_api.py"
```

---

## Parallel Example: User Story 2

```bash
# Launch User Story 2 test tasks together:
Task: "Add service test for borrower-name lookup returning an empty list when no stored borrower name matches in tests/unit/test_loan_service.py"
Task: "Add integration test for unknown borrower-name lookup returning 200 OK with {\"loans\": []} in tests/integration/test_borrower_name_lookup_api.py"
Task: "Add integration test proving restart-session borrower-name lookup returns {\"loans\": []} in tests/integration/test_borrower_name_lookup_api.py"
```

---

## Parallel Example: User Story 3

```bash
# Launch User Story 3 test tasks together:
Task: "Add service test for blank and whitespace-only borrower-name search terms raising clear validation details in tests/unit/test_loan_service.py"
Task: "Add integration test for GET /loans?borrowerName= returning 400 Bad Request with borrowerName validation details in tests/integration/test_borrower_name_lookup_api.py"
Task: "Add integration test for whitespace-only borrowerName query returning 400 Bad Request with borrowerName validation details in tests/integration/test_borrower_name_lookup_api.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Stop and validate `GET /loans?borrowerName=Jane%20Smith` for a non-empty matching loan collection
5. Run the coverage command and confirm the borrower-name lookup slice remains usable

### Incremental Delivery

1. Complete Setup + Foundational
2. Add User Story 1 -> test matching borrower-name lookup
3. Add User Story 2 -> test no-match and restart-session empty borrower-name lookup
4. Add User Story 3 -> test blank and whitespace-only borrower-name validation
5. Complete Polish -> contract consistency, regression tests, quickstart validation, and coverage gate

### Single-Developer Strategy

1. Write failing borrower-name lookup service and API tests first
2. Implement the smallest service and route code to pass non-empty matching lookup
3. Add no-match, restart, and invalid-search tests and behavior
4. Update documentation and run quickstart manually
5. Run the full coverage command before implementation review

---

## Notes

- [P] tasks = different files, no dependencies
- [US1], [US2], and [US3] labels map tasks to the user stories in `specs/004-borrower-name-lookup/spec.md`
- Borrower-name lookup tasks build on the prior create-loan, loan ID lookup, and full-listing workflows but must not add deletion, partial search, pagination, persistence, browser UI, authentication, public exposure, or cloud deployment
- Verify tests fail before implementing each story
- Keep the final solution explainable in under 40 minutes
