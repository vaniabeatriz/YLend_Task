# Feature Specification: Auth0 Authentication

**Feature Branch**: `008-auth0-auth`  
**Created**: 2026-05-12  
**Status**: Draft  
**Input**: User description: "Add Auth0 authentication to protect the loan website and loan API endpoints so only authenticated users can create, list, search, look up, and delete loans. Keep durable persistence, public deployment, container registry, Kubernetes, and cloud infrastructure out of scope for this slice."

## Clarifications

### Session 2026-05-12

- Q: How should protected API endpoints recognize Auth0 authentication? → A: Auth0 JWT bearer access tokens.
- Q: How should Auth0 be handled in automated tests and local demo? → A: Mocked tokens/sessions in tests; real Auth0 for manual demo.
- Q: What should protected API endpoints do when API authentication is missing or invalid? → A: Return 401 JSON authentication error.
- Q: What should the application do when Auth0 configuration is missing? → A: Start app; show setup errors for auth flows.
- Q: What session-cookie security controls are required in this slice? → A: HttpOnly, SameSite=Lax, Secure when HTTPS; no separate CSRF token.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Sign In Before Using Loan Workflows (Priority: P1)

A reviewer must sign in before accessing the loan website workflows.

**Why this priority**: The highest-value outcome is preventing unauthenticated
browser access to loan operations while preserving the existing local website
experience for authenticated users.

**Independent Test**: Open the website while signed out and confirm the user is
not shown loan workflow controls until sign-in succeeds; then sign in and
confirm the loan action menu and forms become available.

**Acceptance Scenarios**:

1. **Given** a user is not signed in, **When** the user opens the loan website, **Then** the website prevents access to loan workflows and presents a clear sign-in path.
2. **Given** a user completes sign-in successfully, **When** the user returns to the website, **Then** the website shows the authenticated experience with create, list, search, lookup, and delete actions.
3. **Given** a signed-in user chooses to sign out, **When** sign-out completes, **Then** the website no longer shows loan workflow controls until the user signs in again.

---

### User Story 2 - Protect Loan API Operations (Priority: P2)

An API caller must provide a valid Auth0 JWT bearer access token before
performing any loan operation.

**Why this priority**: The website cannot be the only protection layer; direct
calls to loan endpoints must also prevent unauthenticated access.

**Independent Test**: Call each loan endpoint without a valid Auth0 bearer
access token and confirm the response returns a JSON authentication error
without returning loan data or performing the action; then call the same
endpoints with a valid Auth0 bearer access token and confirm existing loan
behaviours still work.

**Acceptance Scenarios**:

1. **Given** a request has no valid Auth0 bearer access token, **When** the caller requests loan creation, full listing, borrower-name search, loan ID lookup, or deletion, **Then** the system returns a 401 JSON authentication error and does not perform the requested loan action.
2. **Given** a request has a valid Auth0 bearer access token, **When** the caller performs create, list, borrower-name search, loan ID lookup, or delete, **Then** the existing success, validation, duplicate, empty, and not-found behaviours are preserved.
3. **Given** an authenticated request contains invalid loan input, **When** the caller submits the request, **Then** authentication succeeds and the existing validation response is returned.

---

### User Story 3 - Handle Authentication Errors Clearly (Priority: P3)

A reviewer can understand and recover from expired, invalid, missing, or
misconfigured authentication states during local validation.

**Why this priority**: Authentication introduces new failure states that must be
clear enough for local review and debugging without hiding the existing loan
workflow errors.

**Independent Test**: Exercise missing, expired, invalid, and unavailable
authentication states and confirm the user or caller receives clear feedback
without accidentally exposing loan data.

**Acceptance Scenarios**:

1. **Given** a signed-in user's authentication expires, **When** the user attempts a loan action, **Then** the system denies the action and provides a clear path to sign in again.
2. **Given** an API request includes invalid bearer-token authentication, **When** the caller requests a loan operation, **Then** the system returns a 401 JSON authentication error without creating, returning, updating, or deleting loan data.
3. **Given** authentication settings are missing or invalid in local setup, **When** the application starts, **Then** startup succeeds and unauthenticated operational checks remain available.
4. **Given** authentication settings are missing or invalid in local setup, **When** sign-in or a protected loan flow is used, **Then** the system exposes a clear setup/configuration error to the reviewer.

### Edge Cases

- User opens the website without an active sign-in session.
- User signs in successfully but returns to the website with a stale or expired session.
- User signs out and then uses the browser back button.
- API caller omits authentication.
- API caller sends a missing, expired, malformed, wrong-audience, or otherwise invalid Auth0 bearer access token.
- Authenticated caller sends invalid loan input.
- Authentication provider is unreachable during sign-in.
- Required local authentication configuration is missing or incorrect.
- Health checks are requested while no user is signed in.
- Application starts without Auth0 configuration and a reviewer opens sign-in or a protected loan flow.
- Website authentication session cookies are used over local HTTP and HTTPS-capable environments.
- Durable persistence, public deployment, registry, Kubernetes, and cloud infrastructure remain outside this slice.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The website MUST prevent unauthenticated users from accessing create, list, borrower-name search, loan ID lookup, and delete workflows.
- **FR-002**: The website MUST provide a clear sign-in action when a user is not authenticated.
- **FR-003**: The website MUST provide a clear sign-out action when a user is authenticated.
- **FR-004**: After successful sign-in, users MUST be able to use the existing create, list, borrower-name search, loan ID lookup, and delete workflows.
- **FR-005**: Loan API operations MUST reject requests without a valid Auth0 bearer access token for create, list, borrower-name search, loan ID lookup, and deletion by returning a 401 JSON authentication error.
- **FR-006**: Loan API operations MUST reject missing, expired, malformed, wrong-audience, or otherwise invalid Auth0 bearer access tokens without performing the requested loan action.
- **FR-007**: Authenticated API requests MUST preserve existing success and error behaviours for validation, duplicate loan ID, empty results, not-found lookup, and not-found deletion.
- **FR-008**: The system MUST keep the health check available for local operational validation without requiring user sign-in.
- **FR-009**: Authentication failure responses for protected API requests MUST return a 401 JSON authentication error and must not expose loan records.
- **FR-010**: The website MUST show clear recovery guidance when sign-in is required, has expired, or cannot be completed.
- **FR-011**: Documentation MUST explain required local Auth0 setup for manual demo, run, test, and demo steps for website and API usage.
- **FR-012**: Automated tests MUST cover authenticated and unauthenticated website/API access paths using local mocked sessions and bearer-token verification and keep statement coverage at or above 80%.
- **FR-013**: The feature MUST keep durable persistence, public deployment, container registry, Kubernetes, and cloud infrastructure out of scope.
- **FR-014**: The feature MUST require Auth0 JWT bearer access tokens for protected loan API endpoints and MUST NOT rely solely on website session cookies for API protection.
- **FR-015**: The application MUST start without local Auth0 configuration, keep unauthenticated operational checks available, and show a clear setup error only when sign-in or protected loan flows require Auth0.
- **FR-016**: Authentication session cookies MUST use HttpOnly and SameSite=Lax, MUST use Secure when served over HTTPS, and MUST NOT add separate CSRF token checks in this slice.

### Key Entities *(include if feature involves data)*

- **Authenticated User**: A signed-in person who can access the website and perform loan operations.
- **Authentication Session**: The website session cookie created after successful sign-in and used to show or hide loan workflows.
- **Auth0 Access Token**: A JWT bearer access token issued by Auth0 and sent to protected loan API endpoints in the `Authorization` header.
- **Protected Loan Operation**: Any create, list, borrower-name search, loan ID lookup, or delete action requiring a valid Auth0 bearer access token.
- **Authentication Failure**: A denied access state caused by missing, expired, malformed, wrong-audience, invalid, or misconfigured Auth0 authentication.
- **Session Cookie Security**: The cookie protection settings applied to authentication sessions: HttpOnly, SameSite=Lax, and Secure when served over HTTPS.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A signed-out reviewer cannot access website loan workflows and sees a sign-in path within 5 seconds of opening the website.
- **SC-002**: A signed-in reviewer can complete create, list, borrower-name search, loan ID lookup, and delete workflows from the website in under 7 minutes.
- **SC-003**: Every protected loan endpoint returns a 401 JSON authentication error for unauthenticated requests with no loan data returned.
- **SC-004**: Every protected loan endpoint preserves the existing successful behaviour when called with a valid Auth0 bearer access token.
- **SC-005**: Expired or invalid authentication states show clear recovery guidance and do not create, return, or delete loans.
- **SC-006**: Reviewer can run the authentication-enabled website, service, and test suite from documentation without missing setup steps; automated tests do not require live Auth0 credentials, and missing local Auth0 configuration does not prevent application startup.
- **SC-007**: Test command reports at least 80% statement coverage for implemented behaviour.
- **SC-008**: The authentication scope, trade-offs, and out-of-scope deployment boundaries can be explained in under 40 minutes.
- **SC-009**: Session-cookie settings are documented and covered by automated tests or configuration assertions without adding CSRF token handling.

## Assumptions

- Auth0 is the identity provider for this slice because it is explicitly requested.
- All authenticated users have the same loan-management permissions; roles and per-user authorization rules are out of scope.
- Protected loan API endpoints require Auth0 JWT bearer access tokens; the website sends the access token in the `Authorization` header when calling protected loan APIs.
- The existing loan workflows and response shapes remain the source of truth once authentication succeeds.
- Automated tests use local mocked authenticated and unauthenticated sessions and bearer-token verification so they do not depend on a live Auth0 tenant, network access, or test credentials.
- Manual local demo uses real Auth0 configuration when the reviewer wants to exercise the sign-in and sign-out flow end to end.
- Missing Auth0 configuration is handled at sign-in/protected-flow time instead of failing application startup.
- SameSite=Lax is sufficient CSRF protection for this local same-origin slice; explicit CSRF tokens are deferred.
- Health checks remain available without sign-in so local operational validation stays simple.
- Durable persistence, public deployment, container registry, Kubernetes, and cloud infrastructure are deferred to later slices.
