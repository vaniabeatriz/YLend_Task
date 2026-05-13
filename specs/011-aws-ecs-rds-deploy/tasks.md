# Tasks: AWS ECS RDS Deployment

**Input**: Design documents from `/specs/011-aws-ecs-rds-deploy/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are REQUIRED. Add pytest coverage for repository selection,
PostgreSQL repository behaviour, documentation examples, and deployment
configuration invariants; keep the final coverage gate at 80% or higher.

**Organization**: Tasks are grouped by user story so each story can be
implemented and tested independently after the shared cloud/runtime foundation
is complete.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and does not
  depend on incomplete tasks in the same phase.
- **[Story]**: User story label for story phases only.
- Every task includes exact file paths.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare dependencies, container packaging, and AWS infrastructure
directories.

- [X] T001 Update `requirements.txt` with `psycopg[binary]` for RDS PostgreSQL and `gunicorn` for ECS container runtime.
- [X] T002 [P] Create `.dockerignore` to exclude `.venv/`, caches, local SQLite files, Terraform state, and test artifacts from image builds.
- [X] T003 [P] Create `Dockerfile` for the Flask app using production `gunicorn` startup and the existing `/health` endpoint.
- [X] T004 [P] Create Terraform provider/version scaffolding in `infra/aws/bootstrap/versions.tf`.
- [X] T005 [P] Create Terraform provider/version scaffolding in `infra/aws/app/versions.tf`.
- [X] T006 [P] Add initial AWS app module variables in `infra/aws/app/variables.tf`.
- [X] T007 [P] Add initial AWS bootstrap module variables in `infra/aws/bootstrap/variables.tf`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add runtime storage selection and PostgreSQL repository support
before cloud user stories are implemented.

**CRITICAL**: No user story work should begin until this phase is complete.

- [X] T008 [P] Add repository factory selection tests for SQLite fallback, PostgreSQL URL selection, and deployed fail-closed behaviour in `tests/unit/test_repository_factory.py`.
- [X] T009 [P] Add PostgreSQL schema, create/get/list/search/delete, duplicate, and storage-error tests in `tests/unit/test_postgres_loan_repository.py`.
- [X] T010 [P] Add Flask app factory configuration tests for `DATABASE_URL`, `LOAN_DATABASE_URL`, and deployed no-SQLite fallback behaviour in `tests/integration/test_durable_loan_persistence.py`.
- [X] T011 Create `app/repositories/repository_factory.py` to select the correct loan repository from runtime configuration.
- [X] T012 Create `app/repositories/postgres_loan_repository.py` with RDS PostgreSQL connection handling, schema initialization, CRUD operations, duplicate mapping, and `LoanStorageError` handling.
- [X] T013 Update `app/__init__.py` to use `repository_factory.py` and preserve explicit `LOAN_REPOSITORY` test injection.
- [X] T014 Update `app/repositories/__init__.py` exports for the SQLite, PostgreSQL, and factory repository components.
- [X] T015 Run foundational tests for `tests/unit/test_repository_factory.py`, `tests/unit/test_postgres_loan_repository.py`, and `tests/integration/test_durable_loan_persistence.py`.

**Checkpoint**: The app can choose RDS-backed storage for deployed runtime while
retaining isolated local/test execution.

---

## Phase 3: User Story 1 - Use Loan Workflows In A Cloud Environment (Priority: P1) MVP

**Goal**: Reviewers can access the deployed website/API and complete existing
authenticated loan workflows without running Flask locally.

**Independent Test**: Build the image, deploy the ECS service with required
runtime configuration, open the deployed URL, sign in, and complete create,
list, borrower search, lookup, and delete.

### Tests for User Story 1

- [X] T016 [P] [US1] Add Dockerfile and `gunicorn` startup documentation assertions in `tests/integration/test_documentation_examples.py`.
- [X] T017 [P] [US1] Add deployment runtime configuration contract assertions for Auth0 and database environment variables in `tests/integration/test_documentation_examples.py`.
- [X] T018 [P] [US1] Add cloud health-check and deployed URL smoke-test documentation assertions in `tests/integration/test_documentation_examples.py`.

### Implementation for User Story 1

- [X] T019 [US1] Implement ECS cluster, task definition, service, and load balancer resources in `infra/aws/app/main.tf`.
- [X] T020 [US1] Implement VPC, subnet, routing, load balancer, ECS, and app-to-database security group resources in `infra/aws/app/security.tf`.
- [X] T021 [US1] Wire Auth0, Flask secret, and database runtime environment/secrets into the ECS task definition in `infra/aws/app/main.tf`.
- [X] T022 [US1] Add deployed service outputs for `service_url`, `ecs_cluster_name`, and `ecs_service_name` in `infra/aws/app/outputs.tf`.
- [X] T023 [US1] Update deployed website/API setup and smoke-test instructions in `README.md`.
- [ ] T024 [US1] Run US1 local verification for `Dockerfile` and `tests/integration/test_documentation_examples.py`.

**Checkpoint**: User Story 1 is ready for an AWS smoke deployment with the
existing loan workflows exposed through ECS.

---

## Phase 4: User Story 2 - Preserve Loans Across Service Replacement (Priority: P2)

**Goal**: Loans created in the deployed environment survive ECS task restart,
replacement, and redeploy operations.

**Independent Test**: Create a loan against the deployed service, force ECS task
replacement, and confirm lookup, listing, and borrower-name search still return
the loan; delete it and confirm absence survives another replacement.

### Tests for User Story 2

- [X] T025 [P] [US2] Add PostgreSQL cross-connection persistence tests in `tests/unit/test_postgres_loan_repository.py`.
- [X] T026 [P] [US2] Add deployed storage-unavailable and no-silent-SQLite-fallback tests in `tests/integration/test_durable_loan_persistence.py`.
- [X] T027 [P] [US2] Add persistence replacement checklist assertions in `tests/integration/test_documentation_examples.py`.

### Implementation for User Story 2

- [X] T028 [US2] Add RDS PostgreSQL instance, subnet group, parameter choices, and database outputs in `infra/aws/app/main.tf`.
- [X] T029 [US2] Restrict RDS network access to the ECS app security group in `infra/aws/app/security.tf`.
- [X] T030 [US2] Add database credential and connection URL secret handling for ECS in `infra/aws/app/main.tf`.
- [X] T031 [US2] Ensure PostgreSQL schema initialization is idempotent and preserves insertion ordering in `app/repositories/postgres_loan_repository.py`.
- [X] T032 [US2] Update deployed persistence and forced task replacement verification steps in `specs/011-aws-ecs-rds-deploy/quickstart.md`.
- [X] T033 [US2] Run targeted US2 tests in `tests/unit/test_postgres_loan_repository.py`, `tests/integration/test_durable_loan_persistence.py`, and `tests/integration/test_documentation_examples.py`.

**Checkpoint**: User Stories 1 and 2 both work independently, and deployed loan
data is outside disposable ECS task storage.

---

## Phase 5: User Story 3 - Release The App Repeatably (Priority: P3)

**Goal**: Maintainers can build, publish, deploy, verify, and roll back a
versioned application release without manually editing files on a server.

**Independent Test**: From a clean checkout with AWS permissions, follow the
quickstart to bootstrap ECR, push a versioned image, deploy/update ECS, verify
health, and roll back to a previous image tag.

### Tests for User Story 3

- [X] T034 [P] [US3] Add ECR bootstrap and image-tagging documentation assertions in `tests/integration/test_documentation_examples.py`.
- [X] T035 [P] [US3] Add rollback and teardown documentation assertions in `tests/integration/test_documentation_examples.py`.
- [X] T036 [P] [US3] Add Terraform output contract assertions for `ecr_repository_url`, `service_url`, `ecs_cluster_name`, `ecs_service_name`, and `rds_endpoint` in `tests/integration/test_documentation_examples.py`.

### Implementation for User Story 3

- [X] T037 [US3] Implement ECR repository resources in `infra/aws/bootstrap/main.tf`.
- [X] T038 [US3] Add ECR repository output in `infra/aws/bootstrap/outputs.tf`.
- [X] T039 [US3] Add `image_uri` release input and rollback-oriented outputs in `infra/aws/app/variables.tf` and `infra/aws/app/outputs.tf`.
- [X] T040 [US3] Update build, push, deploy, rollback, and teardown instructions in `specs/011-aws-ecs-rds-deploy/quickstart.md`.
- [X] T041 [US3] Update deployment configuration contract in `specs/011-aws-ecs-rds-deploy/contracts/deployment-config.md`.
- [X] T042 [US3] Run targeted US3 tests in `tests/integration/test_documentation_examples.py`.

**Checkpoint**: All user stories are independently functional and the release
path is repeatable.

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, formatting, regression coverage, security review,
and final verification.

- [X] T043 [P] Update final AWS deployment, local development, and RDS storage notes in `README.md`.
- [X] T044 [P] Review final quickstart accuracy in `specs/011-aws-ecs-rds-deploy/quickstart.md`.
- [X] T045 [P] Review infrastructure contract accuracy in `specs/011-aws-ecs-rds-deploy/contracts/deployment-config.md`.
- [X] T046 Run full regression suite with `.venv/bin/python -m pytest --cov=app --cov-report=term-missing --cov-fail-under=80`.
- [ ] T047 Run Docker image build verification for `Dockerfile`.
- [ ] T048 Run Terraform formatting and validation for `infra/aws/bootstrap/` and `infra/aws/app/`.
- [X] T049 Perform final security/scope review for secrets, Terraform state, public exposure, Auth0 behaviour, roles, per-user ownership, Kubernetes, and multi-region exclusions in `README.md`, `infra/aws/`, and `specs/011-aws-ecs-rds-deploy/`.
- [ ] T050 Run the deployed AWS smoke checklist from `specs/011-aws-ecs-rds-deploy/quickstart.md` if AWS credentials and billing access are available.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup** has no dependencies.
- **Phase 2: Foundational** depends on Setup and blocks all user stories.
- **Phase 3: US1** depends on Foundational and is the MVP.
- **Phase 4: US2** depends on Foundational and can be validated after RDS wiring exists.
- **Phase 5: US3** depends on Setup and Foundational and completes the release path.
- **Final Phase** depends on all desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: No dependency on US2/US3 after Foundational; proves the app can run in ECS.
- **US2 (P2)**: Builds on US1 infrastructure and foundational PostgreSQL repository support to prove persistence across ECS replacement.
- **US3 (P3)**: Builds on US1/US2 deployment shape to make release, rollback, and teardown repeatable.

### Within Each User Story

- Write tests before implementation tasks in that story.
- Repository/runtime configuration before ECS task wiring.
- Network/security before service verification.
- Documentation and smoke checks before considering the story complete.

---

## Parallel Opportunities

- T002, T003, T004, T005, T006, and T007 can run in parallel after T001 is understood.
- T008, T009, and T010 can run in parallel because they touch different test files.
- T016, T017, and T018 can run in parallel for US1 documentation/contract assertions.
- T025, T026, and T027 can run in parallel for US2 tests.
- T034, T035, and T036 can run in parallel for US3 tests.
- T043, T044, and T045 can run in parallel during final documentation polish.

## Parallel Example: User Story 1

```text
Task: "Add Dockerfile and gunicorn startup documentation assertions in tests/integration/test_documentation_examples.py"
Task: "Add deployment runtime configuration contract assertions for Auth0 and database environment variables in tests/integration/test_documentation_examples.py"
Task: "Add cloud health-check and deployed URL smoke-test documentation assertions in tests/integration/test_documentation_examples.py"
```

## Parallel Example: User Story 2

```text
Task: "Add PostgreSQL cross-connection persistence tests in tests/unit/test_postgres_loan_repository.py"
Task: "Add deployed storage-unavailable and no-silent-SQLite-fallback tests in tests/integration/test_durable_loan_persistence.py"
Task: "Add persistence replacement checklist assertions in tests/integration/test_documentation_examples.py"
```

## Parallel Example: User Story 3

```text
Task: "Add ECR bootstrap and image-tagging documentation assertions in tests/integration/test_documentation_examples.py"
Task: "Add rollback and teardown documentation assertions in tests/integration/test_documentation_examples.py"
Task: "Add Terraform output contract assertions for ecr_repository_url, service_url, ecs_cluster_name, ecs_service_name, and rds_endpoint in tests/integration/test_documentation_examples.py"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: US1.
4. Validate local tests, Docker build, and ECS service health.

### Incremental Delivery

1. Add foundational PostgreSQL/runtime selection.
2. Add US1 so the app can run behind ECS/ALB.
3. Add US2 so deployed data survives task replacement through RDS.
4. Add US3 so image publishing, deploy, rollback, and teardown are repeatable.
5. Finish documentation, security review, and full regression verification.

### Single-Developer Strategy

Work sequentially in priority order: Setup -> Foundational -> US1 -> US2 -> US3
-> Polish. Stop at each checkpoint and run the targeted tests before continuing.

## Notes

- Deployed ECS runtime must not silently use SQLite.
- Do not commit secrets, `.env` values, Terraform state, or local database files.
- Keep Auth0 behaviour and existing loan response shapes unchanged.
- Keep Kubernetes, multi-region, production compliance hardening, roles, and
  per-user loan ownership out of scope.
- If AWS credentials are unavailable locally, complete code, Docker, Terraform
  validation, and documentation; mark the live AWS smoke test as not run.
