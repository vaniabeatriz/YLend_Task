# Data Model: Loan Deletion

## Entity: Loan

A `Loan` is a temporary record created earlier in the current application
session and retrievable until deleted or until the application process restarts.

### Fields

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `loanId` | string | Yes | Stored as trimmed text; identity remains case-sensitive; deletion trims the supplied loan ID before matching |
| `borrowerName` | string | Yes | Stored as trimmed text; returned in successful deletion response |
| `fundingAmount` | decimal | Yes | Monetary value greater than 0; returned in successful deletion response |
| `repaymentAmount` | decimal | Yes | Monetary value greater than 0; returned in successful deletion response |

### Relationships

- A loan belongs to the current application session only.
- A borrower name can be associated with zero, one, or many non-deleted current
  loans.

## Entity: Delete Loan Request

A `Delete Loan Request` represents a caller-supplied loan ID used to remove one
current loan.

### Fields

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `loanId` | string | Yes | Trim surrounding whitespace before matching; match case-sensitively; blank or unknown IDs are treated as not found |

### Successful Result Shape

The response body for a successful deletion is the deleted loan record:

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `loanId` | string | Yes | ID of the removed loan |
| `borrowerName` | string | Yes | Borrower name of the removed loan |
| `fundingAmount` | decimal | Yes | Funding amount of the removed loan |
| `repaymentAmount` | decimal | Yes | Repayment amount of the removed loan |

## Validation And Matching Rules

- Delete loan ID is trimmed before matching.
- Delete loan ID matching is case-sensitive.
- A blank, whitespace-only, unknown, already-deleted, or expired loan ID is not
  a current loan and receives not-found feedback.
- Deleting one loan must not remove any other current loan.

## State Transitions

- `Absent -> Stored`: handled by the existing create-loan workflow.
- `Stored -> Deleted`: a delete request supplies a matching trimmed,
  case-sensitive loan ID; the loan is removed and the deleted record is
  returned.
- `Deleted -> Absent From Reads`: loan ID lookup, borrower-name lookup, and full
  listing no longer include the deleted loan.
- `Absent -> Not Found`: a delete request supplies an ID that is blank, unknown,
  already deleted, case-mismatched, or expired after restart.
- `Stored -> Absent`: all stored loans disappear when the application process
  restarts.

## Query Semantics

- Deletion does not create, update, persist, list, search, authenticate, or
  expose any browser UI.
- Existing create, loan ID lookup, borrower-name lookup, and full-listing
  workflows remain unchanged except that deleted loans are absent from their
  results.
