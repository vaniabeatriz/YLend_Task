# Quickstart: Loan Lookup

This quickstart validates the lookup workflow locally. Because storage is
temporary and in-memory, create a loan in the same server session before looking
it up.

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

## Seed a Loan for Lookup

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

Expected result: `201 Created` with the stored loan record in the response body.

## Look Up a Loan

```bash
curl -i http://127.0.0.1:5000/loans/LN-001
```

Expected result: `200 OK` with the stored loan record in the response body:

```json
{
  "borrowerName": "Jane Smith",
  "fundingAmount": 1000.0,
  "loanId": "LN-001",
  "repaymentAmount": 1200.0
}
```

## Missing Loan Lookup

```bash
curl -i http://127.0.0.1:5000/loans/LN-MISSING
```

Expected result: `404 Not Found` with a clear missing-loan message:

```json
{
  "error": "loan_not_found",
  "message": "No loan exists for this loan ID."
}
```

## Restart Behavior

Stop the Flask server with `Ctrl-C`, start it again, and run the lookup request
for `LN-001` without creating it again.

Expected result: `404 Not Found`, because loans are stored only in memory for
the current application session.

## Run Tests

```bash
pytest --cov=app --cov-report=term-missing --cov-fail-under=80
```

Expected result: tests pass and statement coverage is at least 80%.

## Scope Notes

- Lookup retrieves one current loan by loan ID.
- Lookup trims surrounding whitespace and remains case-sensitive.
- Loan listing, deletion, persistence, browser UI, authentication, public
  exposure, and cloud deployment are out of scope.
