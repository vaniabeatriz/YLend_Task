# Quickstart: Loan Deletion

This quickstart validates the delete-by-loan-ID workflow locally. Because
storage is temporary and in-memory, create loans in the same server session
before deleting them.

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

## Seed Loans For Deletion

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
    "borrowerName": "Jane Smith",
    "fundingAmount": 700.0,
    "repaymentAmount": 850.0
  }'
```

Expected result for each request: `201 Created` with the stored loan record in
the response body.

## Delete A Loan

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

## Confirm Deleted Loan Is Absent

```bash
curl -i http://127.0.0.1:5000/loans/LN-001
curl -i http://127.0.0.1:5000/loans
curl -i "http://127.0.0.1:5000/loans?borrowerName=Jane%20Smith"
```

Expected results:

- Loan ID lookup for `LN-001`: `404 Not Found`.
- Full listing: `200 OK` without `LN-001`.
- Borrower-name lookup: `200 OK` without `LN-001` and with any remaining Jane
  Smith loans.

## Missing Or Already Deleted Loan

```bash
curl -i -X DELETE http://127.0.0.1:5000/loans/LN-001
curl -i -X DELETE http://127.0.0.1:5000/loans/LN-MISSING
```

Expected result for each request: `404 Not Found` with a clear no-loan message.

## Restart Behavior

Stop the Flask server with `Ctrl-C`, start it again, and run the delete request
without creating loans again.

Expected result: `404 Not Found`, because loans are stored only in memory for
the current application session.

## Run Tests

```bash
pytest --cov=app --cov-report=term-missing --cov-fail-under=80
```

Expected result: tests pass and statement coverage is at least 80%.

## Scope Notes

- Deletion removes one current loan by exact case-sensitive loan ID after
  trimming the supplied ID.
- Successful deletion returns the deleted loan record.
- Loan creation, loan ID lookup, borrower-name lookup, and full listing remain
  available and reflect the removed loan.
- Persistence, authentication, browser UI, public exposure, cloud deployment,
  and infrastructure changes are out of scope.
