# Data Model: Durable Loan Persistence

## Entity: Durable Loan Record

Represents one current loan that remains available after application restart.

### Fields

- `sequence`: Internal insertion-order value used only to preserve listing and
  search ordering.
- `loanId`: Caller-supplied loan ID after trimming. Required, unique, and
  case-sensitive.
- `borrowerName`: Borrower name after trimming. Required and case-sensitive for
  borrower-name search.
- `fundingAmount`: Positive finite monetary amount, stored as decimal text and
  returned as the existing JSON number value.
- `repaymentAmount`: Positive finite monetary amount, stored as decimal text
  and returned as the existing JSON number value.

### Validation Rules

- `loanId` must be a non-blank string after trimming.
- `borrowerName` must be a non-blank string after trimming.
- `fundingAmount` must be a valid finite amount greater than 0.
- `repaymentAmount` must be a valid finite amount greater than 0.
- Unknown create-loan fields are rejected before storage.
- Duplicate `loanId` values are rejected after trimming and with
  case-sensitive comparison.

### State Transitions

- `Absent -> Current`: Successful authenticated create request stores a durable
  record.
- `Current -> Current`: Duplicate create request is rejected and leaves the
  existing durable record unchanged.
- `Current -> Removed`: Successful authenticated delete request removes the
  durable record.
- `Removed -> Absent`: Removed loans stay absent after application restart.
- `Absent -> Absent`: Missing lookup/delete, invalid input, unauthenticated, and
  invalid-authentication requests do not create records.

## Entity: Loan Collection

Represents the current visible set of durable loan records.

### Fields

- `loans`: Ordered list of durable loan records serialized with the existing
  loan JSON shape.

### Rules

- Full listing returns all current durable records in insertion order.
- Borrower-name search returns only current records whose stored borrower name
  exactly matches the trimmed search term.
- Empty storage or no matching borrower returns `{"loans": []}`.

## Entity: Persistence State

Represents whether local durable storage is ready and what data exists at
startup.

### States

- `Unprepared`: No local database file/table is present yet.
- `ReadyEmpty`: Storage is prepared and contains no current loans.
- `ReadyWithLoans`: Storage is prepared and contains one or more current loans.
- `Unavailable`: Storage cannot be prepared, opened, read, or written.

### Rules

- Startup converts `Unprepared` to `ReadyEmpty` automatically.
- Startup preserves `ReadyWithLoans` records.
- Storage failures move workflow attempts to `Unavailable` feedback without
  changing authentication semantics.

## Entity: Storage Preparation Result

Represents the outcome of startup preparation for durable loan storage.

### Fields

- `ready`: Whether loan workflows may use durable storage.
- `location`: Local storage location for documentation and diagnostics.
- `error`: Clear setup/service message when storage is unavailable.

### Rules

- Successful preparation must not delete existing durable loans.
- Failed preparation must not silently fall back to empty in-memory storage,
  because that would hide durability failures.
