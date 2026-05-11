# Quickstart: Borrower Name Loan Lookup

This quickstart validates the borrower-name lookup workflow locally. Because
storage is temporary and in-memory, create loans in the same server session
before searching for them.

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

## Seed Loans For Borrower Lookup

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

curl -i -X POST http://127.0.0.1:5000/loans \
  -H "Content-Type: application/json" \
  -d '{
    "loanId": "LN-003",
    "borrowerName": "Jane Smith",
    "fundingAmount": 700.0,
    "repaymentAmount": 850.0
  }'
```

Expected result for each request: `201 Created` with the stored loan record in
the response body.

## Search By Borrower Name

```bash
curl -i "http://127.0.0.1:5000/loans?borrowerName=Jane%20Smith"
```

Expected result: `200 OK` with only loans for that borrower:

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
      "borrowerName": "Jane Smith",
      "fundingAmount": 700.0,
      "loanId": "LN-003",
      "repaymentAmount": 850.0
    }
  ]
}
```

## No Borrower Matches

```bash
curl -i "http://127.0.0.1:5000/loans?borrowerName=No%20Match"
```

Expected result: `200 OK` with an empty collection:

```json
{
  "loans": []
}
```

## Blank Borrower Name

```bash
curl -i "http://127.0.0.1:5000/loans?borrowerName="
```

Expected result: `400 Bad Request` with a validation message explaining that
borrowerName is required.

## Existing Listing Still Works

```bash
curl -i http://127.0.0.1:5000/loans
```

Expected result: `200 OK` with all current loans.

## Restart Behavior

Stop the Flask server with `Ctrl-C`, start it again, and run the borrower-name
lookup request without creating loans again.

Expected result: `200 OK` with an empty collection, because loans are stored only
in memory for the current application session.

## Run Tests

```bash
pytest --cov=app --cov-report=term-missing --cov-fail-under=80
```

Expected result: tests pass and statement coverage is at least 80%.

## Scope Notes

- Borrower-name lookup retrieves all current loans with an exact
  case-sensitive borrower-name match after trimming the search term.
- Borrower-name lookup uses the current storage order and does not add sorting
  controls.
- Loan deletion, partial search, pagination, persistence, browser UI,
  authentication, public exposure, and cloud deployment are out of scope.
