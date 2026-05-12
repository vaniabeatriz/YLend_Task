# Tasks: Auth0 Authentication

**Input**: Design documents from `/specs/007-auth0-auth/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are REQUIRED by FR-012. Write pytest coverage for each user
story before implementation and keep the final coverage gate at 80% or higher.

**Organization**: Tasks are grouped by user story so each story can be
implemented and tested independently after the shared foundation is complete.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and does not
  depend on incomplete tasks in the same phase.
- **[Story]**: User story label for story phases only.
- Every task includes exact file paths.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare dependencies, configuration conventions, and test helpers.

- [X] T001 Update Auth0 dependencies in `requirements.txt` with Authlib, PyJWT crypto support, and python-dotenv.
- [X] T002 [P] Add Auth0 environment variable setup notes to `README.md`.
- [X] T003 [P] Add mocked Auth0 session and bearer-token helper fixtures to `tests/conftest.py`.
- [X] T004 [P] Confirm local Auth0 secrets stay ignored by documenting `.env` handling in `.gitignore`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared auth configuration, session cookie settings, and
error primitives before user stories are implemented.

**CRITICAL**: No user story work should begin until this phase is complete.

- [X] T005 Create `app/auth.py` with `AuthConfig`, `AuthError`, `AuthSetupError`, and stable auth error codes.
- [X] T006 Configure `.env` loading, `SECRET_KEY`, and Auth0 defaults in `app/__init__.py`.
- [X] T007 Configure Flask session cookie settings `SESSION_COOKIE_HTTPONLY`, `SESSION_COOKIE_SAMESITE`, and HTTPS-aware `SESSION_COOKIE_SECURE` in `app/__init__.py`.
- [X] T008 Add reusable auth JSON error response helpers in `app/auth.py`.
- [X] T009 Add injectable test auth configuration and fake token verifier hooks in `app/auth.py`.
- [X] T010 Update Flask app factory test configuration support for auth overrides in `app/__init__.py`.
- [X] T011 Add baseline auth configuration unit tests in `tests/unit/test_auth.py`.

**Checkpoint**: Auth foundation is ready; user story implementation can begin.

---

## Phase 3: User Story 1 - Sign In Before Using Loan Workflows (Priority: P1) MVP

**Goal**: Signed-out reviewers see a sign-in path and cannot access loan
workflows; signed-in reviewers see the loan action menu and can sign out.

**Independent Test**: Open the website with no session and verify loan workflow
controls are hidden; mock a signed-in session and verify the action menu/forms
become available; sign out and verify workflows are hidden again.

### Tests for User Story 1

- [X] T012 [P] [US1] Add auth route tests for signed-out status, mocked signed-in status, login redirect, callback success, and logout in `tests/integration/test_auth_routes.py`.
- [X] T013 [P] [US1] Add website rendering tests for signed-out hidden workflows and signed-in visible actions in `tests/integration/test_loan_website.py`.

### Implementation for User Story 1

- [X] T014 [US1] Implement Auth0 OAuth client registration and login/callback/logout/session helpers in `app/auth.py`.
- [X] T015 [US1] Add `/login`, `/callback`, `/logout`, and `/auth/status` routes in `app/routes.py`.
- [X] T016 [US1] Update `app/templates/index.html` with signed-out sign-in controls, signed-in user status, sign-out control, and auth feedback regions.
- [X] T017 [US1] Update `app/static/loan_website.js` to load `/auth/status`, cache authenticated state, and hide/show workflow sections by auth state.
- [X] T018 [US1] Update `app/static/loan_website.css` for auth controls, signed-out state, and responsive sign-in/status layout.
- [X] T019 [US1] Ensure browser back/sign-out state hides workflow sections by resetting menu state in `app/static/loan_website.js`.
- [X] T020 [US1] Run targeted US1 tests and fix failures in `tests/integration/test_auth_routes.py` and `tests/integration/test_loan_website.py`.

**Checkpoint**: User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - Protect Loan API Operations (Priority: P2)

**Goal**: All loan API operations require valid Auth0 JWT bearer access tokens
and preserve existing loan behaviours once authentication succeeds.

**Independent Test**: Call every loan endpoint without a token and with invalid
tokens and verify `401` JSON with no loan data; call the same endpoints with a
mocked valid token and verify create/list/search/lookup/delete behaviours remain
unchanged.

### Tests for User Story 2

- [X] T021 [P] [US2] Add unit tests for Authorization header parsing and token verifier outcomes in `tests/unit/test_auth.py`.
- [X] T022 [US2] Add integration tests for missing and invalid bearer tokens on `POST /loans`, `GET /loans`, `GET /loans?borrowerName=`, `GET /loans/<loanId>`, and `DELETE /loans/<loanId>` in `tests/integration/test_auth_protected_api.py`.
- [X] T023 [US2] Add integration tests for authenticated create/list/search/lookup/delete success and existing validation/not-found/duplicate behaviours in `tests/integration/test_auth_protected_api.py`.

### Implementation for User Story 2

- [X] T024 [US2] Implement bearer-token extraction and malformed Authorization header handling in `app/auth.py`.
- [X] T025 [US2] Implement Auth0 JWKS/RS256 issuer/audience/expiry token verification with injectable verifier support in `app/auth.py`.
- [X] T026 [US2] Add `require_auth` decorator in `app/auth.py` that returns `401` JSON authentication errors without exposing loan records.
- [X] T027 [US2] Apply `require_auth` to `POST /loans`, `GET /loans`, `GET /loans/<path:loan_id>`, and `DELETE /loans/<path:loan_id>` in `app/routes.py`.
- [X] T028 [US2] Keep `GET /` and `GET /health` public while protecting only loan endpoints in `app/routes.py`.
- [X] T029 [US2] Update `app/static/loan_website.js` to send `Authorization: Bearer <accessToken>` on loan API requests and show authentication feedback for `401` responses.
- [X] T030 [US2] Run targeted US2 tests and fix failures in `tests/unit/test_auth.py` and `tests/integration/test_auth_protected_api.py`.

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Handle Authentication Errors Clearly (Priority: P3)

**Goal**: Expired, invalid, unavailable, and misconfigured authentication states
show clear recovery guidance without exposing or mutating loan data.

**Independent Test**: Start the app without Auth0 config and verify `/health`
and `/` work while sign-in/protected flows show setup guidance; simulate
expired/wrong-audience/invalid tokens and verify `401` JSON plus website
re-authentication guidance.

### Tests for User Story 3

- [X] T031 [P] [US3] Add tests for app startup, `/health`, `/`, `/login`, and `/auth/status` when Auth0 config is missing in `tests/integration/test_auth_routes.py`.
- [X] T032 [P] [US3] Add unit tests for expired, wrong-audience, wrong-issuer, malformed, and JWKS-missing token failures in `tests/unit/test_auth.py`.
- [X] T033 [P] [US3] Add website tests for setup-error and re-authentication feedback states in `tests/integration/test_loan_website.py`.

### Implementation for User Story 3

- [X] T034 [US3] Implement missing Auth0 configuration detection and safe setup-error messages in `app/auth.py`.
- [X] T035 [US3] Update `/login`, `/callback`, and `/auth/status` error handling for setup, provider, callback, and expired-session states in `app/routes.py`.
- [X] T036 [US3] Update `app/static/loan_website.js` to show setup-error, expired-session, invalid-token, and re-authentication guidance without stale success states.
- [X] T037 [US3] Update `app/templates/index.html` with accessible setup-error and re-authentication feedback containers.
- [X] T038 [US3] Update `app/static/loan_website.css` for setup-error and re-authentication feedback states.
- [X] T039 [US3] Add session cookie configuration assertions for HttpOnly, SameSite=Lax, and HTTPS Secure behaviour in `tests/unit/test_auth.py`.
- [X] T040 [US3] Run targeted US3 tests and fix failures in `tests/integration/test_auth_routes.py`, `tests/unit/test_auth.py`, and `tests/integration/test_loan_website.py`.

**Checkpoint**: All user stories are independently functional.

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, regression coverage, and final verification across
the complete feature.

- [X] T041 [P] Update Auth0 setup, run, test, website demo, and protected API demo documentation in `README.md`.
- [X] T042 [P] Update documentation example tests for authenticated API examples in `tests/integration/test_documentation_examples.py`.
- [X] T043 [P] Update final Auth0 demo notes and any implementation-specific command changes in `specs/007-auth0-auth/quickstart.md`.
- [X] T044 Review OpenAPI and UI/auth contracts against implemented routes in `specs/007-auth0-auth/contracts/openapi.yaml` and `specs/007-auth0-auth/contracts/ui-auth-contract.md`.
- [X] T045 Run `pytest --cov=app --cov-report=term-missing --cov-fail-under=80` and fix coverage gaps in `app/` and `tests/`.
- [X] T046 Perform final security review of JWT errors, setup messages, and token handling in `app/auth.py` and `app/static/loan_website.js`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup** has no dependencies.
- **Phase 2: Foundational** depends on Setup and blocks all user stories.
- **Phase 3: US1** depends on Foundational.
- **Phase 4: US2** depends on Foundational and can be developed independently
  from US1, but the full website demo needs US1 plus US2.
- **Phase 5: US3** depends on Foundational and can be developed independently
  after the base auth helpers exist.
- **Final Phase** depends on the desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: No dependency on US2/US3 after Foundational; MVP for website
  sign-in gating.
- **US2 (P2)**: No dependency on US1 for direct API tests after Foundational;
  integrates with US1 for browser API calls.
- **US3 (P3)**: Uses auth primitives from Foundational and may build on US1/US2
  UI/API failure surfaces, but remains independently testable.

### Within Each User Story

- Write tests before implementation tasks in that story.
- Auth helpers before routes.
- Routes before template/static integration.
- Static integration before targeted story validation.

---

## Parallel Opportunities

- T002, T003, and T004 can run in parallel after T001 is understood.
- T012 and T013 can run in parallel for US1 tests.
- T021 can run in parallel with T022/T023 planning, but T022 and T023 share the
  same file and should be sequenced.
- T031, T032, and T033 can run in parallel for US3 tests.
- T041, T042, and T043 can run in parallel during the final phase.

## Parallel Example: User Story 1

```text
Task: "Add auth route tests for signed-out status, mocked signed-in status, login redirect, callback success, and logout in tests/integration/test_auth_routes.py"
Task: "Add website rendering tests for signed-out hidden workflows and signed-in visible actions in tests/integration/test_loan_website.py"
```

## Parallel Example: User Story 2

```text
Task: "Add unit tests for Authorization header parsing and token verifier outcomes in tests/unit/test_auth.py"
Task: "Add integration tests for missing and invalid bearer tokens on protected loan endpoints in tests/integration/test_auth_protected_api.py"
```

## Parallel Example: User Story 3

```text
Task: "Add tests for app startup, health, website, login, and auth status when Auth0 config is missing in tests/integration/test_auth_routes.py"
Task: "Add unit tests for expired, wrong-audience, wrong-issuer, malformed, and JWKS-missing token failures in tests/unit/test_auth.py"
Task: "Add website tests for setup-error and re-authentication feedback states in tests/integration/test_loan_website.py"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: US1.
4. Validate website sign-in gating with mocked sessions.

### Incremental Delivery

1. Add US1 for signed-in/signed-out website states.
2. Add US2 for bearer-token API protection and browser API calls.
3. Add US3 for setup, expired, invalid-token, and recovery states.
4. Finish documentation and coverage verification.

### Single-Developer Strategy

Work sequentially in priority order: Setup -> Foundational -> US1 -> US2 -> US3
-> Polish. Stop at each checkpoint and run the targeted tests before continuing.

## Notes

- All protected loan endpoints must preserve existing validation, duplicate,
  empty, not-found, and deletion behaviours after authentication succeeds.
- Automated tests must not require a live Auth0 tenant, network access, or
  committed credentials.
- Keep durable persistence, public deployment, container registry, Kubernetes,
  and cloud infrastructure out of scope.
