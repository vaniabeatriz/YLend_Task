# Quickstart: Loan Listing

This quickstart validates the listing workflow locally. Because storage is
temporary and in-memory, create loans in the same server session before listing
them.

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

## Empty Listing

```bash
curl -i http://127.0.0.1:5000/loans
```

Expected result: `200 OK` with an empty collection when no loans exist:

```json
{
  "loans": []
}
```

## Seed Loans for Listing

```bash
curl -i -X POST http://127.0.0.1:5000/loans \
  -H "Content-Type: application/json" \
  -d '{
    "loanId": "LN-001",
    "borrowerName": "Jane Smith",
    "fundingAmount": 1000.0,
    "repaymentAmount": 1200.0
  }'

curl -i -X POST http://127.0.0.1:5000/loans \
  -H "Content-Type: application/json" \
  -d '{
    "loanId": "LN-002",
    "borrowerName": "Alex Doe",
    "fundingAmount": 500.0,
    "repaymentAmount": 650.0
  }'
```

Expected result for each request: `201 Created` with the stored loan record in
the response body.

## List Current Loans

```bash
curl -i http://127.0.0.1:5000/loans
```

Expected result: `200 OK` with all current loans:

```json
{
  "loans": [
    {
      "borrowerName": "Jane Smith",
      "fundingAmount": 1000.0,
      "loanId": "LN-001",
      "repaymentAmount": 1200.0
    },
    {
      "borrowerName": "Alex Doe",
      "fundingAmount": 500.0,
      "loanId": "LN-002",
      "repaymentAmount": 650.0
    }
  ]
}
```

## Restart Behavior

Stop the Flask server with `Ctrl-C`, start it again, and run the listing request
without creating loans again.

Expected result: `200 OK` with an empty collection, because loans are stored only
in memory for the current application session.

## Run Tests

```bash
pytest --cov=app --cov-report=term-missing --cov-fail-under=80
```

Expected result: tests pass and statement coverage is at least 80%.

## Scope Notes

- Listing retrieves all current loans exactly once.
- Listing uses the current storage order and does not add sorting controls.
- Loan deletion, filtering, searching, pagination, persistence, browser UI,
  authentication, public exposure, and cloud deployment are out of scope.
