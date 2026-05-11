# Data Model: Loan Lookup

## Entity: Loan

A `Loan` is a temporary record created earlier in the current application
session and retrievable by loan ID until the application process restarts.

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `loanId` | string | Yes | Stored as trimmed text; lookup trims surrounding whitespace and matches case-sensitively |
| `borrowerName` | string | Yes | Returned exactly as stored by the create workflow |
| `fundingAmount` | decimal | Yes | Returned exactly as stored by the create workflow |
| `repaymentAmount` | decimal | Yes | Returned exactly as stored by the create workflow |

## Relationships

- No new relationships in this slice.
- Each current `Loan` is uniquely identified by its trimmed, case-sensitive
  `loanId`.

## State Transitions

```text
Absent -> Stored -> Retrieved
Stored -> Absent
Absent -> Not Found
```

- `Absent -> Stored`: handled by the existing create-loan workflow.
- `Stored -> Retrieved`: a lookup request supplies a matching trimmed,
  case-sensitive loan ID and receives the stored loan record.
- `Stored -> Absent`: all stored loans disappear when the application process
  restarts.
- `Absent -> Not Found`: a lookup request supplies an ID that is blank, unknown,
  case-mismatched, or no longer present after restart.

## Validation Rules

- Lookup input is treated as a loan ID.
- Surrounding whitespace is trimmed before matching.
- Matching is case-sensitive.
- A missing, blank, whitespace-only, unknown, expired, or case-mismatched ID
  returns a not-found result without modifying storage.

## Storage

- Reuse the current process-local in-memory dictionary.
- Dictionary key: trimmed `loanId`.
- Dictionary value: stored `Loan` record.
- Lookup does not create, update, delete, persist, or list records.
