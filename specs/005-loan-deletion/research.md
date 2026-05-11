# Research: Loan Deletion

## Decision: Return the deleted loan record on successful deletion

**Rationale**: The clarification selected `200 OK` with the deleted loan record
in the response body. This lets callers confirm exactly which current loan was
removed while keeping the existing loan response shape.

**Alternatives considered**:

- Return `204 No Content`. Rejected by clarification; it confirms success but
  does not identify the removed record.
- Return a separate confirmation message. Rejected because the existing stored
  loan record is more useful and already documented.

## Decision: Reuse existing loan ID normalization and not-found semantics

**Rationale**: Create and lookup already define trimmed, case-sensitive loan ID
identity. Deletion should use the same rule so callers do not need to learn a
new identity policy. Unknown, already-deleted, blank, or expired loan IDs can
share the existing absent-loan feedback pattern.

**Alternatives considered**:

- Treat blank loan IDs as a separate validation error. Rejected because lookup
  already treats blank IDs as not found, and consistent absent-loan feedback is
  simpler.
- Case-insensitive deletion. Rejected because it would conflict with existing
  case-sensitive loan ID identity.

## Decision: Delete directly from the existing in-memory store

**Rationale**: Current loans are stored in one process-local dictionary keyed by
loan ID. Removing the matching dictionary entry is the simplest design that
satisfies the feature and automatically updates lookup, borrower-name search,
and full listing results.

**Alternatives considered**:

- Soft-delete flag. Rejected because persistence, audit history, and recovery
  are out of scope.
- Separate deletion log. Rejected because no audit or observability requirement
  needs it in this slice.

## Decision: Preserve all existing read and create workflows as regressions

**Rationale**: Deletion is intentionally the only new behavior. Tests should
prove create still seeds loans, loan ID lookup still returns non-deleted loans,
borrower-name lookup omits deleted loans, full listing omits deleted loans, and
not-found responses remain clear.

**Alternatives considered**:

- Test only the delete route. Rejected because the primary risk is stale deleted
  loans appearing in existing read workflows.
