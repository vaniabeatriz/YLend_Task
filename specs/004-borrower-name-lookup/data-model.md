# Data Model: Borrower Name Loan Lookup

## Entity: Loan

A `Loan` is a temporary record created earlier in the current application
session and retrievable until the application process restarts.

### Fields

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `loanId` | string | Yes | Stored as trimmed text; identity remains case-sensitive |
| `borrowerName` | string | Yes | Stored as trimmed text; borrower-name lookup matches this value exactly and case-sensitively |
| `fundingAmount` | decimal | Yes | Monetary value greater than 0 |
| `repaymentAmount` | decimal | Yes | Monetary value greater than 0 |

### Relationships

- A borrower name can be associated with zero, one, or many current loans.
- A loan belongs to the current application session only.

## Entity: Borrower Name Search

A `Borrower Name Search` represents a caller-supplied borrower name used to
find matching current loans.

### Fields

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `borrowerName` | string | Yes | Trim surrounding whitespace before validation and matching; reject if blank after trimming |

### Result Shape

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `loans` | array of Loan | Yes | Contains every current loan whose stored borrower name exactly matches the trimmed search term; empty when no current matches exist |

## Validation Rules

- Search term must be present when the caller is performing borrower-name
  lookup.
- Search term must not be blank or whitespace-only after trimming.
- Matching is exact and case-sensitive after trimming the search term.
- Rejected create attempts and duplicate create attempts do not create loan
  records and therefore cannot appear in lookup results.

## State Transitions

- `Absent -> Stored`: handled by the existing create-loan workflow.
- `Stored -> Borrower Matched`: a borrower-name lookup supplies a matching
  borrower name and receives the stored loan in the result collection.
- `Stored -> Borrower Not Matched`: a borrower-name lookup supplies a different
  borrower name and the stored loan is excluded from the result collection.
- `Stored -> Absent`: all stored loans disappear when the application process
  restarts.

## Query Semantics

- Missing borrower-name search term preserves existing full-listing behavior.
- Present but blank borrower-name search term is invalid.
- Borrower-name lookup does not create, update, delete, persist, sort,
  paginate, or partially match records.
