# Research: Auth0 Authentication

## Decision: Use Authlib for Auth0 website login

Use Authlib's Flask OAuth client to implement Auth0 authorization-code login,
callback handling, access-token capture, and sign-out integration inside the
existing Flask app.

**Rationale**: The website is a server-rendered Flask app, and Auth0's Python
web-app guidance supports OAuth/OIDC login for Flask. Authlib keeps OAuth
redirect, token exchange, and userinfo handling out of handwritten application
code while avoiding a separate frontend framework or build step.

**Alternatives considered**:

- Auth0 server SDK: current Auth0 web-app docs include an SDK path, but it adds
  async-oriented setup and more moving parts than this local Flask slice needs.
- Hand-written OAuth flow: rejected because token exchange and state handling
  are easy to implement incorrectly and would weaken explainability.
- Browser-only SPA login: rejected because the constitution keeps the UI as
  Flask templates plus Bootstrap and no frontend build pipeline.

## Decision: Protect loan API endpoints with Auth0 JWT bearer access tokens

Require `Authorization: Bearer <access-token>` on `POST /loans`, `GET /loans`,
`GET /loans/{loanId}`, and `DELETE /loans/{loanId}`. Validate tokens with
RS256, Auth0 issuer, configured API audience, expiry, and JWKS signing keys.

**Rationale**: The clarified spec requires direct loan API protection, not only
browser session protection. Auth0's API guidance uses bearer access tokens,
JWKS, RS256, issuer, and audience validation. A route decorator keeps
authentication enforcement explicit while preserving existing loan service
behaviour after verification succeeds.

**Alternatives considered**:

- Website session cookie only: rejected by clarification because direct API
  calls must use Auth0 JWT bearer tokens.
- Redirect API callers to Auth0 login: rejected by clarification because API
  failures should return `401` JSON authentication errors.
- Scopes/permissions per operation: rejected for this slice because the spec
  states all authenticated users have the same loan-management permissions.

## Decision: Use PyJWT with crypto support for JWT/JWKS validation

Use PyJWT's JWT and JWK support to validate Auth0 access tokens, backed by
RS256 public keys from the tenant JWKS endpoint. Cache JWKS in process during
local runtime and allow tests to inject a fake verifier.

**Rationale**: PyJWT is a focused dependency for signature and claim
verification. It lets the app validate issuer, audience, expiry, and malformed
tokens without implementing cryptographic logic manually.

**Alternatives considered**:

- Decode tokens without verifying: rejected because it would not prove the
  token was issued by Auth0 for the configured API.
- Implement JWKS parsing manually: rejected because it increases security risk
  and code volume.
- Add a separate API gateway or middleware service: rejected as out of scope for
  the local technical-test slice.

## Decision: Automated tests mock Auth0 sessions and bearer-token verification

Automated tests will inject authenticated/unauthenticated website session state
and fake bearer-token verification through Flask test configuration. Live Auth0
is reserved for manual demo.

**Rationale**: Tests must be deterministic, fast, and runnable without network
access or real credentials. Mocking auth boundaries lets tests cover website
gating, protected endpoint failures, successful authenticated loan operations,
and expired/invalid token paths while keeping coverage above 80%.

**Alternatives considered**:

- Require real Auth0 tenant/test user in pytest: rejected because it makes the
  test suite brittle and dependent on network/secrets.
- Mock all authentication including manual demo: rejected because reviewers
  should be able to exercise the real Auth0 sign-in flow when configured.

## Decision: Missing Auth0 configuration does not prevent application startup

The Flask app starts without Auth0 configuration. Public routes such as `/` and
`/health` remain available. Sign-in and protected loan flows show a clear setup
error when required Auth0 settings are missing.

**Rationale**: This keeps local operational validation simple and supports the
test suite without live credentials. It also makes configuration problems
visible exactly where authentication is used.

**Alternatives considered**:

- Fail application startup: rejected because it would block health checks and
  non-auth setup validation.
- Allow unauthenticated local bypass: rejected because it weakens the protected
  loan API requirement.

## Decision: Session-cookie security uses HttpOnly, SameSite=Lax, and Secure when HTTPS

Configure Flask session cookies with `HttpOnly` and `SameSite=Lax`; set
`Secure` when running behind HTTPS-capable configuration. Do not add separate
CSRF token checks in this slice.

**Rationale**: The website remains same-origin and local. SameSite=Lax plus
bearer-token API protection keeps the slice simple and testable while still
documenting session-cookie protections.

**Alternatives considered**:

- Add CSRF token checks for create/delete: rejected for this slice because API
  writes require bearer tokens and explicit CSRF token plumbing would add scope.
- Leave session-cookie protections unspecified: rejected because authentication
  state should have clear security expectations.

## References

- Auth0 Flask API quickstart: https://auth0.com/docs/quickstart/backend/python
- Auth0 Python regular web app quickstart: https://auth0.com/docs/quickstart/webapp/python
- Auth0 JWT validation guidance: https://auth0.com/docs/secure/tokens/json-web-tokens/validate-json-web-tokens
- Auth0 JWKS guidance: https://auth0.com/docs/secure/tokens/json-web-tokens/locate-json-web-key-sets
