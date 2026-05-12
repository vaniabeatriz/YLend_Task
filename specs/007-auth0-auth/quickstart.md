# Quickstart: Auth0 Authentication

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Auth0 Configuration For Manual Demo

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
export APP_SECRET_KEY="$(openssl rand -hex 32)"
```

The app must still start without these values. In that case, `/health` and `/`
remain available, and sign-in/protected flows show setup guidance.

## Run

```bash
flask --app app run --debug
```

The website runs at `http://127.0.0.1:5000/`.

## Test

Automated tests use mocked Auth0 sessions and bearer-token verification. They
do not require live Auth0 credentials or network access.

```bash
pytest --cov=app --cov-report=term-missing --cov-fail-under=80
```

If the virtual environment is not activated, run the same command through the
local interpreter:

```bash
.venv/bin/python -m pytest --cov=app --cov-report=term-missing --cov-fail-under=80
```

## Website Demo Flow

Open `http://127.0.0.1:5000/`.

1. Confirm the signed-out page shows a sign-in action and hides create, list,
   borrower search, loan lookup, and delete workflows.
2. Sign in with Auth0.
3. Confirm the signed-in page shows the action buttons.
4. Create loan `LN-001` for borrower `Jane Smith` with funding amount `1000.0`
   and repayment amount `1200.0`.
5. List loans and confirm `LN-001` appears.
6. Search borrower name `Jane Smith`, then search `No Match` and confirm the
   empty-result state.
7. Look up loan ID `LN-001`, then look up `LN-MISSING` and confirm not-found
   feedback.
8. Delete loan ID `LN-001`, then delete it again and confirm deleted-loan
   confirmation followed by not-found feedback.
9. Sign out and confirm loan workflows are hidden again.

## Protected API Demo

Requests without an Auth0 access token fail with `401` JSON and no loan data:

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

Create a loan:

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

List loans:

```bash
curl -i http://127.0.0.1:5000/loans \
  -H "Authorization: Bearer $TOKEN"
```

Search by borrower name:

```bash
curl -i "http://127.0.0.1:5000/loans?borrowerName=Jane%20Smith" \
  -H "Authorization: Bearer $TOKEN"
```

Look up by loan ID:

```bash
curl -i http://127.0.0.1:5000/loans/LN-001 \
  -H "Authorization: Bearer $TOKEN"
```

Delete by loan ID:

```bash
curl -i -X DELETE http://127.0.0.1:5000/loans/LN-001 \
  -H "Authorization: Bearer $TOKEN"
```

## Health Check

Health stays public:

```bash
curl -i http://127.0.0.1:5000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

## Out Of Scope

- Durable persistence
- Public deployment
- Container registry work
- Kubernetes
- Cloud infrastructure
- Roles, scopes, or per-user loan ownership
