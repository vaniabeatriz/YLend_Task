# Feature Specification: Borrower Name Loan Lookup

**Feature Branch**: `004-borrower-name-lookup`  
**Created**: 2026-05-11  
**Status**: Draft  
**Input**: User description: "Add borrower-name loan lookup so callers can retrieve current loans by borrowerName using GET /loans?borrowerName=, while keeping loan ID lookup, full listing, deletion, persistence, authentication, and UI changes out of scope for this slice."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Find Current Loans By Borrower Name (Priority: P1)

An API caller can search the current application session for loans with a
specific borrower name so they can find borrower-related records without
knowing each loan ID.

**Why this priority**: Borrower-name lookup is a required loan-management
workflow and is the next smallest useful search capability after single-loan
lookup and full listing.

**Independent Test**: Create multiple valid loans, including at least two with
the same borrower name and one with a different borrower name, then search for
the shared borrower name and confirm only the matching current loans are
returned.

**Acceptance Scenarios**:

1. **Given** current loans exist for the supplied borrower name, **When** the caller searches by that borrower name, **Then** every matching current loan is returned exactly once.
2. **Given** current loans exist for different borrower names, **When** the caller searches by one borrower name, **Then** loans for other borrower names are not returned.
3. **Given** the supplied borrower name has leading or trailing whitespace, **When** the caller searches by borrower name, **Then** matching ignores the surrounding whitespace.

---

### User Story 2 - Understand No Borrower Matches (Priority: P2)

An API caller receives a successful empty result when no current loan exists for
the searched borrower name so they can distinguish "no matches" from a system
failure.

**Why this priority**: Search workflows need predictable empty-result behavior,
especially because borrower names are not unique identifiers.

**Independent Test**: Search for a borrower name that has no current matching
loans and confirm the caller receives an empty collection with no loan records.

**Acceptance Scenarios**:

1. **Given** no current loans match the supplied borrower name, **When** the caller searches by borrower name, **Then** the system returns an empty loan collection.
2. **Given** the application has restarted since matching loans were created, **When** the caller searches for that borrower name, **Then** the system returns an empty loan collection.

---

### User Story 3 - Reject Invalid Borrower Search Terms (Priority: P3)

An API caller receives clear feedback when the borrower-name search term is
blank so accidental broad searches are avoided.

**Why this priority**: A blank borrower-name search should not be confused with
the already existing full-listing workflow.

**Independent Test**: Search with an empty or whitespace-only borrower name and
confirm the request is rejected with a clear validation message.

**Acceptance Scenarios**:

1. **Given** the borrower-name search term is empty, **When** the caller searches by borrower name, **Then** the system rejects the request and explains that borrower name is required.
2. **Given** the borrower-name search term is whitespace-only, **When** the caller searches by borrower name, **Then** the system rejects the request and explains that borrower name is required.

### Edge Cases

- Borrower name search term has leading or trailing whitespace.
- Borrower name search term is blank or whitespace-only.
- Multiple current loans share the same borrower name.
- Matching borrower names differ only by letter case.
- Matching loans existed in a previous application session but disappeared
  after restart.
- Rejected create attempts and duplicate create attempts must not appear in
  borrower-name lookup results.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow callers to retrieve current loans by borrower name.
- **FR-002**: System MUST return all current loans whose stored borrower name exactly matches the supplied borrower name after trimming surrounding whitespace from the search term.
- **FR-003**: System MUST match borrower names case-sensitively.
- **FR-004**: System MUST return a loan collection for borrower-name lookup results, including an empty collection when no current matches exist.
- **FR-005**: System MUST reject blank or whitespace-only borrower-name search terms with a clear validation message.
- **FR-006**: System MUST keep existing loan ID lookup behavior unchanged.
- **FR-007**: System MUST keep existing full-loan listing behavior unchanged when no borrower-name search term is supplied.
- **FR-008**: System MUST retain the existing temporary-session storage boundary; borrower-name lookup must not imply persistence after restart.
- **FR-009**: System MUST provide clear setup, run, test, and demo instructions for the borrower-name lookup workflow.
- **FR-010**: System MUST be testable with automated coverage at or above 80%.
- **FR-011**: System MUST treat deletion, persistence, authentication, browser UI, public exposure, and cloud-hosted deployment as out of scope for this slice.

### Key Entities *(include if feature involves data)*

- **Loan**: A temporary record representing one loan during the current
  application session. Key attributes are loan ID, borrower name, funding
  amount, and repayment amount.
- **Borrower Name Search**: A caller-supplied borrower name used to find all
  current loans with an exactly matching stored borrower name after trimming
  the search term.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reviewer can create multiple loans and retrieve the matching loans for one borrower name within 3 minutes after the application is running.
- **SC-002**: A borrower-name lookup for an existing borrower returns only matching current loans within 2 seconds in local test usage.
- **SC-003**: A borrower-name lookup for an unknown or expired borrower name returns an empty collection within 2 seconds in local test usage.
- **SC-004**: Blank borrower-name lookup attempts return clear validation feedback within 2 seconds in local test usage.
- **SC-005**: Case-sensitive and whitespace-trimmed borrower-name lookup behavior is covered by automated tests.
- **SC-006**: Reviewer can run the application and test suite from documentation without missing setup steps.
- **SC-007**: Test command reports at least 80% statement coverage.

## Assumptions

- Borrower names are not unique, so borrower-name lookup returns a collection
  rather than a single loan.
- Borrower-name matching uses exact case-sensitive equality after trimming the
  supplied search term, matching the platform's current simple identity rules.
- Existing loan creation remains the only way current loans enter the system.
- Existing loan ID lookup and full listing workflows remain available and are
  not changed by this feature.
- Current loans remain temporary and disappear when the application process
  restarts.
- Deletion, persistence, authentication, browser UI, public exposure, and
  cloud-hosted deployment remain out of scope for this feature.
