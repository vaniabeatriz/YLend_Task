# Research: Create Loan

## Decision: Use a small Flask JSON API

**Rationale**: The constitution requires Python and Flask, and the clarified
scope is API-only. A minimal Flask app gives a direct implementation path for
`POST /loans` and a health check without adding frontend or background-service
complexity.

**Alternatives considered**:
- Full website plus API: rejected because browser UI is out of scope for this
  slice.
- Additional API framework: rejected because the constitution prioritises Flask
  and simplicity.

## Decision: Store loans in a process-local dictionary

**Rationale**: The source task requires in-memory storage and the clarified
slice only needs temporary runtime data. A dictionary keyed by trimmed,
case-sensitive loan ID is simple, fast, and easy to explain.

**Alternatives considered**:
- SQLite or file storage: rejected because persistence is explicitly out of
  scope.
- Global list: rejected because duplicate detection by loan ID is simpler and
  clearer with a dictionary key.

## Decision: Validate and normalize at the service boundary

**Rationale**: Keeping trimming, required-field checks, positive monetary value
checks, duplicate detection, and response shaping in a service layer keeps the
route thin and allows focused unit tests. Loan IDs and borrower names are
trimmed before validation and storage. Loan ID uniqueness remains
case-sensitive.

**Alternatives considered**:
- Validate only in the route: rejected because it couples HTTP handling to
  business rules and makes unit tests less focused.
- Use a schema validation dependency: rejected because the validation rules are
  small enough to implement clearly without another dependency.

## Decision: Use Decimal for monetary values internally

**Rationale**: Funding amount and repayment amount are monetary values and must
be greater than 0. Python's standard `Decimal` type avoids unnecessary floating
point surprises without adding a dependency. API responses will serialize the
accepted amount values as positive JSON numbers to match the contract.

**Alternatives considered**:
- Float-only values: rejected because float behaviour is harder to defend for
  monetary values.
- Currency-aware money library: rejected as unnecessary for this slice because
  no currency conversion or precision policy is required.

## Decision: Return the stored loan on successful creation

**Rationale**: The clarification chose returning the stored record. This gives
callers immediate confirmation of normalized text values and accepted amount
values, and it makes the success test precise.

**Alternatives considered**:
- Return only the loan ID: rejected because it hides normalized stored values.
- Return only a success message: rejected because callers cannot verify the
  stored record from the response.

## Decision: Use explicit JSON error responses

**Rationale**: The spec requires clear validation and duplicate-loan messages.
The API contract uses a consistent error response with an error code, message,
and optional field-level details. This keeps integration tests straightforward.

**Alternatives considered**:
- Plain-text errors: rejected because JSON callers expect structured errors.
- One generic error message: rejected because it weakens validation feedback.

## Decision: Keep local deployment to the Flask development server for this slice

**Rationale**: The active spec asks for a documented local deployment path that
does not require external services. The Flask development server is enough for
reviewing this API slice locally and keeps the explanation concise.

**Alternatives considered**:
- Docker and Kubernetes: deferred because they belong to a later platform
  readiness slice, not the first Create Loan API requirement.
- Public cloud deployment: rejected for this slice because public exposure and
  cloud-hosted deployment are out of scope.

## Decision: Test with pytest and pytest-cov

**Rationale**: The constitution requires pytest and at least 80% statement
coverage. Unit tests will cover validation/storage decisions, and integration
tests will cover the HTTP contract for success, validation failures, and
duplicates.

**Alternatives considered**:
- Manual-only testing: rejected by the constitution.
- End-to-end browser testing: rejected because browser UI is out of scope.
