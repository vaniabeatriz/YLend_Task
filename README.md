# Loan Management API and Website

Small Flask implementation for the YouLend technical task. It provides a
single-page local website plus the JSON API for creating, looking up, listing,
searching, and deleting loan records.

## Scope

Included:

- `GET http://127.0.0.1:5000/`
- `POST http://127.0.0.1:5000/loans`
- `GET http://127.0.0.1:5000/loans`
- `GET http://127.0.0.1:5000/loans?borrowerName=<borrowerName>`
- `GET http://127.0.0.1:5000/loans/<loanId>`
- `DELETE http://127.0.0.1:5000/loans/<loanId>`
- `GET http://127.0.0.1:5000/health`
- Responsive single-page browser workflow for create, list, borrower search,
  loan ID lookup, and loan deletion
- Runtime loan storage for local demos
- pytest coverage gate at 80%

Out of scope:

- Auth0 or authentication
- Durable persistence
- Public exposure
- Container registry work
- Cloud or Kubernetes deployment

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
flask --app app run --debug
```

The website runs at `http://127.0.0.1:5000/`. The API runs from the same Flask
app under the routes listed above.

## Website Demo Flow

Open `http://127.0.0.1:5000/` in a browser.

1. Confirm the current-loans section shows an empty current-list message in a
   fresh session.
2. Create loan `LN-001` for borrower `Jane Smith` with funding amount `1000.0`
   and repayment amount `1200.0`.
3. Confirm the success message identifies `LN-001` and the current loans list
   includes it.
4. Create `LN-001` again and confirm duplicate-loan feedback appears while the
   entered values remain available for correction.
5. Search borrower name `Jane Smith`, then search `No Match` and confirm the
   empty-result state.
6. Look up loan ID `LN-001`, then look up `LN-MISSING` and confirm not-found
   feedback.
7. Delete loan ID `LN-001`, then delete it again and confirm the deleted-loan
   confirmation followed by not-found feedback.
8. Resize the browser to a mobile-sized width and confirm forms, buttons,
   result rows, and feedback remain readable without horizontal scrolling.

Primary success and error feedback is expected to appear within 2 seconds in
local usage. If the Flask app is stopped while the page is open, the next action
shows service-unavailable feedback and keeps entered values available for retry.

## Health Check

```bash
curl http://127.0.0.1:5000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

## Demo: Empty Loan List

```bash
curl -i http://127.0.0.1:5000/loans
```

Expected result: `200 OK` with an empty collection when no loans exist:

```json
{
  "loans": []
}
```

## Demo: Create a Loan

```bash
curl -i -X POST http://127.0.0.1:5000/loans \
  -H "Content-Type: application/json" \
  -d '{
    "loanId": "LN-001",
    "borrowerName": "Jane Smith",
    "fundingAmount": 1000.0,
    "repaymentAmount": 1200.0
  }'
```

Expected result: `201 Created` with the stored loan record:

```json
{
  "borrowerName": "Jane Smith",
  "fundingAmount": 1000.0,
  "loanId": "LN-001",
  "repaymentAmount": 1200.0
}
```

## Demo: Duplicate Loan

Run the same create request again.

Expected result: `409 Conflict`:

```json
{
  "error": "duplicate_loan_id",
  "message": "A loan with this loan ID already exists."
}
```

## Demo: Look Up a Loan

```bash
curl -i http://127.0.0.1:5000/loans/LN-001
```

Expected result: `200 OK` with the stored loan record:

```json
{
  "borrowerName": "Jane Smith",
  "fundingAmount": 1000.0,
  "loanId": "LN-001",
  "repaymentAmount": 1200.0
}
```

## Demo: List Current Loans

```bash
curl -i http://127.0.0.1:5000/loans
```

Expected result: `200 OK` with the current loan collection:

```json
{
  "loans": [
    {
      "borrowerName": "Jane Smith",
      "fundingAmount": 1000.0,
      "loanId": "LN-001",
      "repaymentAmount": 1200.0
    }
  ]
}
```

## Demo: Look Up Loans By Borrower Name

```bash
curl -i "http://127.0.0.1:5000/loans?borrowerName=Jane%20Smith"
```

Expected result: `200 OK` with current loans for that borrower:

```json
{
  "loans": [
    {
      "borrowerName": "Jane Smith",
      "fundingAmount": 1000.0,
      "loanId": "LN-001",
      "repaymentAmount": 1200.0
    }
  ]
}
```

## Demo: No Borrower Matches

```bash
curl -i "http://127.0.0.1:5000/loans?borrowerName=No%20Match"
```

Expected result: `200 OK` with an empty collection:

```json
{
  "loans": []
}
```

## Demo: Blank Borrower Name Lookup

```bash
curl -i "http://127.0.0.1:5000/loans?borrowerName="
```

Expected result: `400 Bad Request`:

```json
{
  "details": [
    {
      "field": "borrowerName",
      "message": "borrowerName is required."
    }
  ],
  "error": "validation_error",
  "message": "borrowerName is required."
}
```

## Demo: Delete a Loan

```bash
curl -i -X DELETE http://127.0.0.1:5000/loans/LN-001
```

Expected result: `200 OK` with the deleted loan record:

```json
{
  "borrowerName": "Jane Smith",
  "fundingAmount": 1000.0,
  "loanId": "LN-001",
  "repaymentAmount": 1200.0
}
```

After deletion, lookup and listing workflows no longer include `LN-001`:

```bash
curl -i http://127.0.0.1:5000/loans/LN-001
curl -i http://127.0.0.1:5000/loans
curl -i "http://127.0.0.1:5000/loans?borrowerName=Jane%20Smith"
```

Expected results: loan ID lookup returns `404 Not Found`; full listing and
borrower-name lookup return `200 OK` without the deleted loan.

## Demo: Already Deleted or Missing Loan

```bash
curl -i -X DELETE http://127.0.0.1:5000/loans/LN-001
curl -i -X DELETE http://127.0.0.1:5000/loans/LN-MISSING
```

Expected result for each request: `404 Not Found`:

```json
{
  "error": "loan_not_found",
  "message": "No loan exists for this loan ID."
}
```

## Demo: Missing Loan Lookup

```bash
curl -i http://127.0.0.1:5000/loans/LN-MISSING
```

Expected result: `404 Not Found`:

```json
{
  "error": "loan_not_found",
  "message": "No loan exists for this loan ID."
}
```

## Demo: Restart Behavior

Stop the Flask server with `Ctrl-C`, start it again, and list or delete loans
before creating another record. You can also run the borrower-name lookup
request.

Expected listing result: `200 OK` with `{"loans": []}` after the local runtime
store resets. Expected borrower-name lookup result is also `{"loans": []}`.
Deleting a loan from a previous run returns `404 Not Found`. Running the same
create request again returns `201 Created`.

## Demo: Validation Error

```bash
curl -i -X POST http://127.0.0.1:5000/loans \
  -H "Content-Type: application/json" \
  -d '{
    "loanId": "LN-002",
    "borrowerName": "Jane Smith",
    "fundingAmount": 0,
    "repaymentAmount": 1200.0
  }'
```

Expected result: `400 Bad Request`:

```json
{
  "details": [
    {
      "field": "fundingAmount",
      "message": "fundingAmount must be greater than 0."
    }
  ],
  "error": "validation_error",
  "message": "Loan could not be created because one or more fields are invalid."
}
```

## Test

```bash
pytest --cov=app --cov-report=term-missing --cov-fail-under=80
```

Expected result: all tests pass and statement coverage is at least 80%.

Latest local result: `76 passed`, total coverage `91.80%`.

## Architecture

- `app/routes.py`: HTTP routes, request parsing, and JSON responses.
- `app/templates/index.html`: single-page browser website.
- `app/static/loan_website.css`: responsive website styling.
- `app/static/loan_website.js`: browser Fetch API workflow handling.
- `app/models/loan.py`: immutable loan data shape and JSON serialization.
- `app/services/loan_service.py`: validation, normalization, duplicate checks,
  Decimal parsing, lookup, listing, borrower-name search, deletion, and
  runtime storage.
- `tests/unit/`: service-level validation and storage tests.
- `tests/integration/`: Flask API, website, and documentation smoke tests.

## Trade-Offs and Assumptions

- Loan IDs are caller-supplied, trimmed before storage, and case-sensitive.
- Lookup uses the same trimmed, case-sensitive loan ID rules as creation.
- Deletion uses trimmed, case-sensitive loan ID matching and returns the deleted
  loan record.
- Deleted loans are removed from loan ID lookup, borrower-name lookup, and full
  listing.
- Listing returns all current loans in storage order without sorting controls.
- Borrower names are trimmed before storage.
- Borrower-name lookup trims the search term and matches stored borrower names
  exactly and case-sensitively.
- A missing `borrowerName` query lists all current loans; a blank `borrowerName`
  query is rejected as validation error.
- Funding and repayment amounts must be valid monetary values greater than 0.
- Amounts are parsed with `Decimal` internally and returned as JSON numbers.
- Storage is process-local and resets when the application starts again.
- Local Flask deployment is enough for this first API slice.
