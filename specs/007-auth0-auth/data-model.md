# Data Model: Auth0 Authentication

This slice adds authentication state and token validation concepts around the
existing loan model. It does not add durable persistence or change loan fields.

## Existing Entity: Loan

Fields are unchanged:

- `loanId`: trimmed, non-empty, case-sensitive unique string
- `borrowerName`: trimmed, non-empty string
- `fundingAmount`: positive number
- `repaymentAmount`: positive number

Authentication impact:

- Create, list, borrower-name search, loan ID lookup, and delete require a valid
  Auth0 bearer access token.
- After authentication succeeds, all existing loan validation, duplicate,
  empty-result, lookup, and deletion behaviours remain unchanged.

## Authenticated User

Represents the signed-in website reviewer.

Fields:

- `sub`: Auth0 subject identifier from ID token/userinfo
- `name`: optional display name
- `email`: optional email address
- `picture`: optional profile image URL, if provided by Auth0

Relationships:

- One authenticated user has at most one active website authentication session
  in the current browser.
- Users do not own loans in this slice; all authenticated users share the same
  loan-management permissions.

Validation rules:

- A user is authenticated for website UI purposes only after a successful Auth0
  callback stores trusted user/session data.
- Roles, permissions, and per-user loan ownership are out of scope.

## Authentication Session

Represents the Flask session state created after Auth0 sign-in.

Fields:

- `user`: authenticated user profile subset
- `access_token`: Auth0 access token requested for the configured API audience
- `expires_at`: optional token/session expiry timestamp when available

Validation rules:

- Session cookie uses HttpOnly and SameSite=Lax.
- Session cookie uses Secure when the app is served over HTTPS.
- Missing or expired session hides loan workflows and shows sign-in/recovery
  guidance.
- Session state is not durable and is cleared on sign-out.

State transitions:

- `signed_out` -> `signing_in`: reviewer selects sign-in.
- `signing_in` -> `signed_in`: Auth0 callback succeeds and session is stored.
- `signed_in` -> `expired`: token/session expiry is detected.
- `signed_in` -> `signed_out`: reviewer signs out.
- any state -> `setup_error`: sign-in/protected flow requires missing Auth0
  configuration.

## Auth0 Access Token

Represents the bearer token used by the website and direct API callers to access
loan endpoints.

Fields/claims:

- `iss`: Auth0 issuer matching `https://{AUTH0_DOMAIN}/`
- `aud`: configured Auth0 API audience
- `sub`: Auth0 subject
- `exp`: expiry timestamp
- `iat`: issued-at timestamp
- `scope`: optional space-delimited scopes; not required for this slice

Validation rules:

- Must be present in `Authorization: Bearer <token>`.
- Must be a valid JWT signed with RS256 by a key from the Auth0 tenant JWKS.
- Must have the configured issuer and audience.
- Must not be expired.
- Missing, malformed, expired, wrong-audience, wrong-issuer, or unverifiable
  tokens produce a `401` JSON authentication error.

## Authentication Configuration

Represents local runtime settings needed for Auth0.

Fields:

- `AUTH0_DOMAIN`
- `AUTH0_CLIENT_ID`
- `AUTH0_CLIENT_SECRET`
- `AUTH0_AUDIENCE`
- `AUTH0_CALLBACK_URL`
- `APP_SECRET_KEY`

Validation rules:

- Application startup does not fail when values are missing.
- Sign-in, callback, and protected loan flows report clear setup errors if
  required values are missing.
- Automated tests may inject fake auth/session/token verification instead of
  using these values.

## Authentication Failure

Represents a denied authentication state.

Fields:

- `error`: stable machine-readable error code, such as
  `authentication_required`, `invalid_token`, or `auth_configuration_error`
- `message`: reviewer-readable explanation
- `details`: optional list of setup or validation details

Rules:

- Protected API failures return `401` JSON and never include loan records.
- Setup errors provide enough guidance to fix local Auth0 configuration without
  exposing secrets.
