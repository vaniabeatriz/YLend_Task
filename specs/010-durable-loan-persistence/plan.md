# Implementation Plan: Durable Loan Persistence

**Branch**: `010-durable-loan-persistence` | **Date**: 2026-05-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-durable-loan-persistence/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Replace process-local loan storage with a local SQLite-backed loan repository so
authenticated create, list, borrower-name search, loan ID lookup, and delete
workflows survive Flask app restarts. Keep existing response shapes,
normalization, duplicate checks, Auth0 protection, and website behaviour intact.
Initialize local storage automatically on app startup and prove restart
persistence with automated tests using isolated temporary database files.

## Technical Context

**Language/Version**: Python 3.11+ (local environment currently reports Python 3.14.4)  
**Primary Dependencies**: Flask, Authlib, PyJWT crypto support, python-dotenv, pytest, pytest-cov, Bootstrap; SQLite through Python standard library `sqlite3`  
**Storage**: Local SQLite database file, defaulting to the Flask instance directory and configurable for tests/local demos  
**Testing**: pytest with coverage >=80%  
**Target Platform**: Local Flask development server, browser website, and HTTP clients such as curl or tests  
**Project Type**: Flask web application with JSON API and server-rendered single-page website  
**Performance Goals**: Authenticated loan create/list/search/lookup/delete actions complete within 2 seconds for local technical-test usage  
**Constraints**: Explainable under 40 minutes; simplest database-backed storage; no public deployment; no managed infrastructure; no Auth0 behaviour changes; concise documentation  
**Scale/Scope**: Single-process local demo with durable current loan records shared by all authenticated users; no roles, per-user ownership, migrations framework, or cloud services

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Scope is small enough to explain, run, and defend within 40 minutes.
  **Pass**: one storage replacement plus restart verification for existing loan workflows.
- Technical approach uses Python, Flask, and Bootstrap; any extra framework,
  service, or dependency is justified in Complexity Tracking.
  **Pass**: SQLite uses Python standard library support; no extra service or frontend framework is added.
- UI defaults to Flask-rendered templates with Bootstrap unless an alternative
  is explicitly justified.
  **Pass**: existing Flask template and Bootstrap website remains unchanged except for any persistence-related copy needed in documentation.
- Test strategy uses pytest and enforces at least 80% statement coverage.
  **Pass**: unit and integration tests will run with `pytest --cov=app --cov-report=term-missing --cov-fail-under=80`.
- Documentation plan includes concise setup, run, test, and demo instructions.
  **Pass**: quickstart and README updates will explain database location, restart verification, and reset behaviour.
- Data storage and project structure are the simplest options that satisfy the
  feature requirements.
  **Pass**: a single local SQLite file satisfies durable database-backed storage without a managed database.

## Project Structure

### Documentation (this feature)

```text
specs/010-durable-loan-persistence/
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
├── auth.py
├── routes.py
├── models/
│   └── loan.py
├── repositories/
│   └── loan_repository.py
├── services/
│   └── loan_service.py
├── templates/
│   └── index.html
└── static/
    ├── loan_website.css
    └── loan_website.js

tests/
├── unit/
│   ├── test_loan_repository.py
│   └── test_loan_service.py
└── integration/
    ├── test_durable_loan_persistence.py
    ├── test_auth_protected_api.py
    ├── test_create_loan_api.py
    ├── test_list_loans_api.py
    ├── test_borrower_name_lookup_api.py
    ├── test_get_loan_api.py
    ├── test_delete_loan_api.py
    ├── test_loan_website.py
    └── test_documentation_examples.py

README.md
requirements.txt
```

**Structure Decision**: Keep validation and response-preserving business rules in
`app/services/loan_service.py`, move durable CRUD storage behind
`app/repositories/loan_repository.py`, and wire the app factory to initialize a
SQLite-backed repository. This keeps routes and UI stable while allowing tests
to prove persistence with separate app instances that share the same database
file.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| SQLite-backed repository boundary | Durable database-backed storage must survive process restarts while preserving current service validation and route behaviour | Keeping the existing in-memory dictionary cannot satisfy restart persistence; writing SQL directly in routes would spread storage concerns across request handlers |

## Phase 0 Research Summary

See [research.md](./research.md). All planning questions are resolved; no
`NEEDS CLARIFICATION` items remain.

## Phase 1 Design Summary

- Data model: [data-model.md](./data-model.md)
- API contract: [contracts/openapi.yaml](./contracts/openapi.yaml)
- Quickstart and demo path: [quickstart.md](./quickstart.md)

## Post-Design Constitution Check

- Scope remains one persistence slice for existing authenticated workflows.
- Design uses Python, Flask, Bootstrap, pytest, and standard library SQLite.
- No new hosted service, frontend framework, managed database, deployment
  tooling, or infrastructure is introduced.
- Tests include repository-level behaviour plus integration restart proof with
  isolated temporary database files and the 80% coverage gate.
- Documentation artifacts cover setup, run, test, local database location,
  restart verification, and reset behaviour.
- The repository boundary is justified by the durability requirement and keeps
  route/service responsibilities explainable.

**Result**: PASS. Ready for `/speckit-tasks`.
