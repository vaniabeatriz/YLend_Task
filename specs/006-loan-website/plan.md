# Implementation Plan: Loan Website

**Branch**: `006-loan-website` | **Date**: 2026-05-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-loan-website/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add a single-page website for the existing loan-management API. The page lets a
reviewer create loans, list current loans, search by borrower name, look up by
loan ID, and delete by loan ID from one responsive browser surface. Reuse the
existing Flask application, loan service, and current-session in-memory store.
Add a Flask-rendered page plus static browser assets that call the existing JSON
endpoints from the same origin, show clear success/error/empty states, and keep
Auth0, durable persistence, public exposure, container registry work,
Kubernetes, cloud infrastructure, and separate frontend build tooling out of
scope.

## Technical Context

**Language/Version**: Python 3.11+ (local environment currently reports Python 3.14.4)  
**Primary Dependencies**: Flask, Bootstrap for UI styling, pytest, pytest-cov; browser Fetch API via plain JavaScript with no frontend framework or build step  
**Storage**: Existing process-local in-memory dictionary keyed by trimmed, case-sensitive loan ID; website adds no storage layer  
**Testing**: pytest with coverage >=80%; integration tests for page rendering, route/static assets, API regressions, and documented demo flow  
**Target Platform**: Local Flask development server and modern browser  
**Project Type**: Flask web application serving both JSON API endpoints and one browser page  
**Performance Goals**: Primary website actions show success or error feedback within 2 seconds for local technical-test usage; reviewer can complete the full browser demo in under 6 minutes  
**Constraints**: Explainable under 40 minutes; single-page local demo; no authentication; no persistence beyond runtime; no public exposure; no container registry; no Kubernetes; no cloud infrastructure; no Node/Angular build pipeline in this slice; concise documentation  
**Scale/Scope**: Single-user local browser demo over the current loan API, one page, current-session temporary loan records only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Scope is small enough to explain, run, and defend within 40 minutes.
  **Pass**: one browser page over existing loan API workflows plus tests and
  documentation.
- Technical approach uses Python, Flask, and Bootstrap; any extra framework,
  service, or dependency is justified in Complexity Tracking.
  **Pass**: use Flask templates and static assets with Bootstrap styling; no
  Angular, Node build, additional API layer, queue, service, database, or
  frontend framework is introduced.
- UI defaults to Flask-rendered templates with Bootstrap unless an alternative
  is explicitly justified.
  **Pass**: the page is rendered from Flask templates and styled with Bootstrap.
- Test strategy uses pytest and enforces at least 80% statement coverage.
  **Pass**: pytest remains the test runner and coverage gate; browser-only
  visual checks are documented in quickstart in addition to route/static/API
  tests.
- Documentation plan includes concise setup, run, test, and demo instructions.
  **Pass**: README and feature quickstart will cover local website usage.
- Data storage and project structure are the simplest options that satisfy the
  feature requirements.
  **Pass**: the website reuses the existing in-memory store and app structure.

## Project Structure

### Documentation (this feature)

```text
specs/006-loan-website/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── ui-contract.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
app/
├── __init__.py
├── routes.py
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
│   └── test_loan_service.py
└── integration/
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

**Structure Decision**: Keep a single Flask app. Add one browser route in
`app/routes.py`, one template in `app/templates/index.html`, and small static
assets in `app/static/`. Reuse the existing API routes and service behaviour for
all loan operations. Do not add a separate frontend project, package manager,
database, authentication module, deployment manifests, container files, or cloud
infrastructure in this slice.

## Complexity Tracking

No constitution violations identified.

## Phase 0 Research Summary

See [research.md](./research.md). All planning questions are resolved; no
`NEEDS CLARIFICATION` items remain.

## Phase 1 Design Summary

- Data model: [data-model.md](./data-model.md)
- UI contract: [contracts/ui-contract.md](./contracts/ui-contract.md)
- Quickstart and demo path: [quickstart.md](./quickstart.md)

## Post-Design Constitution Check

- Scope remains one local single-page website over existing API workflows.
- Design uses Flask-rendered templates, Bootstrap styling, and plain browser
  JavaScript only.
- Existing API endpoints and in-memory storage remain the data boundary.
- No Angular, Auth0, persistence, public exposure, container registry,
  Kubernetes, cloud infrastructure, or separate frontend build pipeline is
  introduced.
- Tests are planned with pytest and the existing 80% coverage gate; responsive
  and browser-state validation is documented in quickstart and backed by route,
  static asset, and integration tests where practical.
- Documentation artifacts cover setup, run, test, local browser demo, and
  trade-offs.

**Result**: PASS. Ready for `/speckit-tasks`.
