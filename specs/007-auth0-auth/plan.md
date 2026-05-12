# Implementation Plan: Auth0 Authentication

**Branch**: `008-auth0-auth` | **Date**: 2026-05-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-auth0-auth/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add Auth0 authentication to the existing Flask loan website and JSON loan API.
The website gets sign-in, callback, sign-out, authenticated/unauthenticated UI
states, and clear setup/authentication error feedback. Protected loan API
endpoints require Auth0 JWT bearer access tokens in the `Authorization` header,
return `401` JSON authentication errors for missing or invalid tokens, and
preserve all existing loan behaviours once authentication succeeds.

Keep the app as one Flask project with Bootstrap templates and plain
JavaScript. Add a small auth module for Auth0 configuration, OAuth login
session handling, and access-token verification. Automated tests use mocked
sessions and token verification so the coverage gate does not depend on a live
Auth0 tenant.

## Technical Context

**Language/Version**: Python 3.11+ (local environment currently reports Python 3.14.4)  
**Primary Dependencies**: Flask, Bootstrap for UI styling, pytest, pytest-cov, Authlib for Auth0/OIDC login, PyJWT with crypto support for Auth0 JWT/JWKS validation, python-dotenv for local Auth0 configuration  
**Storage**: Existing process-local runtime dictionary keyed by trimmed, case-sensitive loan ID; Flask secure-cookie session for website authentication state; no durable storage added  
**Testing**: pytest with coverage >=80%; mocked Auth0 sessions/token verification for automated tests, plus manual Auth0 demo documented in quickstart  
**Target Platform**: Local Flask development server and modern browser  
**Project Type**: Flask web application serving a Bootstrap website plus JSON API endpoints  
**Performance Goals**: Authenticated loan API responses and authentication errors return within 2 seconds for local technical-test usage; signed-in reviewer can complete the full browser demo in under 7 minutes  
**Constraints**: Explainable under 40 minutes; single Flask app; Auth0 required; no durable persistence; no public deployment; no container registry; no Kubernetes; no cloud infrastructure; no frontend framework or build step; no CSRF token handling in this slice  
**Scale/Scope**: Single-user local browser/API demo over existing loan workflows with Auth0 sign-in and bearer-token API protection

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Scope is small enough to explain, run, and defend within 40 minutes.
  **Pass**: one authentication layer over existing website/API workflows plus
  tests and documentation.
- Technical approach uses Python, Flask, and Bootstrap; any extra framework,
  service, or dependency is justified in Complexity Tracking.
  **Pass with justified additions**: Authlib, PyJWT, and python-dotenv are
  directly required to integrate Auth0 login, validate Auth0 API tokens, and
  configure local credentials without adding another service or app framework.
- UI defaults to Flask-rendered templates with Bootstrap unless an alternative
  is explicitly justified.
  **Pass**: the website remains Flask-rendered and Bootstrap-styled with plain
  JavaScript.
- Test strategy uses pytest and enforces at least 80% statement coverage.
  **Pass**: pytest remains the runner and tests will mock Auth0 paths so the
  coverage gate is deterministic.
- Documentation plan includes concise setup, run, test, and demo instructions.
  **Pass**: quickstart and README updates will document Auth0 local setup,
  mocked tests, protected API calls, and website demo flow.
- Data storage and project structure are the simplest options that satisfy the
  feature requirements.
  **Pass**: no new data store; auth state stays in Flask session and existing
  loan storage remains unchanged.

## Project Structure

### Documentation (this feature)

```text
specs/007-auth0-auth/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── openapi.yaml
│   └── ui-auth-contract.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
app/
├── __init__.py
├── routes.py
├── auth.py
├── models/
│   └── loan.py
├── services/
│   └── loan_service.py
├── templates/
│   └── index.html
└── static/
    ├── loan_website.css
    └── loan_website.js

tests/
├── unit/
│   ├── test_auth.py
│   └── test_loan_service.py
└── integration/
    ├── test_auth_routes.py
    ├── test_auth_protected_api.py
    ├── test_borrower_name_lookup_api.py
    ├── test_create_loan_api.py
    ├── test_delete_loan_api.py
    ├── test_documentation_examples.py
    ├── test_get_loan_api.py
    ├── test_health_api.py
    ├── test_list_loans_api.py
    └── test_loan_website.py

README.md
requirements.txt
```

**Structure Decision**: Keep a single Flask app. Add `app/auth.py` for Auth0
configuration, OAuth login/session helpers, bearer-token extraction, JWT/JWKS
verification, and route decorators. Update `app/__init__.py` to configure
session cookie settings and initialize auth. Update `app/routes.py` to add
login/callback/logout/status routes and protect loan endpoints only; keep
`GET /` and `GET /health` public. Update the existing template/static assets to
hide loan workflows while signed out and send `Authorization: Bearer <token>`
for loan API calls. Do not add a separate frontend project, database,
deployment manifests, container files, Kubernetes resources, or cloud
infrastructure.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| New dependency: Authlib | Required to implement Auth0/OIDC authorization-code login and callback handling in the existing Flask app. | Hand-writing OAuth redirects, token exchange, and session handling would be more error-prone and harder to explain. |
| New dependency: PyJWT with crypto support | Required to validate Auth0 JWT bearer access tokens against RS256 issuer, audience, expiry, and JWKS signing keys. | Trusting the website session or decoding tokens without signature/claim verification would not protect direct API calls. |
| New dependency: python-dotenv | Required to document local Auth0 configuration cleanly without committing secrets. | Manual exports only are easier to mistype and make local demo setup less repeatable. |

## Phase 0 Research Summary

See [research.md](./research.md). All planning questions are resolved; no
`NEEDS CLARIFICATION` items remain.

## Phase 1 Design Summary

- Data model: [data-model.md](./data-model.md)
- API contract: [contracts/openapi.yaml](./contracts/openapi.yaml)
- UI/auth contract: [contracts/ui-auth-contract.md](./contracts/ui-auth-contract.md)
- Quickstart and demo path: [quickstart.md](./quickstart.md)

## Post-Design Constitution Check

- Scope remains one local Auth0 authentication slice over existing loan
  website/API workflows.
- Design keeps Python, Flask, Flask templates, Bootstrap, and plain JavaScript;
  no separate frontend framework or build system is introduced.
- Additional dependencies are limited to Auth0/OIDC login, JWT verification,
  and local configuration support, with rationale recorded in Complexity
  Tracking and research.
- Existing loan storage and service behaviour remain unchanged after
  authentication succeeds.
- Tests are planned with pytest and the existing 80% coverage gate; automated
  auth tests use mocked sessions/token verification rather than live Auth0.
- Documentation artifacts cover setup, Auth0 local configuration, run, test,
  protected API calls, local browser demo, and out-of-scope boundaries.

**Result**: PASS. Ready for `/speckit-tasks`.
