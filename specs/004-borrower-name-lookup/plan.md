# Implementation Plan: Borrower Name Loan Lookup

**Branch**: `004-borrower-name-lookup` | **Date**: 2026-05-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-borrower-name-lookup/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add borrower-name lookup as the next required loan-management workflow: callers
can retrieve all current-session loans whose borrower name exactly matches a
supplied borrower-name search term. Reuse the existing Flask API application,
immutable loan model, and in-memory loan service. Borrower-name lookup returns
the same loan collection envelope as full listing, returns an empty collection
when there are no matches, rejects blank search terms, preserves existing loan
ID lookup and full-listing behaviour, and does not add deletion, persistence,
authentication, browser UI, public exposure, or cloud deployment.

## Technical Context

**Language/Version**: Python 3.11+ (local environment currently reports Python 3.14.4)  
**Primary Dependencies**: Flask, pytest, pytest-cov; Bootstrap not used because browser UI is out of scope  
**Storage**: Existing process-local in-memory dictionary keyed by trimmed, case-sensitive loan ID  
**Testing**: pytest with coverage >=80%  
**Target Platform**: Local Flask development server, exercised by HTTP clients such as curl or tests  
**Project Type**: Flask API web service  
**Performance Goals**: Borrower-name lookup success, empty-result, and validation responses returned within 2 seconds for local technical-test usage  
**Constraints**: Explainable under 40 minutes; API-only slice; no browser UI; no authentication; no persistence beyond runtime; no deletion; no partial matching, case folding, sorting controls, pagination, or secondary index; concise documentation  
**Scale/Scope**: Single-process local demo, borrower-name search over current-session temporary loan records only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Scope is small enough to explain, run, and defend within 40 minutes.
  **Pass**: one borrower-name lookup workflow plus documentation and tests.
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
  structure; scan current loans for borrower-name matches.

## Project Structure

### Documentation (this feature)

```text
specs/004-borrower-name-lookup/
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
    ├── test_documentation_examples.py
    ├── test_get_loan_api.py
    ├── test_health_api.py
    └── test_list_loans_api.py

README.md
requirements.txt
```

**Structure Decision**: Keep a single small Flask API application. Add
borrower-name matching behaviour to `app/services/loan_service.py` and route
query handling to `app/routes.py`; keep the loan data shape in
`app/models/loan.py`. Do not add templates, static assets, database migrations,
auth modules, delete routes, partial-search modules, sorting/pagination modules,
or deployment infrastructure for this slice.

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

- Scope remains one borrower-name lookup workflow that builds on existing
  create-loan, single-loan lookup, and full-listing workflows.
- Design uses Flask and Python only for application behaviour.
- Browser UI remains out of scope; Bootstrap is not needed.
- Existing in-memory storage satisfies the current-session lookup requirement.
- Tests are planned at unit and integration levels with an 80% coverage gate.
- Documentation artifacts cover setup, run, test, local validation, and
  trade-offs.

**Result**: PASS. Ready for `/speckit-tasks`.
