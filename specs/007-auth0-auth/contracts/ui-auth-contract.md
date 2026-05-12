# UI/Auth Contract: Auth0 Authentication

## Public Browser Entry Point

### `GET /`

Returns the single-page loan-management website.

Signed-out state:

- Shows the service title and short summary.
- Shows a clear sign-in action.
- Does not show or enable create, list, borrower-name search, loan ID lookup, or
  delete workflows.
- Health check remains available.

Signed-in state:

- Shows user/session status and sign-out action.
- Shows action buttons: Create loan, List loans, Search borrower, Look up loan,
  Delete loan, Health check.
- Opens workflow forms only after their action button is selected.
- Calls protected loan APIs with `Authorization: Bearer <access-token>`.

Setup-error state:

- If Auth0 configuration is missing, the website still renders.
- Sign-in or protected-flow attempts show a clear setup error explaining which
  local configuration is missing.

## Auth Routes

### `GET /login`

Starts Auth0 sign-in.

Expected behaviour:

- If Auth0 configuration is valid, redirects to Auth0 Universal Login.
- If configuration is missing or invalid, returns a clear setup error without
  exposing secrets.

### `GET /callback`

Handles Auth0 callback.

Expected behaviour:

- On success, stores the authenticated user profile and access token in Flask
  session state, then redirects to `/`.
- On failure, clears partial auth state and shows recovery guidance.

### `GET /logout`

Signs out.

Expected behaviour:

- Clears local Flask session.
- Redirects through Auth0 logout when configuration is present.
- Returns to `/` with loan workflows hidden.

### `GET /auth/status`

Returns website authentication state for the page JavaScript.

Signed-out response:

```json
{
  "authenticated": false,
  "user": null,
  "accessToken": null,
  "setupError": null
}
```

Signed-in response:

```json
{
  "authenticated": true,
  "user": {
    "name": "Jane Reviewer",
    "email": "jane@example.com"
  },
  "accessToken": "eyJ...",
  "setupError": null
}
```

Setup-error response:

```json
{
  "authenticated": false,
  "user": null,
  "accessToken": null,
  "setupError": "Please sign in or register to continue."
}
```

## Protected API Interaction

The website must include the Auth0 access token from authenticated state when
calling loan endpoints:

```http
Authorization: Bearer <access-token>
```

Authentication failure handling:

- `401` JSON with `authentication_required` or `invalid_token` shows a sign-in
  or re-authentication message.
- The website must not display stale loan data as if the failed action
  succeeded.
- Existing validation, duplicate, not-found, empty, and service-unavailable
  feedback remains unchanged after authentication succeeds.

## Session Cookie Contract

Flask session cookies:

- HttpOnly
- SameSite=Lax
- Secure when served over HTTPS

No separate CSRF token checks are added in this slice.

## Out Of Scope

- Durable persistence
- Public deployment
- Container registry work
- Kubernetes or Helm
- Cloud infrastructure
- Roles, scopes, or per-user loan permissions
- Separate frontend application build or deployment pipeline
