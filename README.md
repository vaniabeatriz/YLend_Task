# Loan Management API and Website

Small Flask implementation for the YouLend technical task. It provides a
single-page local website plus authenticated JSON API operations for creating,
looking up, listing, searching, and deleting loan records.

## Scope

Included:

- `GET http://127.0.0.1:5000/`
- `GET http://127.0.0.1:5000/login`
- `GET http://127.0.0.1:5000/callback`
- `GET http://127.0.0.1:5000/logout`
- `GET http://127.0.0.1:5000/auth/status`
- `POST http://127.0.0.1:5000/loans`
- `GET http://127.0.0.1:5000/loans`
- `GET http://127.0.0.1:5000/loans?borrowerName=<borrowerName>`
- `GET http://127.0.0.1:5000/loans/<loanId>`
- `DELETE http://127.0.0.1:5000/loans/<loanId>`
- `GET http://127.0.0.1:5000/health`
- Auth0 sign-in for the website
- Auth0 bearer-token protection for loan API endpoints
- Responsive single-page browser workflow for create, list, borrower search,
  loan ID lookup, and loan deletion
- Durable local SQLite loan storage for local demos
- pytest coverage gate at 80%

Out of scope:

- Public exposure
- Container registry work
- Cloud or Kubernetes deployment

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Auth0 Configuration

Create or select an Auth0 Regular Web Application and an Auth0 API.

Set the Auth0 application URLs for local Flask:

- Allowed Callback URLs: `http://127.0.0.1:5000/callback`
- Allowed Logout URLs: `http://127.0.0.1:5000/`
- Allowed Web Origins: `http://127.0.0.1:5000`

Set the Auth0 API signing algorithm to RS256 and use its identifier as the API
audience.

Create a local `.env` file or export these values before running Flask:

```bash
export AUTH0_DOMAIN="your-tenant.auth0.com"
export AUTH0_CLIENT_ID="your-client-id"
export AUTH0_CLIENT_SECRET="your-client-secret"
export AUTH0_AUDIENCE="https://your-loan-api"
export AUTH0_CALLBACK_URL="http://127.0.0.1:5000/callback"
export AUTH0_LOGOUT_RETURN_URL="http://127.0.0.1:5000/"
export APP_SECRET_KEY="$(openssl rand -hex 32)"
```

Local `.env` files are ignored by `.gitignore`. The app still starts without
Auth0 values: `/health` and `/` remain public, while sign-in and protected API
flows show setup guidance instead of exposing loan data.

## Persistence Configuration

Loans are stored in a local SQLite database so created records survive Flask app
restarts. By default, the database lives in the Flask instance directory. For a
predictable local demo path, set:

```bash
export LOAN_DATABASE_PATH="instance/loans.sqlite3"
```

The app prepares the database and loan table automatically on startup. To reset
local demo data, stop Flask and remove the configured SQLite file.

## Run

```bash
flask --app app run --debug
```

The website runs at `http://127.0.0.1:5000/`. The API runs from the same Flask
app under the routes listed above.

## Website Demo Flow

Open `http://127.0.0.1:5000/` in a browser.

1. Confirm the signed-out page shows a sign-in action and hides create, list,
   borrower search, loan lookup, and delete workflows.
2. Sign in with Auth0.
3. Confirm the signed-in page shows the action buttons: Create loan, List
   loans, Search borrower, Look up loan, Delete loan, and Health check.
4. Create loan `LN-001` for borrower `Jane Smith` with funding amount `1000.0`
   and repayment amount `1200.0`.
5. Confirm the success message identifies `LN-001` and the current loans list
   includes it.
6. Create `LN-001` again and confirm duplicate-loan feedback appears while the
   entered values remain available for correction.
7. Search borrower name `Jane Smith`, then search `No Match` and confirm the
   empty-result state.
8. Look up loan ID `LN-001`, then look up `LN-MISSING` and confirm not-found
   feedback.
9. Delete loan ID `LN-001`, then delete it again and confirm the deleted-loan
   confirmation followed by not-found feedback.
10. Sign out and confirm loan workflows are hidden again.
11. Resize the browser to a mobile-sized width and confirm forms, buttons,
   result rows, and feedback remain readable without horizontal scrolling.

Primary success and error feedback is expected to appear within 2 seconds in
local usage. If the Flask app is stopped while the page is open, the next action
shows service-unavailable feedback and keeps entered values available for retry.

## Health Check

Health stays public:

```bash
curl http://127.0.0.1:5000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

## Protected API Authentication

Requests to loan endpoints without an Auth0 access token fail with `401`
JSON and no loan data:

```bash
curl -i http://127.0.0.1:5000/loans
```

Expected result:

```json
{
  "error": "authentication_required",
  "message": "A valid Auth0 access token is required."
}
```

After signing in, obtain a valid Auth0 access token for the configured API
audience. Use it as `TOKEN`:

```bash
export TOKEN="paste-auth0-access-token-here"
```

All `/loans` examples below require this header:

```bash
-H "Authorization: Bearer $TOKEN"
```

## Demo: Empty Loan List

```bash
curl -i http://127.0.0.1:5000/loans \
  -H "Authorization: Bearer $TOKEN"
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
  -H "Authorization: Bearer $TOKEN" \
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

Run the same authenticated create request again.

Expected result: `409 Conflict`:

```json
{
  "error": "duplicate_loan_id",
  "message": "A loan with this loan ID already exists."
}
```

## Demo: Look Up a Loan

```bash
curl -i http://127.0.0.1:5000/loans/LN-001 \
  -H "Authorization: Bearer $TOKEN"
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
curl -i http://127.0.0.1:5000/loans \
  -H "Authorization: Bearer $TOKEN"
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
curl -i "http://127.0.0.1:5000/loans?borrowerName=Jane%20Smith" \
  -H "Authorization: Bearer $TOKEN"
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
curl -i "http://127.0.0.1:5000/loans?borrowerName=No%20Match" \
  -H "Authorization: Bearer $TOKEN"
```

Expected result: `200 OK` with an empty collection:

```json
{
  "loans": []
}
```

## Demo: Blank Borrower Name Lookup

```bash
curl -i "http://127.0.0.1:5000/loans?borrowerName=" \
  -H "Authorization: Bearer $TOKEN"
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
curl -i -X DELETE http://127.0.0.1:5000/loans/LN-001 \
  -H "Authorization: Bearer $TOKEN"
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
curl -i http://127.0.0.1:5000/loans/LN-001 \
  -H "Authorization: Bearer $TOKEN"
curl -i http://127.0.0.1:5000/loans \
  -H "Authorization: Bearer $TOKEN"
curl -i "http://127.0.0.1:5000/loans?borrowerName=Jane%20Smith" \
  -H "Authorization: Bearer $TOKEN"
```

Expected results: loan ID lookup returns `404 Not Found`; full listing and
borrower-name lookup return `200 OK` without the deleted loan.

## Demo: Already Deleted or Missing Loan

```bash
curl -i -X DELETE http://127.0.0.1:5000/loans/LN-001 \
  -H "Authorization: Bearer $TOKEN"
curl -i -X DELETE http://127.0.0.1:5000/loans/LN-MISSING \
  -H "Authorization: Bearer $TOKEN"
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
curl -i http://127.0.0.1:5000/loans/LN-MISSING \
  -H "Authorization: Bearer $TOKEN"
```

Expected result: `404 Not Found`:

```json
{
  "error": "loan_not_found",
  "message": "No loan exists for this loan ID."
}
```

## Demo: Restart Behavior

Stop the Flask server with `Ctrl-C`, start it again, sign in, and list or
delete loans before creating another record. You can also run the borrower-name
lookup request.

Expected result after restart with the same `LOAN_DATABASE_PATH`: lookup,
listing, and borrower-name search still include loans created before restart.
Deleting a loan removes it from the SQLite database, so it remains absent after
later restarts. Running the same create request again for an existing loan ID
returns `409 Conflict`.

## Demo: Validation Error

```bash
curl -i -X POST http://127.0.0.1:5000/loans \
  -H "Authorization: Bearer $TOKEN" \
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

Latest local result: `115 passed`; total coverage `87.65%`.

## Architecture

- `app/auth.py`: Auth0 configuration, login/logout helpers, JWT validation,
  session handling, and auth error responses.
- `app/routes.py`: HTTP routes, request parsing, auth gates, and JSON
  responses.
- `app/repositories/loan_repository.py`: SQLite schema initialization and
  durable loan storage.
- `app/templates/index.html`: single-page browser website.
- `app/static/loan_website.css`: responsive website styling.
- `app/static/loan_website.js`: browser Fetch API workflow handling and
  authenticated request headers.
- `app/models/loan.py`: immutable loan data shape and JSON serialization.
- `app/services/loan_service.py`: validation, normalization, duplicate checks,
  Decimal parsing, lookup, listing, borrower-name search, deletion, and
  repository coordination.
- `tests/unit/`: repository, service-level validation, storage, and auth tests.
- `tests/integration/`: Flask API, website, auth, and documentation smoke
  tests.

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
- Amounts are parsed with `Decimal` internally, stored as decimal text in
  SQLite, and returned as JSON numbers.
- SQLite storage is local to the configured database path and survives Flask app
  restarts using that same path.
- Auth0 login and JWT verification are mocked in automated tests so the suite
  does not require live Auth0 credentials or network access.
- The website reads the Auth0 access token from authenticated status for local
  same-origin API calls; production token/session hardening is deferred with
  public deployment.
- Missing Auth0 configuration is reported through setup guidance while public
  routes remain available.
- Local Flask deployment is enough for this slice.
