# Feature Specification: Loan Listing

**Feature Branch**: `003-loan-listing`  
**Created**: 2026-05-11  
**Status**: Draft  
**Input**: User description: "Add loan listing so callers can retrieve all current loans created during the active application session, leaving deletion for later."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Current Loans (Priority: P1)

A caller can view all loans currently stored in the active application session so
they can confirm the complete temporary loan set without knowing each loan ID in
advance.

**Why this priority**: Listing is the next natural workflow after creating and
looking up individual loans. It lets reviewers see the active data set while
still avoiding deletion, persistence, search, or reporting scope.

**Independent Test**: Create more than one valid loan, request the current loan
collection, and confirm every stored loan is returned.

**Acceptance Scenarios**:

1. **Given** multiple loans exist in the current session, **When** the caller requests the current loan collection, **Then** all current loans are returned.
2. **Given** loan IDs differ only by letter case, **When** the caller requests the current loan collection, **Then** both distinct loans are present.
3. **Given** loans were created with surrounding whitespace in text fields, **When** the caller requests the current loan collection, **Then** the stored trimmed values are returned.

---

### User Story 2 - Understand an Empty Session (Priority: P2)

A caller receives a clear successful response when no loans exist in the current
application session so they can distinguish an empty data set from an error.

**Why this priority**: Empty-list behaviour is essential for a listing workflow,
but it depends on the primary ability to return the current collection.

**Independent Test**: Start a fresh application session, request the current loan
collection before creating any loans, and confirm an empty collection is returned.

**Acceptance Scenarios**:

1. **Given** no loans exist in the current session, **When** the caller requests the current loan collection, **Then** an empty collection is returned.
2. **Given** the application restarted after loans were created, **When** the caller requests the current loan collection, **Then** an empty collection is returned.

### Edge Cases

- No loans have been created in the active session.
- Loans existed in a previous session but disappeared after restart.
- Multiple loans have the same letters with different casing in their loan IDs.
- Stored text values were created with leading or trailing whitespace and should
  appear in normalized form.
- Listing is requested after validation failures or duplicate create attempts;
  rejected loans must not appear.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow callers to retrieve the collection of all loans currently stored in the active session.
- **FR-002**: System MUST return every currently stored loan exactly once.
- **FR-003**: System MUST include each loan's loan ID, borrower name, funding amount, and repayment amount.
- **FR-004**: System MUST return an empty collection when no current loans exist.
- **FR-005**: System MUST not include loans rejected by validation or duplicate checks.
- **FR-006**: System MUST preserve the existing case-sensitive loan ID identity rules.
- **FR-007**: System MUST retain the existing temporary-session storage boundary; listing must not imply persistence after restart.
- **FR-008**: System MUST keep deletion, filtering, searching, sorting controls, pagination, authentication, public exposure, and cloud-hosted deployment out of scope for this feature.
- **FR-009**: System MUST provide clear setup, run, test, and demo instructions for the listing workflow.
- **FR-010**: System MUST be testable with automated coverage at or above 80%.

### Key Entities *(include if feature involves data)*

- **Loan**: A temporary record representing one loan during the current
  application session. Key attributes are loan ID, borrower name, funding
  amount, and repayment amount.
- **Loan Collection**: The current set of stored loans available during the
  active application session.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reviewer can create multiple loans and retrieve the current loan collection within 3 minutes after the application is running.
- **SC-002**: Listing current loans returns within 2 seconds in local test usage.
- **SC-003**: A fresh or restarted session returns an empty collection within 2 seconds.
- **SC-004**: Automated tests cover non-empty listing, empty listing, case-sensitive distinct IDs, and restart behaviour.
- **SC-005**: Reviewer can run the application and test suite from documentation without missing setup steps.
- **SC-006**: Test command reports at least 80% statement coverage.

## Assumptions

- Loan creation already exists and remains the way current loans enter the system.
- Loan lookup already exists and remains limited to retrieving one current loan by loan ID.
- Current loans remain temporary and disappear when the application process restarts.
- The listing returns the current collection without filtering, searching, sorting controls, or pagination.
- The returned collection may use the system's current storage order as long as every current loan is returned exactly once.
- Browser UI, loan deletion, authentication, public exposure, and cloud-hosted deployment are out of scope for this feature.
- The solution must remain explainable in under 40 minutes.
