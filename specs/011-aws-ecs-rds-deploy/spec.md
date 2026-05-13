# Feature Specification: AWS ECS RDS Deployment

**Feature Branch**: `011-aws-ecs-rds-deploy`  
**Created**: 2026-05-13  
**Status**: Draft  
**Input**: User description: "Put the Flask loan management app on AWS, replace SQLite persistence with RDS, and use ECR and ECS."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Use Loan Workflows In A Cloud Environment (Priority: P1)

An authenticated reviewer can open the deployed loan management website and use
the existing create, list, borrower-name search, loan ID lookup, and delete
workflows without relying on a local Flask process.

**Why this priority**: This is the core delivery value: reviewers need the
application available from a managed environment while preserving the workflows
already validated locally.

**Independent Test**: Deploy the application to the target cloud environment,
authenticate through the existing sign-in flow, then create, list, search, look
up, and delete a loan through the website and protected API.

**Acceptance Scenarios**:

1. **Given** the application is deployed and authentication settings are configured, **When** a reviewer opens the deployed website, **Then** the public page loads and protected loan actions remain hidden until sign-in.
2. **Given** a reviewer is signed in on the deployed website, **When** they create loan `LN-001`, **Then** the deployed service returns the same successful loan response shape used locally.
3. **Given** loan `LN-001` exists in the deployed environment, **When** the reviewer lists loans, searches by borrower name, and looks up the loan ID, **Then** each workflow returns `LN-001` with the existing response shape.
4. **Given** loan `LN-001` exists in the deployed environment, **When** the reviewer deletes it, **Then** future deployed listing, search, and lookup workflows no longer return it.

---

### User Story 2 - Preserve Loans Across Service Replacement (Priority: P2)

An authenticated reviewer can create loan records in the deployed environment
and still retrieve them after the running application task is restarted,
replaced, or redeployed.

**Why this priority**: Containerized application instances are disposable; loan
records must live outside any single running task.

**Independent Test**: Create a loan in the deployed environment, replace or
restart the running application task, then verify the loan remains available
through lookup, listing, and borrower-name search.

**Acceptance Scenarios**:

1. **Given** loan `LN-002` was created in the deployed environment, **When** the running application task is replaced, **Then** loan ID lookup still returns `LN-002`.
2. **Given** loan `LN-002` exists after a task replacement, **When** a reviewer submits another create request for `LN-002`, **Then** the existing duplicate-loan response is returned.
3. **Given** loan `LN-002` is deleted before a task replacement, **When** the replacement task starts, **Then** `LN-002` remains absent from lookup, listing, and borrower-name search.

---

### User Story 3 - Release The App Repeatably (Priority: P3)

A maintainer can build, publish, configure, deploy, verify, and document a new
application release without manually changing application files on a server.

**Why this priority**: The deployment needs to be repeatable and explainable,
not a one-off manual server setup.

**Independent Test**: From a clean checkout and an authorized cloud account, a
maintainer follows the documented release steps to publish an application
artifact, update the running service, and verify the health and loan workflows.

**Acceptance Scenarios**:

1. **Given** a maintainer has cloud permissions and required secrets, **When** they follow the documented release steps, **Then** a new application version is published and the running service uses it.
2. **Given** the service has been updated to a new version, **When** the maintainer checks service health, **Then** the deployed health endpoint reports healthy status.
3. **Given** a deploy fails health verification, **When** the maintainer inspects the documented rollback path, **Then** they can return the service to the previous working version without data loss.

### Edge Cases

- The deployed application starts with an empty managed loan database.
- The deployed application starts when loan records already exist.
- The application task is replaced while loan records exist.
- The application task is replaced after a loan has been deleted.
- Database connectivity is unavailable during startup or during a protected loan workflow.
- Required runtime configuration or secrets are missing.
- Authentication callback/logout origins do not include the deployed endpoint.
- A published application version fails health checks.
- A stale application version is accidentally redeployed.
- Two authenticated callers create the same loan ID at nearly the same time.
- Local development and automated tests must remain runnable without requiring production cloud resources.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a deployed environment where the existing website and protected loan API can be accessed without running Flask locally.
- **FR-002**: The deployed environment MUST preserve existing Auth0-protected access rules, authentication errors, success responses, validation responses, duplicate responses, not-found responses, and deletion responses.
- **FR-003**: The deployed environment MUST store loan records in managed durable relational storage rather than in a process-local dictionary or container-local file.
- **FR-004**: Loan records created in the deployed environment MUST remain available after the running application task is restarted, replaced, or redeployed.
- **FR-005**: Duplicate-loan detection in the deployed environment MUST include records created before a task restart, replacement, or redeploy.
- **FR-006**: Deleting a loan in the deployed environment MUST keep that loan absent after a task restart, replacement, or redeploy.
- **FR-007**: The deployed application MUST prepare or verify required loan storage schema automatically during startup or release without requiring manual database edits.
- **FR-008**: Storage and startup failures in the deployed environment MUST return clear service-unavailable feedback for protected loan workflows without exposing secrets.
- **FR-009**: Runtime configuration MUST support separate local/test and deployed environment settings without source-code edits between environments.
- **FR-010**: Required secrets and sensitive values MUST NOT be committed to the repository or printed in normal logs.
- **FR-011**: The release process MUST publish a versioned application artifact before updating the running service.
- **FR-012**: The release process MUST include a documented health verification step after deployment.
- **FR-013**: The release process MUST include a documented rollback path to a previous working application version.
- **FR-014**: Documentation MUST explain setup, cloud prerequisites, configuration, build, publish, deploy, verify, rollback, and teardown/reset steps.
- **FR-015**: Automated tests MUST continue to verify existing loan workflows and maintain statement coverage at or above 80%.
- **FR-016**: The feature MUST keep new business capabilities, roles, per-user loan ownership, Kubernetes, multi-region failover, and production compliance hardening out of scope.

### Key Entities *(include if feature involves data)*

- **Cloud Environment**: The deployed runtime where reviewers access the loan website and protected API.
- **Application Release**: A versioned deployable artifact used to update the running loan service.
- **Managed Loan Database**: Durable relational storage that holds current loan records outside any application task.
- **Runtime Configuration**: Environment-specific settings and secrets required by authentication, storage, and service startup.
- **Service Health State**: The deploy-time and runtime status used to decide whether the current application version is healthy or needs rollback.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reviewer can open the deployed website, sign in, and complete create, list, borrower search, lookup, and delete workflows successfully within 10 minutes of receiving the deployed endpoint.
- **SC-002**: After creating a loan in the deployed environment and replacing the running application task, the reviewer can retrieve that loan by loan ID, full listing, and borrower-name search within 2 seconds per action.
- **SC-003**: A duplicate create request for a loan ID created before task replacement returns the existing duplicate-loan response 100% of the time in automated or documented verification.
- **SC-004**: A deleted loan remains absent from lookup, listing, and borrower-name search after task replacement in automated or documented verification.
- **SC-005**: A maintainer can build, publish, deploy, verify, and roll back an application release by following repository documentation without manually editing files on a server.
- **SC-006**: The deployed service health endpoint reports a healthy status after successful deployment and fails deployment verification when the service is not reachable.
- **SC-007**: Repository tests continue to pass with at least 80% statement coverage.
- **SC-008**: The deployment architecture, persistence behavior, release flow, and out-of-scope boundaries can be explained in under 40 minutes.

## Assumptions

- AWS is the required target cloud provider for this feature.
- Amazon RDS, Amazon ECR, and Amazon ECS are stakeholder-mandated platform services for implementation planning.
- The first target is a single non-production demo environment, not a highly available production deployment.
- The existing Auth0 tenant, API audience, protected endpoint behavior, and website sign-in model will be reused.
- The deployed endpoint can initially use a managed load balancer URL unless a custom domain and certificate are provided before implementation.
- The cloud account, permissions, network quotas, and billing access needed for the environment will be available to the maintainer.
- Local development and CI-style tests may use local or isolated test storage, but deployed runtime must not depend on SQLite.
- Existing loan records are current-state demo data only; historical audit trails and complex schema migrations are out of scope for this feature.
- Secrets will be provided through environment configuration or managed secret storage, not committed repository files.
