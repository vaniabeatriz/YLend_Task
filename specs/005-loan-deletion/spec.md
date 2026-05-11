# Feature Specification: Loan Deletion

**Feature Branch**: `005-loan-deletion`  
**Created**: 2026-05-11  
**Status**: Draft  
**Input**: User description: "Add loan deletion by loanId so callers can remove a current temporary loan using DELETE /loans/{loanId}, while keeping create loan, loan ID lookup, borrower-name lookup, full listing, persistence, authentication, browser UI, and deployment changes out of scope for this slice."

## Clarifications

### Session 2026-05-11

- Q: What should a successful delete response return? → A: 200 OK with the deleted loan record in the response body.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Delete A Current Loan By Loan ID (Priority: P1)

An API caller can remove one current temporary loan by loan ID so that deleted
loans are no longer available in the active application session.

**Why this priority**: Deletion is the remaining required loan-management
workflow after creation, loan ID lookup, borrower-name lookup, and full listing.
It completes the API-only loan lifecycle for the technical task while keeping
the implementation small.

**Independent Test**: Create a valid loan, delete it by the same loan ID, then
confirm loan ID lookup, borrower-name lookup, and full listing no longer return
the deleted loan.

**Acceptance Scenarios**:

1. **Given** a current loan exists for the supplied loan ID, **When** the caller deletes that loan ID, **Then** the loan is removed from the current application session and the deleted loan record is returned.
2. **Given** a current loan was deleted, **When** the caller looks up that loan ID, **Then** the system reports that no matching loan exists.
3. **Given** a current loan was deleted, **When** the caller lists current loans or searches by borrower name, **Then** the deleted loan is not included.
4. **Given** the supplied loan ID has leading or trailing whitespace, **When** the caller deletes the loan, **Then** matching ignores the surrounding whitespace.

---

### User Story 2 - Report Missing Loan Deletions Clearly (Priority: P2)

An API caller receives clear feedback when they try to delete a loan ID that is
not present in the current application session.

**Why this priority**: Deletion needs predictable not-found behavior so callers
can distinguish an absent or already-deleted loan from a successful deletion.

**Independent Test**: Request deletion for an unknown, already-deleted, or
expired loan ID and confirm the system returns a clear not-found response
without changing any remaining loans.

**Acceptance Scenarios**:

1. **Given** no current loan exists for the supplied loan ID, **When** the caller deletes that loan ID, **Then** the system reports that no matching loan exists.
2. **Given** a loan was already deleted, **When** the caller deletes the same loan ID again, **Then** the system reports that no matching loan exists.
3. **Given** the application has restarted since a loan was created, **When** the caller deletes the old loan ID, **Then** the system reports that no matching loan exists.

### Edge Cases

- Delete loan ID has leading or trailing whitespace.
- Delete loan ID is blank or whitespace-only.
- Delete loan ID differs from a stored loan ID only by letter case.
- Delete is requested for a loan that never existed.
- Delete is requested for a loan that was already deleted.
- Delete is requested for a loan that existed in a previous application session
  but disappeared after restart.
- Deleting one loan must not remove other current loans.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow callers to delete one current loan by loan ID.
- **FR-002**: System MUST trim surrounding whitespace from delete loan IDs before matching.
- **FR-003**: System MUST match delete loan IDs case-sensitively.
- **FR-004**: System MUST remove only the matching current loan when a delete request succeeds.
- **FR-005**: System MUST ensure a deleted loan is no longer returned by loan ID lookup, borrower-name lookup, or full listing.
- **FR-006**: System MUST return the deleted loan record after a current matching loan is deleted.
- **FR-007**: System MUST return a clear not-found message when no current matching loan exists for deletion.
- **FR-008**: System MUST keep existing create loan, loan ID lookup, borrower-name lookup, and full listing behavior unchanged except that deleted loans are absent from their results.
- **FR-009**: System MUST retain the existing temporary-session storage boundary; deletion must not imply persistence after restart.
- **FR-010**: System MUST provide clear setup, run, test, and demo instructions for the deletion workflow.
- **FR-011**: System MUST be testable with automated coverage at or above 80%.
- **FR-012**: System MUST treat persistence, authentication, browser UI, public exposure, cloud-hosted deployment, and infrastructure changes as out of scope for this slice.

### Key Entities *(include if feature involves data)*

- **Loan**: A temporary record representing one loan during the current
  application session. Key attributes are loan ID, borrower name, funding
  amount, and repayment amount.
- **Delete Loan Request**: A caller-supplied loan ID used to remove one current
  loan from the active application session.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reviewer can create a loan, delete it, and confirm it is absent from lookup and listing workflows within 3 minutes after the application is running.
- **SC-002**: A successful deletion removes only the targeted current loan and completes within 2 seconds in local test usage.
- **SC-003**: A deletion attempt for an unknown, already-deleted, or expired loan ID returns clear feedback within 2 seconds in local test usage.
- **SC-004**: Case-sensitive and whitespace-trimmed delete loan ID behavior is covered by automated tests.
- **SC-005**: Reviewer can run the application and test suite from documentation without missing setup steps.
- **SC-006**: Test command reports at least 80% statement coverage.

## Assumptions

- Successful deletion returns the deleted loan record so callers can confirm
  which current loan was removed.
- Delete loan ID matching follows the existing loan ID rule: trim surrounding
  whitespace and preserve case-sensitive identity.
- Existing loan creation remains the way current loans enter the system.
- Existing lookup and listing workflows remain available and reflect deletion by
  omitting removed loans.
- Current loans remain temporary and disappear when the application process
  restarts.
- Persistence, authentication, browser UI, public exposure, cloud-hosted
  deployment, and infrastructure changes remain out of scope for this feature.
