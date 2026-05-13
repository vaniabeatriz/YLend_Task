# Implementation Plan: AWS ECS RDS Deployment

**Branch**: `011-aws-ecs-rds-deploy` | **Date**: 2026-05-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/011-aws-ecs-rds-deploy/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Deploy the existing Flask loan management app to AWS by containerizing the
service, publishing versioned images to ECR, running the app on ECS Fargate
behind a load balancer, and replacing deployed SQLite storage with RDS
PostgreSQL. Preserve existing Auth0-protected loan API and website behaviours,
keep local/test workflows runnable, and document a repeatable build, deploy,
verify, rollback, and teardown path.

## Technical Context

**Language/Version**: Python 3.11+ (local environment currently reports Python 3.14.4)  
**Primary Dependencies**: Flask, Authlib, PyJWT crypto support, python-dotenv, pytest, pytest-cov, Bootstrap; add `psycopg` for PostgreSQL/RDS access and `gunicorn` for container runtime  
**Storage**: Amazon RDS PostgreSQL for deployed runtime; existing SQLite path retained only for local/test fallback unless explicitly configured otherwise  
**Testing**: pytest with coverage >=80%; Docker image build verification; documented AWS smoke tests for deployed workflows  
**Target Platform**: AWS ECS Fargate service behind an Application Load Balancer, ECR image repository, RDS PostgreSQL database, local Flask development server for non-cloud development  
**Project Type**: Flask web application with JSON API, server-rendered single-page website, container image, and small infrastructure-as-code footprint  
**Performance Goals**: Deployed health check and authenticated loan create/list/search/lookup/delete actions complete within 2 seconds for demo-scale usage  
**Constraints**: Explainable under 40 minutes; simplest cloud deployment that satisfies AWS/RDS/ECR/ECS requirement; no Kubernetes; no multi-region; no production compliance hardening; no secrets in git; concise documentation  
**Scale/Scope**: Single non-production demo environment, desired ECS task count of 1 by default, small RDS instance, current loan records shared by all authenticated users

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Scope is small enough to explain, run, and defend within 40 minutes.
  **Pass with recorded complexity**: one containerized Flask service, one managed database, and one repeatable deployment path.
- Technical approach uses Python, Flask, and Bootstrap; any extra framework,
  service, or dependency is justified in Complexity Tracking.
  **Pass with recorded complexity**: `psycopg`, `gunicorn`, Docker, Terraform, ECR, ECS, and RDS are required by the cloud deployment request.
- UI defaults to Flask-rendered templates with Bootstrap unless an alternative
  is explicitly justified.
  **Pass**: website templates and Bootstrap UI remain unchanged.
- Test strategy uses pytest and enforces at least 80% statement coverage.
  **Pass**: existing coverage gate remains; new storage factory/repository behaviour is covered with pytest.
- Documentation plan includes concise setup, run, test, and demo instructions.
  **Pass**: README and feature quickstart will cover local development, image build, deploy, smoke test, rollback, and teardown.
- Data storage and project structure are the simplest options that satisfy the
  feature requirements.
  **Pass with recorded complexity**: RDS replaces deployed SQLite because managed database persistence is explicitly required.

## Project Structure

### Documentation (this feature)

```text
specs/011-aws-ecs-rds-deploy/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── deployment-config.md
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
│   ├── __init__.py
│   ├── loan_repository.py
│   ├── postgres_loan_repository.py
│   └── repository_factory.py
├── services/
│   └── loan_service.py
├── templates/
│   └── index.html
└── static/
    ├── loan_website.css
    └── loan_website.js

infra/
└── aws/
    ├── bootstrap/
    │   ├── main.tf
    │   ├── outputs.tf
    │   └── variables.tf
    └── app/
        ├── main.tf
        ├── outputs.tf
        ├── security.tf
        ├── variables.tf
        └── versions.tf

tests/
├── unit/
│   ├── test_loan_repository.py
│   ├── test_postgres_loan_repository.py
│   └── test_repository_factory.py
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

Dockerfile
.dockerignore
README.md
requirements.txt
```

**Structure Decision**: Keep application behaviour in the existing Flask app,
add a PostgreSQL repository and repository factory beside the SQLite
implementation, and keep AWS infrastructure isolated under `infra/aws/`. Split
Terraform into `bootstrap` for the ECR repository and `app` for the ECS/RDS
runtime so maintainers can create the image repository before building and
pushing the first image.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| AWS managed services: RDS, ECR, ECS, load balancer, security groups | The new requirement is to run the app on AWS with RDS-backed persistence and ECS/ECR deployment | Keeping the local Flask server and SQLite cannot satisfy cloud deployment or RDS/ECS/ECR requirements |
| Docker image and `gunicorn` runtime | ECS runs the app as a containerized long-running service and the Flask dev server is not appropriate for that runtime | Running `flask run` in ECS would be less reliable and harder to defend |
| PostgreSQL driver dependency | RDS PostgreSQL access needs a supported database driver from Flask code | Continuing to use standard-library SQLite cannot connect to RDS |
| Terraform infrastructure files | The deployment must be repeatable, reviewable, and rollback-aware | Console-only or ad hoc AWS CLI setup is harder to reproduce and document |

## Phase 0 Research Summary

See [research.md](./research.md). All planning questions are resolved; no
`NEEDS CLARIFICATION` items remain.

## Phase 1 Design Summary

- Data model: [data-model.md](./data-model.md)
- Deployment/configuration contract: [contracts/deployment-config.md](./contracts/deployment-config.md)
- Quickstart and demo path: [quickstart.md](./quickstart.md)

## Post-Design Constitution Check

- Scope remains one non-production cloud deployment slice for the existing loan
  app.
- Application code continues to use Python, Flask, Flask templates, and
  Bootstrap.
- Additional dependencies and services are explicitly justified by the
  stakeholder requirement to use RDS, ECR, and ECS.
- Tests keep the pytest coverage gate at 80% or higher and add focused coverage
  around repository selection and PostgreSQL SQL behaviour.
- Documentation artifacts cover local run, image build, ECR publish, ECS/RDS
  deploy, health verification, persistence verification, rollback, and teardown.
- Infrastructure remains deliberately small: one containerized app service, one
  managed relational database, one registry, and supporting network/security
  resources.

**Result**: PASS with recorded complexity. Ready for `/speckit-tasks`.
