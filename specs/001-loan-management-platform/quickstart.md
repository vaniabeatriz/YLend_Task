# Quickstart: Create Loan

This quickstart validates the first Create Loan API slice locally.

## Prerequisites

- Python 3.11+
- A shell with `python3` and `pip`

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run Locally

```bash
flask --app app run --debug
```

The application should listen on `http://127.0.0.1:5000`.

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

## Create a Loan

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

Expected result: `201 Created` with the stored loan record in the response body:

```json
{
  "borrowerName": "Jane Smith",
  "fundingAmount": 1000.0,
  "loanId": "LN-001",
  "repaymentAmount": 1200.0
}
```

## Duplicate Loan Check

Run the same create request again.

Expected result: `409 Conflict` with a clear duplicate-loan message:

```json
{
  "error": "duplicate_loan_id",
  "message": "A loan with this loan ID already exists."
}
```

## Restart Behavior

Stop the Flask server with `Ctrl-C`, start it again, and run the same create
request once more.

Expected result: `201 Created`, because loans are stored only in memory for the
current application session.

## Validation Check

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

Expected result: `400 Bad Request` with a clear validation message:

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

## Run Tests

```bash
pytest --cov=app --cov-report=term-missing --cov-fail-under=80
```

Expected result: tests pass and statement coverage is at least 80%.

## Architecture Notes

- `app/routes.py` owns HTTP request and response handling.
- `app/models/loan.py` owns the loan data shape.
- `app/services/loan_service.py` owns validation, normalization, duplicate
  checks, and in-memory storage.
- Storage is process-local and intentionally disappears when the application
  restarts.

## Out of Scope for This Slice

- Browser UI
- Loan lookup
- Loan listing
- Loan deletion
- Authentication
- Public exposure
- Cloud-hosted deployment
- Kubernetes or Helm deployment
