# Quickstart: Durable Loan Persistence

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Auth0 Configuration

This slice preserves the existing Auth0 flow. Use the same local Auth0 values
from the authentication slice:

```bash
export AUTH0_DOMAIN="your-tenant.auth0.com"
export AUTH0_CLIENT_ID="your-client-id"
export AUTH0_CLIENT_SECRET="your-client-secret"
export AUTH0_AUDIENCE="https://your-loan-api"
export AUTH0_CALLBACK_URL="http://127.0.0.1:5000/callback"
export AUTH0_LOGOUT_RETURN_URL="http://127.0.0.1:5000/"
export APP_SECRET_KEY="$(openssl rand -hex 32)"
```

## Persistence Configuration

By default, the app stores durable local loans in the Flask instance directory.
For a predictable demo path, set an explicit local database path:

```bash
export LOAN_DATABASE_PATH="instance/loans.sqlite3"
```

The app prepares loan storage automatically on startup. To reset the local demo
data, stop Flask and remove the local database file.

## Run

```bash
flask --app app run --debug
```

The website runs at `http://127.0.0.1:5000/`.

## Test

Automated tests use isolated temporary database files and mocked Auth0 sessions
and tokens. They do not require live Auth0 credentials.

```bash
pytest --cov=app --cov-report=term-missing --cov-fail-under=80
```

If the virtual environment is not activated:

```bash
.venv/bin/python -m pytest --cov=app --cov-report=term-missing --cov-fail-under=80
```

Latest local result: `115 passed`; total coverage `87.65%`.

## Website Restart Demo

1. Start Flask.
2. Open `http://127.0.0.1:5000/`.
3. Sign in with Auth0.
4. Create loan `LN-001` for borrower `Jane Smith` with funding amount `1000.0`
   and repayment amount `1200.0`.
5. List loans and confirm `LN-001` appears.
6. Stop Flask with `Ctrl-C`.
7. Start Flask again with the same `LOAN_DATABASE_PATH`.
8. Sign in again if needed.
9. List loans, search borrower `Jane Smith`, and look up loan ID `LN-001`.
10. Confirm `LN-001` is still available after restart.
11. Delete `LN-001`, restart Flask again, and confirm lookup returns not-found
    while listing/search do not include the deleted loan.

## Protected API Restart Demo

After signing in, obtain a valid Auth0 access token for the configured API
audience:

```bash
export TOKEN="paste-auth0-access-token-here"
```

Create a durable loan:

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

Restart Flask with the same `LOAN_DATABASE_PATH`, then verify persistence:

```bash
curl -i http://127.0.0.1:5000/loans/LN-001 \
  -H "Authorization: Bearer $TOKEN"

curl -i http://127.0.0.1:5000/loans \
  -H "Authorization: Bearer $TOKEN"

curl -i "http://127.0.0.1:5000/loans?borrowerName=Jane%20Smith" \
  -H "Authorization: Bearer $TOKEN"
```

Expected result: each request returns `200 OK`; lookup returns `LN-001`, and
listing/search include `LN-001`.

Delete and verify durable removal:

```bash
curl -i -X DELETE http://127.0.0.1:5000/loans/LN-001 \
  -H "Authorization: Bearer $TOKEN"
```

Restart Flask again with the same `LOAN_DATABASE_PATH`, then verify lookup
returns `404 Not Found` and listing/search no longer include `LN-001`.

## Out Of Scope

- Auth0 changes
- Roles or per-user loan ownership
- Public deployment
- Container registry work
- Kubernetes
- Cloud infrastructure
- Managed database services
