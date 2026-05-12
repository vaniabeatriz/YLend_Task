# Tasks: Loan Website

**Input**: Design documents from `/specs/006-loan-website/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/ui-contract.md`, `quickstart.md`

**Tests**: Tests are REQUIRED. Add pytest coverage for each user story and keep the final coverage gate at 80% or higher.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and has no dependency on an incomplete task.
- **[Story]**: User story label for story-specific tasks only.
- Every task includes exact file paths.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the website slice uses the existing Flask app and creates only the planned template/static surface.

- [X] T001 Confirm active feature metadata points to `specs/006-loan-website` in `.specify/feature.json`.
- [X] T002 [P] Confirm no new Node, Angular, Auth0, persistence, registry, Kubernetes, or cloud dependency is introduced in `requirements.txt` and `specs/006-loan-website/plan.md`.
- [X] T003 [P] Create or verify the planned website file locations for `app/templates/index.html`, `app/static/loan_website.css`, and `app/static/loan_website.js`.
- [X] T004 [P] Confirm repository guidance points to `specs/006-loan-website/plan.md` in `AGENTS.md`.
- [X] T005 [P] Review the browser entry point, page regions, and existing API dependency contract in `specs/006-loan-website/contracts/ui-contract.md`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Understand the shared app, API, and test surface before adding the website.

**Critical**: No user story implementation should begin until these checks are complete.

- [X] T006 Review existing JSON API route shapes, status codes, and error payloads for website reuse in `app/routes.py`.
- [X] T007 [P] Review Flask app factory defaults for templates and static assets in `app/__init__.py`.
- [X] T008 [P] Review current-session fixture isolation for website tests in `tests/conftest.py`.

**Checkpoint**: Existing app structure and API behaviours are ready for the website layer.

---

## Phase 3: User Story 1 - Create And Review Current Loans (Priority: P1) MVP

**Goal**: A user can open the website, create a valid loan, and see the current loan list update on the same page.

**Independent Test**: Open the website, create a valid loan, and confirm the loan appears in the current loan list with a success message.

### Tests for User Story 1 (REQUIRED)

Write these tests first and confirm they fail before implementation.

- [X] T009 [P] [US1] Add integration tests that `GET /` renders the website shell with create-loan form, current-loans region, global feedback region, Bootstrap reference, and `app/static` asset links in `tests/integration/test_loan_website.py`.
- [X] T010 [US1] Add integration tests that `app/static/loan_website.js` contains create/list API hooks, validation/duplicate feedback handling, current-list refresh hooks, and failed-input preservation selectors in `tests/integration/test_loan_website.py`.

### Implementation for User Story 1

- [X] T011 [US1] Add the `GET /` browser route using template rendering while preserving existing API routes in `app/routes.py`.
- [X] T012 [US1] Create the page shell with create-loan form, current-loans list region, global feedback region, Bootstrap stylesheet reference, and static asset references in `app/templates/index.html`.
- [X] T013 [US1] Add base compact operational layout, form, feedback, and current-loans list styling in `app/static/loan_website.css`.
- [X] T014 [US1] Implement initial current-loans load, create-loan submit, current-list rendering, success feedback, validation/duplicate feedback mapping, and failed-input preservation in `app/static/loan_website.js`.
- [X] T015 [US1] Run focused US1 tests with `.venv/bin/pytest tests/integration/test_loan_website.py tests/integration/test_create_loan_api.py` covering `app/routes.py`, `app/templates/index.html`, `app/static/loan_website.css`, and `app/static/loan_website.js`.

**Checkpoint**: User Story 1 is functional and independently testable as the MVP.

---

## Phase 4: User Story 2 - Find Current Loans (Priority: P2)

**Goal**: A user can search current loans by borrower name and look up one loan by loan ID from the website.

**Independent Test**: Seed several current loans, search by borrower name, look up by loan ID, and confirm match, empty-result, and not-found states.

### Tests for User Story 2 (REQUIRED)

- [X] T016 [US2] Add integration tests for borrower-search form, borrower-results region, loan-ID lookup form, lookup-result region, empty-state copy, and not-found copy in `tests/integration/test_loan_website.py`.
- [X] T017 [US2] Add integration tests that `app/static/loan_website.js` contains borrower-name search and loan-ID lookup API handling plus empty/not-found message mapping in `tests/integration/test_loan_website.py`.

### Implementation for User Story 2

- [X] T018 [US2] Add borrower-name search and loan-ID lookup sections with result regions in `app/templates/index.html`.
- [X] T019 [US2] Implement borrower-name search, no-match empty state, loan-ID lookup, and not-found feedback in `app/static/loan_website.js`.
- [X] T020 [US2] Add scannable result styling for borrower-search and lookup sections in `app/static/loan_website.css`.
- [X] T021 [US2] Run focused US2 tests with `.venv/bin/pytest tests/integration/test_loan_website.py tests/integration/test_borrower_name_lookup_api.py tests/integration/test_get_loan_api.py` covering `app/templates/index.html`, `app/static/loan_website.js`, and `app/static/loan_website.css`.

**Checkpoint**: User Story 2 is functional and independently testable.

---

## Phase 5: User Story 3 - Delete Current Loans (Priority: P3)

**Goal**: A user can delete a current loan by loan ID from the website and see visible state update after removal.

**Independent Test**: Create or seed a loan, delete it by loan ID, then confirm it no longer appears in current list, lookup, or borrower-search results.

### Tests for User Story 3 (REQUIRED)

- [X] T022 [US3] Add integration tests for delete-loan form, deleted-loan result region, deleted confirmation copy, and delete not-found copy in `tests/integration/test_loan_website.py`.
- [X] T023 [US3] Add integration tests that `app/static/loan_website.js` contains delete API handling, deleted-loan confirmation rendering, not-found mapping, and current-list refresh hooks in `tests/integration/test_loan_website.py`.

### Implementation for User Story 3

- [X] T024 [US3] Add delete-loan section and deleted-loan result region in `app/templates/index.html`.
- [X] T025 [US3] Implement delete submit, deleted-loan confirmation, delete not-found feedback, and current-list refresh after successful deletion in `app/static/loan_website.js`.
- [X] T026 [US3] Add delete and deleted-result styling in `app/static/loan_website.css`.
- [X] T027 [US3] Run focused US3 tests with `.venv/bin/pytest tests/integration/test_loan_website.py tests/integration/test_delete_loan_api.py` covering `app/templates/index.html`, `app/static/loan_website.js`, and `app/static/loan_website.css`.

**Checkpoint**: User Story 3 is functional and independently testable.

---

## Phase 6: User Story 4 - Use The Website Responsively With Clear Feedback (Priority: P4)

**Goal**: A reviewer can use the website at desktop and mobile widths and understand success, empty, validation, not-found, service-unavailable, and loading states.

**Independent Test**: Use the website at desktop and mobile widths, trigger the major success and failure states, and confirm controls and messages remain readable.

### Tests for User Story 4 (REQUIRED)

- [X] T028 [US4] Add integration tests for temporary-session note, service-unavailable feedback copy, loading/action-in-progress selectors, and accessible status regions in `tests/integration/test_loan_website.py`.
- [X] T029 [US4] Add integration tests that `app/static/loan_website.css` contains responsive layout rules, mobile-safe result selectors, and no-horizontal-overflow safeguards in `tests/integration/test_loan_website.py`.

### Implementation for User Story 4

- [X] T030 [US4] Add temporary-session note, shared status regions, loading markers, and retry-friendly form structure in `app/templates/index.html`.
- [X] T031 [US4] Implement shared action-state guard, service-unavailable handling, loading feedback, repeated-submit prevention, and retry-preserving failures in `app/static/loan_website.js`.
- [X] T032 [US4] Add responsive desktop/mobile layout rules that keep forms, buttons, result rows, and feedback readable without horizontal scrolling in `app/static/loan_website.css`.
- [X] T033 [US4] Run focused US4 tests with `.venv/bin/pytest tests/integration/test_loan_website.py tests/integration/test_health_api.py` covering `app/templates/index.html`, `app/static/loan_website.js`, and `app/static/loan_website.css`.

**Checkpoint**: User Story 4 is functional and independently testable.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Update documentation, validate contracts, and run final regression coverage.

- [X] T034 [P] Update `README.md` scope, run instructions, website demo flow, responsive check, and latest coverage result.
- [X] T035 [P] Update documentation smoke expectations for the website route and `specs/006-loan-website/quickstart.md` in `tests/integration/test_documentation_examples.py`.
- [X] T036 [P] Review `specs/006-loan-website/quickstart.md` and `specs/006-loan-website/contracts/ui-contract.md` against the implemented page, selectors, and messages.
- [X] T037 Add documented browser-responsive validation notes for any behaviour not covered by pytest in `README.md` and `specs/006-loan-website/quickstart.md`.
- [X] T038 Run all integration tests with `.venv/bin/pytest tests/integration` and fix website/API regressions in `app/routes.py`, `app/templates/index.html`, `app/static/loan_website.js`, `app/static/loan_website.css`, or `tests/integration/`.
- [X] T039 Run the full coverage gate with `.venv/bin/pytest --cov=app --cov-report=term-missing --cov-fail-under=80` and update `README.md`.
- [X] T040 Validate the local website quickstart against `http://127.0.0.1:5000/`, `README.md`, and `specs/006-loan-website/quickstart.md`.
- [X] T041 Perform final diff cleanup for unrelated edits in `app/routes.py`, `app/templates/index.html`, `app/static/loan_website.js`, `app/static/loan_website.css`, `README.md`, and `tests/`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks user story implementation.
- **User Story 1 (Phase 3)**: Depends on Foundational completion and is the MVP.
- **User Story 2 (Phase 4)**: Depends on the shared page/assets from US1.
- **User Story 3 (Phase 5)**: Depends on the shared page/assets from US1 and can be validated independently with seeded loans.
- **User Story 4 (Phase 6)**: Depends on the visible page workflows from US1-US3.
- **Polish (Phase 7)**: Depends on the desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: MVP. Delivers page entry, create form, current list, and feedback foundation.
- **User Story 2 (P2)**: Adds find workflows to the existing page.
- **User Story 3 (P3)**: Adds delete workflow to the existing page.
- **User Story 4 (P4)**: Hardens responsive layout and cross-workflow feedback states.

### Within Each User Story

- Write tests before implementation and confirm they fail.
- Template regions before JavaScript handlers when both are missing.
- JavaScript behaviour before final visual polish for that story.
- Focused story tests before moving to the next story.

## Parallel Opportunities

- **Setup**: T002, T003, T004, and T005 can run in parallel.
- **Foundational**: T007 and T008 can run in parallel.
- **Polish**: T034, T035, and T036 can run in parallel because they touch different files.
- Most story tasks intentionally avoid `[P]` because they coordinate through the same `tests/integration/test_loan_website.py`, `app/templates/index.html`, `app/static/loan_website.js`, and `app/static/loan_website.css` files.

## Parallel Example: Setup

```bash
Task: "Confirm no new Node, Angular, Auth0, persistence, registry, Kubernetes, or cloud dependency is introduced in requirements.txt and specs/006-loan-website/plan.md"
Task: "Create or verify the planned website file locations for app/templates/index.html, app/static/loan_website.css, and app/static/loan_website.js"
Task: "Confirm repository guidance points to specs/006-loan-website/plan.md in AGENTS.md"
Task: "Review the browser entry point, page regions, and existing API dependency contract in specs/006-loan-website/contracts/ui-contract.md"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational checks.
3. Complete Phase 3: User Story 1.
4. Stop and validate the website can load, create a loan, and show the current list.

### Incremental Delivery

1. Complete Setup and Foundational checks.
2. Add US1 create/list shell and validate it independently.
3. Add US2 search/lookup and validate it independently.
4. Add US3 deletion and validate it independently.
5. Add US4 responsive/error-state hardening.
6. Complete documentation, regression, quickstart, and coverage validation.

### Validation Targets

- `.venv/bin/pytest tests/integration/test_loan_website.py`
- `.venv/bin/pytest tests/integration`
- `.venv/bin/pytest --cov=app --cov-report=term-missing --cov-fail-under=80`
- Local browser validation at `http://127.0.0.1:5000/`

## Notes

- Keep the website as a single local Flask-rendered page.
- Reuse existing JSON API endpoints for all loan operations.
- Do not add Angular, Node build tooling, Auth0, persistence, public exposure, container registry work, Kubernetes, Helm, or cloud infrastructure in this slice.
- Keep UI compact and operational; no landing page or marketing hero.
