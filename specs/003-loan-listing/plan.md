# Implementation Plan: Loan Listing

**Branch**: `003-loan-listing` | **Date**: 2026-05-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-loan-listing/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add the next loan-management workflow after create and lookup: callers can
retrieve the collection of all loans currently stored in the active application
session. Reuse the existing Flask API application, immutable loan model, and
in-memory loan service. Listing returns every current stored loan exactly once,
uses the existing storage order, returns an empty collection for a fresh or
restarted session, and does not add deletion, filtering, searching, sorting
controls, pagination, persistence, browser UI, authentication, public exposure,
or cloud deployment.

## Technical Context

**Language/Version**: Python 3.11+ (local environment currently reports Python 3.14.4)  
**Primary Dependencies**: Flask, pytest, pytest-cov; Bootstrap not used because browser UI is out of scope  
**Storage**: Existing process-local in-memory dictionary keyed by trimmed, case-sensitive loan ID  
**Testing**: pytest with coverage >=80%  
**Target Platform**: Local Flask development server, exercised by HTTP clients such as curl or tests  
**Project Type**: Flask API web service  
**Performance Goals**: Listing success and empty-session responses returned within 2 seconds for local technical-test usage  
**Constraints**: Explainable under 40 minutes; API-only slice; no browser UI; no authentication; no persistence beyond runtime; no filtering/searching/sorting controls/pagination; concise documentation  
**Scale/Scope**: Single-process local demo, one listing endpoint, current-session temporary loan records only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Scope is small enough to explain, run, and defend within 40 minutes.
  **Pass**: one follow-up listing workflow plus documentation and tests.
- Technical approach uses Python and Flask; any extra framework, service, or
  dependency is justified in Complexity Tracking.
  **Pass**: no extra framework, background service, database, frontend
  framework, or dependency is needed.
- UI defaults to Flask-rendered templates with Bootstrap unless an alternative
  is explicitly justified.
  **Pass**: browser UI is out of scope, so no UI or Bootstrap assets are needed.
- Test strategy uses pytest and enforces at least 80% statement coverage.
  **Pass**: unit and integration tests will run with `pytest --cov=app
  --cov-report=term-missing --cov-fail-under=80`.
- Documentation plan includes concise setup, run, test, and demo instructions.
  **Pass**: quickstart and README content will document commands and demo
  requests.
- Data storage and project structure are the simplest options that satisfy the
  feature requirements.
  **Pass**: reuse the existing in-memory dictionary and small Flask app
  structure.

## Project Structure

### Documentation (this feature)

```text
specs/003-loan-listing/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── openapi.yaml
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
└── services/
    └── loan_service.py

tests/
├── unit/
│   └── test_loan_service.py
└── integration/
    ├── test_create_loan_api.py
    ├── test_documentation_examples.py
    ├── test_get_loan_api.py
    ├── test_health_api.py
    └── test_list_loans_api.py

README.md
requirements.txt
```

**Structure Decision**: Keep a single small Flask API application. Add listing
behaviour to `app/services/loan_service.py` and route handling to
`app/routes.py`; keep the loan data shape in `app/models/loan.py`. Do not add
templates, static assets, database migrations, auth modules, delete routes,
filtering/searching/sorting/pagination modules, or deployment infrastructure
for this slice.

## Complexity Tracking

No constitution violations identified.

## Phase 0 Research Summary

See [research.md](./research.md). All planning questions are resolved; no
`NEEDS CLARIFICATION` items remain.

## Phase 1 Design Summary

- Data model: [data-model.md](./data-model.md)
- API contract: [contracts/openapi.yaml](./contracts/openapi.yaml)
- Quickstart and demo path: [quickstart.md](./quickstart.md)

## Post-Design Constitution Check

- Scope remains one listing workflow that builds on the existing create-loan
  and lookup workflows.
- Design uses Flask and Python only for application behaviour.
- Browser UI remains out of scope; Bootstrap is not needed.
- Existing in-memory storage satisfies the current-session listing requirement.
- Tests are planned at unit and integration levels with an 80% coverage gate.
- Documentation artifacts cover setup, run, test, local validation, and
  trade-offs.

**Result**: PASS. Ready for `/speckit-tasks`.
