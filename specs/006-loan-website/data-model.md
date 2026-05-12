# Data Model: Loan Website

## Entity: Loan

A `Loan` is an in-memory record already managed by the existing
loan service.

### Fields

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `loanId` | string | Yes | Trim surrounding whitespace before storage or matching; identity remains case-sensitive |
| `borrowerName` | string | Yes | Trim surrounding whitespace; search matches stored borrower names exactly and case-sensitively |
| `fundingAmount` | decimal | Yes | Must be greater than 0 |
| `repaymentAmount` | decimal | Yes | Must be greater than 0 |

### Relationships

- A loan belongs to the current application session only.
- The website displays loans returned by the existing create, list,
  borrower-name search, loan ID lookup, and delete workflows.

## Entity: Loan Form Input

User-entered values used by website actions.

### Fields

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `loanId` | string | Required for create, lookup, and delete | Preserve entered value on failure; submit to existing matching rules |
| `borrowerName` | string | Required for create and borrower-name search | Preserve entered value on failure; submit to existing matching rules |
| `fundingAmount` | decimal-like input | Required for create | Show validation guidance when missing, non-numeric, zero, or negative |
| `repaymentAmount` | decimal-like input | Required for create | Show validation guidance when missing, non-numeric, zero, or negative |

## Entity: Loan Result View

The visible representation of loan-related results on the single page.

### States

| State | Meaning | Required content |
|-------|---------|------------------|
| `current-list` | All current loans are shown | Loan ID, borrower name, funding amount, repayment amount |
| `borrower-results` | Borrower-name matches are shown | Matching loans or empty-result message |
| `loan-lookup-result` | One loan lookup result is shown | Loan details or not-found message |
| `deleted-loan-result` | A delete action succeeded | Deleted loan details and confirmation |
| `empty` | No loans or no matches exist | Plain-language empty-state message |

### Relationships

- Successful create and delete actions update the current-list state.
- Deleted loans must not remain visible as current results after a refresh or
  page-state update.

## Entity: User Feedback Message

A visible message shown after a user action.

### Fields

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `type` | enum | Yes | `success`, `validation`, `duplicate`, `not-found`, `empty`, or `service-unavailable` |
| `message` | string | Yes | Human-readable and tied to the completed or failed action |
| `details` | list | No | Field-level guidance when provided by validation errors |

## Entity: Client Action State

The transient state of an in-progress website action.

### Fields

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `action` | enum | Yes | `create`, `list`, `search`, `lookup`, or `delete` |
| `isSubmitting` | boolean | Yes | Prevent repeated submissions while an action is in progress |
| `lastResult` | Loan Result View | No | Preserve latest useful result until a new result replaces it |
| `lastFeedback` | User Feedback Message | No | Shows the outcome of the latest action |

## State Transitions

- `Empty Session -> Current List`: page loads and lists zero or more current loans.
- `Create Form Submitted -> Created Loan`: valid create succeeds and current list includes the new loan.
- `Create Form Submitted -> Validation/Duplicate Feedback`: create fails and entered values remain available.
- `Borrower Search Submitted -> Borrower Results`: matching loans or an empty-state message is shown.
- `Loan ID Lookup Submitted -> Lookup Result`: one matching loan or not-found feedback is shown.
- `Delete Submitted -> Deleted Loan Result`: matching loan is removed and delete confirmation is shown.
- `Delete Submitted -> Not Found Feedback`: absent or already-deleted loan leaves visible current loans unchanged.
- `Service Restart -> Empty/Not Found`: previously visible loans may disappear because data is temporary.
- `Service Unavailable -> Retryable Feedback`: form values remain available for retry.

## Validation And Display Rules

- Required inputs should provide immediate field-level guidance when blank.
- API validation details should be displayed as field guidance when available.
- All visible result sections must handle zero-result states.
- Responsive layout must avoid horizontal scrolling for primary workflows.
- Amounts are displayed as numeric monetary values consistent with the API
  response shape.
