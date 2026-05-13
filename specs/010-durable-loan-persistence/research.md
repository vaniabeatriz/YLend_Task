# Research: Durable Loan Persistence

## Decision: Use local SQLite via Python standard library

**Rationale**: The feature explicitly requires local database-backed
persistence. SQLite provides a real durable database file without adding a
managed service, container, cloud dependency, or third-party package. Python
includes `sqlite3`, so the implementation remains easy to install, test, and
explain.

**Alternatives considered**:

- Keep in-memory storage: rejected because loans would still disappear on
  restart.
- JSON or CSV file storage: rejected because the requirement says
  database-backed repository and because duplicate/delete/list behaviours are
  safer with database constraints and transactions.
- PostgreSQL or another external database: rejected because it adds service
  setup and infrastructure beyond the local technical-test scope.
- SQLAlchemy or migration framework: rejected because standard library SQLite is
  sufficient for one simple table and avoids extra dependency explanation.

## Decision: Initialize storage automatically during app startup

**Rationale**: The spec requires reviewers to start in a fresh local environment
without manual storage preparation. Creating the SQLite directory/file and loan
table from the Flask app factory keeps setup simple and makes tests able to use
isolated temporary database paths.

**Alternatives considered**:

- Manual setup command: rejected because it adds a step reviewers can miss and
  conflicts with automatic preparation requirements.
- Lazy initialization on first loan request: rejected because startup health and
  configuration failures are easier to diagnose when storage is prepared before
  loan workflows are served.
- Migration framework: rejected because this slice has one table and no schema
  evolution requirement.

## Decision: Use a repository boundary below the existing loan service

**Rationale**: `LoanService` already owns validation, normalization, duplicate
rules, and response conversion. A repository can own durable create/list/search/
lookup/delete operations while keeping routes and website logic stable. This is
the smallest abstraction that prevents SQL concerns from spreading into route
handlers.

**Alternatives considered**:

- Put SQLite access directly in `LoanService`: rejected because validation and
  storage mechanics would be tightly coupled, making restart tests and storage
  error tests harder to keep focused.
- Put SQLite access in routes: rejected because routes should remain request
  parsing/auth/response orchestration only.
- Full ORM/data mapper: rejected because it is unnecessary for one table.

## Decision: Store monetary values as decimal text

**Rationale**: Existing service logic parses monetary values with `Decimal`.
Storing canonical decimal strings preserves precision and avoids SQLite floating
point surprises. Public JSON response shapes stay unchanged because `Loan`
already serializes amounts as JSON numbers.

**Alternatives considered**:

- Store SQLite REAL values: rejected because binary floating point can introduce
  surprising formatting/precision changes.
- Store integer cents: rejected because the current API accepts decimal amounts
  without a specified number of decimal places; forcing cents would add
  unrequested rounding policy.

## Decision: Preserve list ordering with an insertion sequence

**Rationale**: Earlier slices document full listing as storage-order. SQLite
does not guarantee row order without an explicit ordering column. A generated
insertion sequence keeps list/search results stable across process restarts.

**Alternatives considered**:

- Order by loan ID: rejected because it changes existing storage-order
  behaviour.
- Rely on database row return order: rejected because it is not a stable
  contract.

## Decision: Treat storage availability failures as service errors

**Rationale**: The spec requires clear service feedback when durable storage
cannot be prepared or accessed. Protected loan workflows should fail without
mutating data and without changing authentication behaviour. A stable service
error response lets the website reuse its existing service-unavailable feedback
path.

**Alternatives considered**:

- Crash the app on every storage error: rejected because the spec asks for clear
  workflow feedback.
- Return validation errors for storage failures: rejected because storage
  availability is not user input validation.
