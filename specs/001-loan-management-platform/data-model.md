# Data Model: Create Loan

## Entity: Loan

A `Loan` is a temporary record created through the Create Loan API and retained
only for the lifetime of the running application session.

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `loanId` | string | Yes | Trim surrounding whitespace; value after trimming MUST be non-empty; uniqueness is case-sensitive |
| `borrowerName` | string | Yes | Trim surrounding whitespace; value after trimming MUST be non-empty |
| `fundingAmount` | decimal | Yes | MUST be a valid monetary value greater than 0 |
| `repaymentAmount` | decimal | Yes | MUST be a valid monetary value greater than 0 |

## Relationships

- No relationships in this slice.
- Each current `Loan` is uniquely identified by its trimmed, case-sensitive
  `loanId`.

## State Transitions

```text
Absent -> Stored
```

- `Absent -> Stored`: a valid create request is accepted and the stored loan is
  returned to the caller.
- `Absent -> Rejected`: the request is missing required data, contains invalid
  data, or cannot be parsed as a valid create-loan request.
- `Stored -> Rejected`: a later request uses the same trimmed, case-sensitive
  `loanId` and is rejected as a duplicate.
- `Stored -> Absent`: all stored loans disappear when the application process
  restarts.

## Validation Rules

- Required fields: `loanId`, `borrowerName`, `fundingAmount`,
  `repaymentAmount`.
- Text fields are trimmed before validation and storage.
- Blank or whitespace-only `loanId` and `borrowerName` values are invalid.
- `loanId` uniqueness is checked after trimming surrounding whitespace and is
  case-sensitive.
- Monetary fields must parse as positive decimal values greater than 0.
- Duplicate loan IDs are rejected without modifying the existing stored loan.

## Storage

- Store current loans in a process-local in-memory dictionary.
- Dictionary key: trimmed `loanId`.
- Dictionary value: stored `Loan` record.
- Storage is intentionally temporary and is not shared across application
  restarts or multiple processes.
