# Implementation Plan: Loan Deletion

**Branch**: `005-loan-deletion` | **Date**: 2026-05-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-loan-deletion/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add the remaining required loan-management workflow: callers can delete one
current temporary loan by loan ID. Reuse the existing Flask API application,
immutable loan model, and in-memory loan service. Deletion trims the supplied
loan ID, matches case-sensitively, removes only the targeted current loan,
returns `200 OK` with the deleted loan record, and ensures deleted loans are
absent from loan ID lookup, borrower-name lookup, and full listing. Keep
persistence, authentication, browser UI, public exposure, cloud deployment, and
infrastructure changes out of scope.

## Technical Context

**Language/Version**: Python 3.11+ (local environment currently reports Python 3.14.4)  
**Primary Dependencies**: Flask, pytest, pytest-cov; Bootstrap not used because browser UI is out of scope  
**Storage**: Existing process-local in-memory dictionary keyed by trimmed, case-sensitive loan ID  
**Testing**: pytest with coverage >=80%  
**Target Platform**: Local Flask development server, exercised by HTTP clients such as curl or tests  
**Project Type**: Flask API web service  
**Performance Goals**: Successful deletion and not-found deletion responses returned within 2 seconds for local technical-test usage  
**Constraints**: Explainable under 40 minutes; API-only slice; no browser UI; no authentication; no persistence beyond runtime; no new storage layer; no infrastructure/deployment changes; concise documentation  
**Scale/Scope**: Single-process local demo, one delete-by-loan-ID endpoint, current-session temporary loan records only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Scope is small enough to explain, run, and defend within 40 minutes.
  **Pass**: one deletion workflow plus documentation and tests.
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
specs/005-loan-deletion/
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
    ├── test_borrower_name_lookup_api.py
    ├── test_create_loan_api.py
    ├── test_delete_loan_api.py
    ├── test_documentation_examples.py
    ├── test_get_loan_api.py
    ├── test_health_api.py
    └── test_list_loans_api.py

README.md
requirements.txt
```

**Structure Decision**: Keep a single small Flask API application. Add deletion
behavior to `app/services/loan_service.py` and route handling to
`app/routes.py`; keep the loan data shape in `app/models/loan.py`. Do not add
templates, static assets, database migrations, auth modules, persistence,
deployment infrastructure, or a separate repository layer for this slice.

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

- Scope remains one deletion workflow that builds on existing create, lookup,
  borrower-name search, and listing workflows.
- Design uses Flask and Python only for application behaviour.
- Browser UI remains out of scope; Bootstrap is not needed.
- Existing in-memory storage satisfies the current-session deletion
  requirement.
- Tests are planned at unit and integration levels with an 80% coverage gate.
- Documentation artifacts cover setup, run, test, local validation, and
  trade-offs.

**Result**: PASS. Ready for `/speckit-tasks`.
