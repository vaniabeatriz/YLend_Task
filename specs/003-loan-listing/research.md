# Research: Loan Listing

## Decision: Reuse the Existing Flask API Surface

**Rationale**: Listing is part of the same local loan-management workflow as
creation and single-loan lookup. Reusing the existing Flask application keeps
the feature small, reviewable, and easy to explain.

**Alternatives considered**:

- Browser UI: rejected because the feature only requires callers to retrieve the
  current loan collection and UI remains out of scope.
- Separate service process: rejected because it adds deployment and integration
  complexity without a requirement.

## Decision: Reuse the In-Memory Loan Store

**Rationale**: The spec requires listing current-session loans only. The existing
process-local dictionary already contains exactly the active loan set and clears
on restart.

**Alternatives considered**:

- Database persistence: rejected because records should disappear after restart.
- File storage: rejected because persistence beyond runtime is out of scope.
- Separate listing projection: rejected because the in-memory create/lookup store
  is already the source of truth for the active session.

## Decision: Return a `loans` Collection Object

**Rationale**: A response object with a `loans` array is explicit for both
non-empty and empty sessions, remains simple to document, and can be validated
without adding metadata, pagination, or filtering controls.

**Alternatives considered**:

- Bare JSON array: rejected because a named collection is clearer in docs and
  tests.
- Response with `count` or pagination metadata: rejected because the feature
  intentionally excludes pagination and extra controls.

## Decision: Use Existing Storage Order

**Rationale**: The spec only requires every current loan exactly once. Returning
the dictionary's current order avoids adding sorting rules and keeps the feature
small.

**Alternatives considered**:

- Sort by loan ID: rejected because sorting controls and ordering rules are out
  of scope.
- Sort by borrower or amount: rejected for the same reason and because it adds
  unnecessary behaviour.

## Decision: Return Success with an Empty Collection

**Rationale**: An empty current session is a valid state, not an error. Returning
an empty collection lets callers distinguish "no loans" from a failure.

**Alternatives considered**:

- Not-found error for empty sessions: rejected because the collection resource
  exists even when it contains no loans.
- Validation error: rejected because no caller input is invalid in this flow.

## Decision: Cover Listing at Service and Integration Levels

**Rationale**: Unit tests can prove collection composition, rejection exclusion,
case-sensitive distinct IDs, and empty-store behaviour close to the store.
Integration tests can prove the externally visible response shape and restart
behaviour.

**Alternatives considered**:

- Integration tests only: rejected because service-level collection rules are
  important and cheap to test directly.
- Manual smoke tests only: rejected because the project has an 80% automated
  coverage gate.
