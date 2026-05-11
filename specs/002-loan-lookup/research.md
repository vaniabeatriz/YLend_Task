# Research: Loan Lookup

## Decision: Reuse the Existing Flask API Surface

**Rationale**: The lookup workflow is part of the same local loan-management
slice as loan creation. Reusing the existing Flask application keeps the feature
small, testable, and explainable without adding an interface style or framework.

**Alternatives considered**:

- Browser UI: rejected because the feature only requires a caller to retrieve a
  current loan and UI remains out of scope.
- Separate service process: rejected because it adds deployment and integration
  complexity without a requirement.

## Decision: Reuse the In-Memory Loan Store

**Rationale**: The spec requires current-session lookup only. The existing
process-local dictionary keyed by trimmed, case-sensitive loan ID already models
that lifecycle.

**Alternatives considered**:

- Database persistence: rejected because records should disappear after restart.
- File storage: rejected because persistence beyond runtime is out of scope.
- Separate lookup cache: rejected because the create-loan store is already the
  source of truth for the active session.

## Decision: Trim Lookup IDs and Match Case-Sensitively

**Rationale**: Lookup should follow the same identity rules as creation so a
loan accepted under a trimmed, case-sensitive ID can be retrieved predictably.

**Alternatives considered**:

- Case-insensitive lookup: rejected because it conflicts with the existing loan
  ID uniqueness rule.
- Raw, untrimmed lookup: rejected because it would make leading/trailing
  whitespace behave differently from creation.

## Decision: Return a Clear Not-Found Error for Missing Loans

**Rationale**: A missing lookup result is a normal user-facing outcome, not an
internal failure. The caller needs a clear response when the ID is unknown,
expired after restart, blank, or case-mismatched.

**Alternatives considered**:

- Empty successful response: rejected because it hides whether the lookup
  succeeded.
- Validation error for all misses: rejected because a well-formed ID can still
  be absent from the current session.

## Decision: Cover Lookup at Service and Integration Levels

**Rationale**: Unit tests can prove trimming, case sensitivity, and not-found
logic close to the store. Integration tests can prove the externally visible
lookup response and error format.

**Alternatives considered**:

- Integration tests only: rejected because service identity rules are important
  and cheap to test directly.
- Manual smoke tests only: rejected because the project has an 80% automated
  coverage gate.
