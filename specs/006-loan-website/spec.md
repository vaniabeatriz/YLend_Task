# Feature Specification: Loan Website

**Feature Branch**: `006-loan-website`  
**Created**: 2026-05-12  
**Status**: Draft  
**Input**: User description: "Add a single-page website that consumes the existing loan API and lets users create loans, list all current loans, search loans by borrowerName, look up a loan by loanId, and delete a loan by loanId, with responsive UI and meaningful success/error states. Keep Auth0, persistence, public deployment, container registry, Kubernetes, and cloud infrastructure out of scope for this slice."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create And Review Current Loans (Priority: P1)

A user can create a loan from the website and immediately review the current
loan collection on the same page.

**Why this priority**: The website must first prove that users can perform the
primary loan-management workflow without leaving the page.

**Independent Test**: Open the website, create a valid loan, and confirm the
loan appears in the current loan list with the submitted details.

**Acceptance Scenarios**:

1. **Given** the website is open and no loan has been created during the current session, **When** the user submits valid loan details, **Then** the website confirms the loan was created and shows the new loan in the current loan list.
2. **Given** a loan already exists for a loan ID, **When** the user submits another loan with the same case-sensitive loan ID after trimming surrounding whitespace, **Then** the website keeps the user on the page and shows a clear duplicate-loan message.
3. **Given** one or more loan fields are missing, blank, or invalid, **When** the user submits the create form, **Then** the website shows field-level guidance without clearing valid entered values.

---

### User Story 2 - Find Current Loans (Priority: P2)

A user can find current loans by borrower name or by loan ID from the website.

**Why this priority**: Users need to inspect existing loans without reading raw
responses or using separate tools.

**Independent Test**: Seed several current loans, search by borrower name, look
up one loan by loan ID, and confirm matching and no-match states are shown
clearly.

**Acceptance Scenarios**:

1. **Given** multiple current loans exist, **When** the user searches by a borrower name, **Then** the website shows only current loans for that borrower.
2. **Given** no current loan matches the searched borrower name, **When** the user submits the search, **Then** the website shows an empty-state message instead of an error.
3. **Given** a current loan exists for a loan ID, **When** the user looks up that loan ID, **Then** the website shows that loan's details.
4. **Given** no current loan exists for a loan ID, **When** the user looks up that loan ID, **Then** the website shows a clear not-found message.

---

### User Story 3 - Delete Current Loans (Priority: P3)

A user can delete a current loan by loan ID from the website and see the page
state update to reflect the removal.

**Why this priority**: The website must expose the full current loan lifecycle
that already exists in the loan-management service.

**Independent Test**: Create or seed a loan, delete it by loan ID from the
website, then confirm it no longer appears in lookup, borrower search, or the
current loan list.

**Acceptance Scenarios**:

1. **Given** a current loan exists for a loan ID, **When** the user deletes that loan ID, **Then** the website confirms which loan was deleted and removes it from visible loan results.
2. **Given** a loan was already deleted, **When** the user attempts to delete the same loan ID again, **Then** the website shows a clear not-found message and leaves other visible loans unchanged.
3. **Given** the supplied loan ID has surrounding whitespace, **When** the user deletes the loan, **Then** matching ignores the surrounding whitespace while preserving case-sensitive identity.

---

### User Story 4 - Use The Website Responsively With Clear Feedback (Priority: P4)

A reviewer can use the website on desktop and mobile-sized screens and
understand success, empty, validation, not-found, and service-unavailable
states.

**Why this priority**: The website is a user-facing deliverable and must be
usable enough to demonstrate the technical task without hidden instructions.

**Independent Test**: Use the website at desktop and mobile widths, trigger each
major success and error state, and confirm controls remain usable and messages
are understandable.

**Acceptance Scenarios**:

1. **Given** the website is viewed on a narrow screen, **When** the user creates, searches, looks up, or deletes loans, **Then** controls and results remain readable without horizontal scrolling.
2. **Given** the loan-management service cannot be reached, **When** the user attempts an action, **Then** the website shows a clear service-unavailable message and keeps the user's entered values available for retry.
3. **Given** an action completes successfully, **When** the website updates the screen, **Then** the success message identifies the completed action and the affected loan when applicable.

### Edge Cases

- Required form fields are blank or whitespace-only.
- Funding amount or repayment amount is zero, negative, missing, or not a valid amount.
- Loan IDs or borrower names include leading or trailing whitespace.
- Loan IDs differ only by letter case.
- Borrower-name search returns no current loans.
- Loan ID lookup or deletion targets a loan that does not exist or was already deleted.
- Current loans disappear after the service restarts.
- The loan-management service is unavailable or returns an unexpected response.
- The page is used on a narrow viewport where tables, forms, and messages could otherwise overflow.
- A user submits the same action repeatedly before the previous action has visibly completed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The website MUST provide one page from which users can create, list, search, look up, and delete current loans.
- **FR-002**: The website MUST allow users to create a loan with loan ID, borrower name, funding amount, and repayment amount.
- **FR-003**: The website MUST show current loans in a scannable list, including loan ID, borrower name, funding amount, and repayment amount.
- **FR-004**: The website MUST allow users to search current loans by borrower name and display all matching current loans.
- **FR-005**: The website MUST allow users to look up one current loan by loan ID and display the matching loan details.
- **FR-006**: The website MUST allow users to delete one current loan by loan ID.
- **FR-007**: The website MUST refresh or update visible loan results after successful creation or deletion so removed loans are not shown as current.
- **FR-008**: The website MUST display meaningful success messages for completed create, lookup, search, listing, and delete actions.
- **FR-009**: The website MUST display meaningful validation, duplicate, not-found, empty-result, and service-unavailable messages.
- **FR-010**: The website MUST preserve user-entered values when an action fails due to validation or service availability.
- **FR-011**: The website MUST remain usable on desktop and mobile-sized screens without horizontal scrolling for primary workflows.
- **FR-012**: The website MUST keep authentication integration, durable persistence, public exposure, container registry work, Kubernetes, and cloud infrastructure out of scope for this slice.
- **FR-013**: The website MUST provide clear setup, run, test, and demo instructions for the website workflow.
- **FR-014**: The website MUST be testable with automated coverage at or above 80% for implemented behaviour.
- **FR-015**: The website MUST keep the existing temporary-session data boundary visible to users through documentation and appropriate empty/not-found states after restart.

### Key Entities *(include if feature involves data)*

- **Loan**: An in-memory record with loan ID, borrower name,
  funding amount, and repayment amount.
- **Loan Form Input**: User-entered loan ID, borrower name, funding amount,
  repayment amount, borrower-name search term, or loan ID action term.
- **Loan Result View**: The visible representation of current loans, one looked-up
  loan, borrower-name matches, empty results, and deleted loan confirmation.
- **User Feedback Message**: A success, validation, duplicate, not-found,
  empty-result, or service-unavailable message shown after user actions.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reviewer can create a valid loan from the website and see it in the current loan list within 3 minutes after the service and website are running.
- **SC-002**: A reviewer can complete create, list, borrower-name search, loan ID lookup, and delete workflows from the website in under 6 minutes.
- **SC-003**: Success and error feedback for each primary workflow is visible within 2 seconds in local test usage.
- **SC-004**: The primary workflows remain usable at desktop and mobile-sized widths without horizontal scrolling.
- **SC-005**: Empty, validation, duplicate, not-found, and service-unavailable states are covered by automated or documented validation.
- **SC-006**: Reviewer can run the website, service, and test suite from documentation without missing setup steps.
- **SC-007**: Test command reports at least 80% statement coverage for implemented behaviour.
- **SC-008**: The website scope, trade-offs, and temporary-session assumptions can be explained in under 40 minutes.

## Assumptions

- The existing loan-management service remains the source of truth for create,
  list, borrower-name search, loan ID lookup, and delete behaviour.
- Users of this slice are reviewers or internal operators validating the
  technical task locally.
- The website is a local demonstration surface and does not introduce
  authentication, durable storage, public exposure, container registry work,
  Kubernetes, or cloud infrastructure.
- Current loans remain temporary and may disappear when the running service
  restarts.
- Loan ID and borrower-name matching continue to follow the existing trimmed,
  case-sensitive rules from the service.
- The website should favor clear, compact workflows over marketing content.
