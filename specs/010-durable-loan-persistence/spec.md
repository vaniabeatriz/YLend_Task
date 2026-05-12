# Feature Specification: Durable Loan Persistence

**Feature Branch**: `010-durable-loan-persistence`  
**Created**: 2026-05-12  
**Status**: Draft  
**Input**: User description: "Add durable loan persistence so created loans survive Flask app restarts using a local database-backed repository. Preserve the existing authenticated create, list, borrower-name search, loanId lookup, and delete behaviours for the API and website. Include schema initialization and automated tests proving loans persist across app/service restarts. Keep public deployment, container registry, Kubernetes, cloud infrastructure, Auth0 changes, roles, and per-user loan ownership out of scope for this slice."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve Loans After Restart (Priority: P1)

An authenticated reviewer can create a loan, restart the application, and still
retrieve that loan through the existing loan workflows.

**Why this priority**: This is the core value of the feature: loan records must
survive beyond a single running application process.

**Independent Test**: Create a loan as an authenticated user, simulate an
application restart, then verify the same loan can be found through full
listing, borrower-name search, and loan ID lookup.

**Acceptance Scenarios**:

1. **Given** an authenticated reviewer creates loan `LN-001`, **When** the application is restarted, **Then** `LN-001` is still returned by the loan ID lookup.
2. **Given** an authenticated reviewer creates loan `LN-001` for borrower `Jane Smith`, **When** the application is restarted, **Then** full listing and borrower-name search still include `LN-001`.
3. **Given** no loans have been created, **When** the application starts, **Then** listing and borrower-name search return empty loan collections.

---

### User Story 2 - Preserve Existing Loan Behaviour (Priority: P2)

Authenticated callers continue to use the existing create, list, borrower-name
search, loan ID lookup, and delete behaviours without response-shape or user
workflow regressions.

**Why this priority**: Persistence must improve data durability without changing
the contract reviewers already validated in earlier slices.

**Independent Test**: Run the existing authenticated API and website workflows
against persisted data and confirm success, validation, duplicate, empty,
not-found, and deletion behaviours remain unchanged.

**Acceptance Scenarios**:

1. **Given** loan `LN-001` already exists from a previous application run, **When** an authenticated caller creates `LN-001` again, **Then** the existing duplicate-loan response is returned.
2. **Given** loan `LN-001` exists, **When** an authenticated caller deletes `LN-001`, **Then** the deleted loan record is returned and future listing, search, and lookup workflows no longer include it.
3. **Given** a create request has invalid loan input, **When** an authenticated caller submits it, **Then** the existing validation response is returned and no durable record is created.

---

### User Story 3 - Start Cleanly In Local Demo Environments (Priority: P3)

A reviewer can start the application in a fresh local environment and use loan
workflows without manual storage preparation.

**Why this priority**: Durable storage adds setup risk; the local technical test
must remain easy to run and explain.

**Independent Test**: Start the application with no prior loan storage, confirm
loan workflows show an empty state, create a loan, restart, and confirm the
record remains available.

**Acceptance Scenarios**:

1. **Given** no durable loan storage exists, **When** the application starts, **Then** storage is prepared automatically and loan listing returns an empty collection.
2. **Given** durable storage already contains loans, **When** the application starts, **Then** those loans are available before any new create request is made.
3. **Given** durable storage cannot be prepared or accessed, **When** a protected loan workflow is attempted, **Then** the reviewer receives a clear service error without losing already persisted loan data.

### Edge Cases

- Application starts with no prior loan records.
- Application restarts after one or more loans have been created.
- Application restarts after a loan has been deleted.
- A duplicate loan ID is submitted after the original loan was created in a previous run.
- Invalid create input is submitted and must not leave a partial durable record.
- Borrower-name search is performed after restart for both matching and non-matching borrowers.
- Loan ID lookup is performed after restart for both existing and missing loan IDs.
- Authenticated and unauthenticated access rules remain unchanged.
- Durable storage is unavailable or cannot be prepared during local use.
- Public deployment, registry, Kubernetes, cloud infrastructure, roles, and per-user ownership remain outside this slice.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST keep created loan records available after the application is stopped and started again.
- **FR-002**: The system MUST prepare empty durable loan storage automatically when no prior loan records exist.
- **FR-003**: The system MUST load existing durable loan records before serving loan create, list, search, lookup, or delete workflows.
- **FR-004**: Authenticated create-loan behaviour MUST preserve the existing success response, validation response, duplicate-loan response, normalization rules, and amount handling.
- **FR-005**: Authenticated full listing MUST return all durable current loans and MUST return an empty collection when no current loans exist.
- **FR-006**: Authenticated borrower-name search MUST preserve existing exact-match, trimming, empty-result, and blank-query behaviours across restarts.
- **FR-007**: Authenticated loan ID lookup MUST preserve existing found and not-found behaviours across restarts.
- **FR-008**: Authenticated loan deletion MUST remove the durable loan record so it remains absent after application restart.
- **FR-009**: Duplicate-loan checks MUST include loans created in previous application runs.
- **FR-010**: Failed validation, duplicate, unauthenticated, and invalid-authentication requests MUST NOT create, replace, or delete durable loan records.
- **FR-011**: Existing website workflows MUST continue to display success, empty, validation, duplicate, not-found, deletion, authentication, and service-unavailable states consistently after persistence is added.
- **FR-012**: Existing Auth0 authentication behaviour MUST remain unchanged for website access and protected loan API endpoints.
- **FR-013**: Documentation MUST explain setup, run, test, and demo steps for durable loan persistence, including how to verify records survive restart.
- **FR-014**: Automated tests MUST prove loan persistence across separate application/service instances and keep statement coverage at or above 80%.
- **FR-015**: The feature MUST keep public deployment, container registry, Kubernetes, cloud infrastructure, Auth0 changes, roles, and per-user loan ownership out of scope.

### Key Entities *(include if feature involves data)*

- **Durable Loan Record**: A current loan record that remains available after the application restarts. It includes the existing loan ID, borrower name, funding amount, and repayment amount.
- **Loan Collection**: The set of durable current loan records visible through full listing and borrower-name search.
- **Persistence State**: The local stored state used to determine whether the application starts with existing loans or an empty collection.
- **Storage Preparation Result**: The outcome of preparing local durable loan storage for use, either ready for workflows or unavailable with a clear service error.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After an authenticated reviewer creates a loan and restarts the application, the reviewer can retrieve that loan by loan ID, full listing, and borrower-name search within 2 seconds per action in local usage.
- **SC-002**: A duplicate create request for a loan ID created before restart returns the existing duplicate-loan response 100% of the time in automated tests.
- **SC-003**: A deleted loan remains absent from loan ID lookup, full listing, and borrower-name search after restart in automated tests.
- **SC-004**: Existing authenticated loan workflows continue to pass their current success and error assertions without response-shape regressions.
- **SC-005**: A fresh local start with no prior loan records requires no manual data preparation and returns an empty loan collection.
- **SC-006**: Reviewer can run the persistence-enabled website, service, and test suite from documentation without missing setup steps.
- **SC-007**: Automated test command reports at least 80% statement coverage.
- **SC-008**: The persistence scope, restart behaviour, and out-of-scope deployment boundaries can be explained in under 40 minutes.

## Assumptions

- The existing authenticated loan workflows and response shapes remain the source of truth.
- Durable records are shared by all authenticated users in this slice; roles and per-user loan ownership are deferred.
- Local durable storage is sufficient for this technical-test slice; public deployment and managed infrastructure are deferred.
- Startup should create or prepare required local storage automatically rather than requiring reviewers to run a separate setup command.
- Restart validation may be proven with separate application/service instances in automated tests rather than a live manual server restart.
- Existing Auth0 sign-in, access-token validation, session handling, and authentication errors are not changed in this slice.
- The solution must remain small enough to run, test, and explain within the existing project workflow.
