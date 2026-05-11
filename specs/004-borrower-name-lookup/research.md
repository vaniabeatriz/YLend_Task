# Research: Borrower Name Loan Lookup

## Decision: Reuse the existing loan collection response envelope

**Rationale**: Borrower names are not unique, so search can return zero, one, or
many loans. Reusing the existing `loans` collection shape keeps full listing and
borrower-name lookup consistent for callers and avoids introducing a second
collection representation.

**Alternatives considered**:

- Return a bare array. Rejected because current listing already uses an object
  envelope and the project benefits from one collection shape.
- Return a single loan. Rejected because multiple loans can share one borrower
  name.

## Decision: Keep exact case-sensitive borrower-name matching after trimming the search term

**Rationale**: Existing loan ID rules are trim-and-preserve-case. Applying the
same simple identity style to borrower names keeps behavior predictable and
easy to test while avoiding hidden normalization rules.

**Alternatives considered**:

- Case-insensitive matching. Rejected because the spec explicitly records
  case-sensitive behavior and this would add a broader search policy.
- Partial or contains matching. Rejected because the feature asks for lookup by
  borrower name, not text search.

## Decision: Treat missing borrower-name query as full listing and blank borrower-name query as validation error

**Rationale**: The application already exposes full listing through the same
loan collection resource. A missing borrower-name search term should preserve
that behavior. An explicitly blank borrower-name search term is likely caller
error and should not silently become full listing.

**Alternatives considered**:

- Treat blank borrower name as full listing. Rejected because it blurs the
  difference between list-all and search workflows.
- Return an empty collection for blank borrower name. Rejected because blank
  input is invalid rather than a meaningful borrower identity.

## Decision: Scan current loans instead of adding a secondary borrower-name index

**Rationale**: The current technical-test scope is a single-process local demo
with temporary data. Scanning the current in-memory loan collection keeps the
design simpler and avoids index update paths when loans are added or later
deleted.

**Alternatives considered**:

- Maintain an index keyed by borrower name. Rejected because it adds consistency
  work without a current scale requirement.
- Add persistent search storage. Rejected because persistence is out of scope.

## Decision: Test at service and route levels

**Rationale**: Service tests can prove matching, trimming, case sensitivity, and
empty results without HTTP overhead. Integration tests can prove the externally
visible borrower-name lookup, validation response, no-match response, restart
behavior, and preservation of full listing and loan ID lookup.

**Alternatives considered**:

- Integration tests only. Rejected because matching rules are easier to isolate
  and debug at service level.
- Service tests only. Rejected because the user-facing contract is HTTP-visible.
