# Data Model: Loan Listing

## Entity: Loan

A `Loan` is a temporary record created earlier in the current application
session and available in the current loan collection until the application
process restarts.

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `loanId` | string | Yes | Stored as trimmed text; identity remains case-sensitive |
| `borrowerName` | string | Yes | Returned exactly as stored by the create workflow |
| `fundingAmount` | decimal | Yes | Returned exactly as stored by the create workflow |
| `repaymentAmount` | decimal | Yes | Returned exactly as stored by the create workflow |

## Entity: Loan Collection

A `Loan Collection` is the current set of stored loans in the active application
session.

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `loans` | array of Loan | Yes | Contains every currently stored loan exactly once; empty when no loans exist |

## Relationships

- `Loan Collection` contains zero or more `Loan` records.
- No new relationships are introduced by listing.
- Each current `Loan` remains uniquely identified by its trimmed,
  case-sensitive `loanId`.

## State Transitions

```text
Empty Collection -> Non-Empty Collection -> Listed
Non-Empty Collection -> Empty Collection
Empty Collection -> Listed
```

- `Empty Collection -> Non-Empty Collection`: handled by the existing
  create-loan workflow when a valid loan is accepted.
- `Non-Empty Collection -> Listed`: a listing request returns all current loans.
- `Non-Empty Collection -> Empty Collection`: all stored loans disappear when
  the application process restarts.
- `Empty Collection -> Listed`: a listing request returns an empty collection.

## Validation Rules

- Listing requires no caller-provided filters, sort keys, search terms, or
  pagination controls.
- Each currently stored loan appears exactly once.
- Rejected create attempts do not alter the current collection and must not
  appear in listing results.
- Loans with IDs that differ only by letter case remain distinct records.
- Returned text values reflect the normalized values stored by creation.

## Storage

- Reuse the current process-local in-memory dictionary.
- Dictionary key: trimmed `loanId`.
- Dictionary value: stored `Loan` record.
- Listing reads the current dictionary values and does not create, update,
  delete, persist, filter, search, sort, or paginate records.
