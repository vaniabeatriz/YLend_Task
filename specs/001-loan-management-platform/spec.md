# Feature Specification: Create Loan

**Feature Branch**: `001-loan-management-platform`  
**Created**: 2026-05-09  
**Status**: Draft  
**Input**: User description: "YouLend Platform Engineer Technical Task from `/Users/vbeatrizmarquesdelim/Documents/youLend/technical_task.md`"

## Clarifications

### Session 2026-05-09

- Q: What delivery scope should the active spec target? → A: Create Loan only.
- Q: How should the Create Loan workflow be exposed in this slice? → A: API only.
- Q: What amount values are valid for a created loan? → A: Funding amount and repayment amount must both be greater than 0.
- Q: How should loan IDs be normalised for validation and uniqueness? → A: Trim surrounding whitespace; loan ID uniqueness is case-sensitive.
- Q: What should successful loan creation return? → A: The stored loan record.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create Loan Records (Priority: P1)

An API caller can create a loan record with a loan ID, borrower name,
funding amount, and repayment amount so the loan can be managed during the
current application session.

**Why this priority**: Creating loans is the first required API capability and
the foundation for later lookup, listing, and deletion workflows.

**Independent Test**: Create a valid loan, then confirm the system accepts and
stores the loan for the current application session.

**Acceptance Scenarios**:

1. **Given** no loan exists with the submitted loan ID, **When** the API caller submits all required loan fields, **Then** the loan is accepted, stored for the current application session, and returned to the caller.
2. **Given** a loan already exists with the submitted loan ID after trimming surrounding whitespace, **When** the API caller submits another loan with the same case-sensitive loan ID, **Then** the system rejects the duplicate and explains the issue.
3. **Given** one or more required fields are missing or invalid, **When** the API caller submits the loan, **Then** the system rejects the request and shows which fields need correction.

---

### User Story 2 - Validate Delivery Readiness (Priority: P2)

A reviewer can run, test, and evaluate the solution from concise documentation
so they can assess engineering quality without hidden setup knowledge.

**Why this priority**: The submission must demonstrate maintainability,
testing, deployment readiness, and clear trade-offs.

**Independent Test**: A reviewer follows the documented setup, test, local
deployment, and demo instructions from a fresh checkout.

**Acceptance Scenarios**:

1. **Given** a fresh checkout, **When** the reviewer follows the setup instructions, **Then** the application can be started locally.
2. **Given** a fresh checkout, **When** the reviewer follows the test instructions, **Then** the automated test suite completes and reports coverage.
3. **Given** the reviewer reads the documentation, **When** they review architecture, trade-offs, and assumptions, **Then** the scope and design choices are clear enough to explain in under 40 minutes.

### Edge Cases

- Missing, blank, or whitespace-only loan IDs and borrower names.
- Duplicate loan IDs.
- Loan IDs submitted with leading or trailing whitespace.
- Funding amount or repayment amount values that are missing, zero, negative, or not valid monetary numbers.
- Temporary data disappearing after the application restarts.
- User-facing errors that need to be clear without exposing internal details.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow API callers to create a loan with loan ID, borrower name, funding amount, and repayment amount.
- **FR-002**: System MUST require loan ID and borrower name to be non-empty text values.
- **FR-003**: System MUST require funding amount and repayment amount to be valid monetary values greater than 0.
- **FR-004**: System MUST trim surrounding whitespace from loan IDs and borrower names before validation and storage.
- **FR-005**: System MUST prevent more than one current loan from using the same case-sensitive loan ID after trimming surrounding whitespace.
- **FR-006**: System MUST make the create-loan workflow available through an API interface only for this slice.
- **FR-007**: System MUST return the stored loan record after successful creation.
- **FR-008**: System MUST return clear validation and duplicate-loan messages for the create-loan workflow.
- **FR-009**: System MUST store created loan data only for the lifetime of the running application session.
- **FR-010**: System MUST provide clear setup, run, test, local deployment, architecture, trade-off, and assumption documentation for this slice.
- **FR-011**: System MUST be testable with automated coverage at or above 80%.
- **FR-012**: System MUST provide a simple way for reviewers to confirm the running application is healthy.
- **FR-013**: System MUST treat browser UI, loan lookup, listing, deletion, authentication, public exposure, and cloud-hosted deployment as out of scope for this slice.

### Key Entities *(include if feature involves data)*

- **Loan**: A temporary record representing one loan during the current application session. Key attributes are loan ID, borrower name, funding amount greater than 0, and repayment amount greater than 0.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reviewer can create a valid loan within 2 minutes after the application is running.
- **SC-002**: API callers receive clear feedback for invalid input and duplicates within 2 seconds.
- **SC-003**: A reviewer can complete the create-loan demo flow in under 3 minutes.
- **SC-004**: After an application restart, previously entered temporary loans are no longer available and this behaviour is documented.
- **SC-005**: Reviewer can run the application and test suite from documentation without missing setup steps.
- **SC-006**: Test command reports at least 80% statement coverage.
- **SC-007**: A reviewer can complete documented local setup and local deployment validation in under 20 minutes from a fresh checkout.
- **SC-008**: The architecture, trade-offs, and assumptions can be explained end-to-end in under 40 minutes.

## Assumptions

- Loan IDs are supplied by the user or calling client and are not generated by the system.
- Loan ID uniqueness is case-sensitive after trimming surrounding whitespace.
- Funding amount and repayment amount use positive decimal monetary values without currency conversion.
- Browser UI, loan lookup, listing, deletion, authentication, public exposure, and cloud-hosted deployment are out of scope for this create-loan slice.
- Data persistence beyond the running application session is intentionally out of scope.
- The baseline solution prioritises the first required API workflow and delivery clarity over broader platform enhancements.
