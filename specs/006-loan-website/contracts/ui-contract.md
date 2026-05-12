# UI Contract: Loan Website

## Browser Entry Point

### `GET /`

Returns the single-page loan-management website.

Expected page regions:

- Create loan form
- Current loans list
- Borrower-name search form and results
- Loan ID lookup form and result
- Loan deletion form and result
- Global feedback area for success and error messages
- Temporary-session note
- Loading/action-in-progress state with a `data-feedback-target-ms="2000"`
  marker for local feedback timing validation

Expected static assets:

- `/static/loan_website.css`
- `/static/loan_website.js`

## Existing API Dependencies

The website consumes the existing same-origin loan API:

| User action | API operation | Success state | Error/empty state |
|-------------|---------------|---------------|-------------------|
| Create loan | `POST /loans` | Show created loan and refresh current loans | Show validation or duplicate feedback |
| List current loans | `GET /loans` | Show all current loans | Show empty current-list state |
| Search by borrower name | `GET /loans?borrowerName=<value>` | Show matching loans | Show empty borrower-result or validation feedback |
| Look up by loan ID | `GET /loans/<loanId>` | Show one loan | Show not-found feedback |
| Delete by loan ID | `DELETE /loans/<loanId>` | Show deleted loan and refresh current loans | Show not-found feedback |

## Page Interaction Contract

### Create Loan

Inputs:

- Loan ID
- Borrower name
- Funding amount
- Repayment amount

Expected behaviour:

- Submit creates one loan.
- Success message identifies the created loan.
- Current loans refresh after success.
- Validation or duplicate feedback remains visible after failure.
- Entered values remain available after failure.

### List Current Loans

Expected behaviour:

- Initial page load requests current loans.
- Refresh action requests current loans again.
- Empty session shows an empty-state message, not an error.

### Borrower-Name Search

Inputs:

- Borrower name

Expected behaviour:

- Search returns all current loans with exact matching borrower name after
  existing service normalization rules.
- No matches shows an empty-state message.
- Blank search shows validation feedback.

### Loan ID Lookup

Inputs:

- Loan ID

Expected behaviour:

- Lookup shows the matching loan details.
- Missing or case-mismatched IDs show not-found feedback.
- Surrounding whitespace follows existing service normalization rules.

### Delete Loan

Inputs:

- Loan ID

Expected behaviour:

- Delete shows the deleted loan details and a success message.
- Current loans refresh after success.
- Already-deleted, missing, or case-mismatched IDs show not-found feedback.
- Other current loans remain visible and unchanged.

## Feedback Contract

Feedback types:

- Success: completed action and affected loan where applicable
- Validation: field-level guidance
- Duplicate: duplicate loan ID explanation
- Not found: no matching current loan
- Empty: no current loans or no borrower matches
- Service unavailable: retryable message when the service cannot be reached
- Loading: immediate action-in-progress message while a request is pending

## Responsive Contract

Validation targets:

- Desktop-width layout shows forms and results in a compact scannable layout.
- Mobile-width layout keeps controls, messages, and result rows readable without
  horizontal scrolling.
- Buttons and inputs remain reachable and text remains inside its container.
- Primary success and error feedback is expected within 2 seconds in local
  usage; browser validation should include this timing check.

## Out Of Scope

- Auth0 or any authentication integration
- Durable persistence
- Public exposure
- Container registry work
- Kubernetes or Helm
- Cloud infrastructure
- Separate frontend application build or deployment pipeline
