# Loan API

Small Flask API slice for the YouLend technical task. This implementation
covers creating, looking up, and listing temporary loan records.

## Scope

Included:

- `POST http://127.0.0.1:5000/loans`
- `GET http://127.0.0.1:5000/loans`
- `GET http://127.0.0.1:5000/loans/<loanId>`
- `GET http://127.0.0.1:5000/health`
- In-memory loan storage for the current application session
- pytest coverage gate at 80%

Out of scope:

- Browser UI
- Loan deletion
- Authentication
- Public exposure
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

The API runs at `http://127.0.0.1:5000`.

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

Expected result: `200 OK` with the current in-memory loan collection:

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

## Demo: Duplicate Loan

Run the same create request again.

Expected result: `409 Conflict`:

```json
{
  "error": "duplicate_loan_id",
  "message": "A loan with this loan ID already exists."
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

Stop the Flask server with `Ctrl-C`, start it again, and list loans before
creating another record.

Expected listing result: `200 OK` with `{"loans": []}`, because loans are stored
only in memory for the current application session. Running the same create
request again returns `201 Created`.

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

Latest local result: `42 passed`, total coverage `91%`.

## Architecture

- `app/routes.py`: HTTP routes, request parsing, and JSON responses.
- `app/models/loan.py`: immutable loan data shape and JSON serialization.
- `app/services/loan_service.py`: validation, normalization, duplicate checks,
  Decimal parsing, lookup, listing, and in-memory storage.
- `tests/unit/`: service-level validation and storage tests.
- `tests/integration/`: Flask API and documentation smoke tests.

## Trade-Offs and Assumptions

- Loan IDs are caller-supplied, trimmed before storage, and case-sensitive.
- Lookup uses the same trimmed, case-sensitive loan ID rules as creation.
- Listing returns all current loans in storage order without sorting controls.
- Borrower names are trimmed before storage.
- Funding and repayment amounts must be valid monetary values greater than 0.
- Amounts are parsed with `Decimal` internally and returned as JSON numbers.
- Storage is process-local and disappears when the application restarts.
- Local Flask deployment is enough for this first API slice.
