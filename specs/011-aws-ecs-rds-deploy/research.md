# Research: AWS ECS RDS Deployment

## Decision: Use RDS PostgreSQL For Deployed Loan Storage

**Rationale**: PostgreSQL satisfies the managed relational database requirement,
supports unique constraints needed for duplicate loan IDs, works cleanly with a
small DB-API repository, and keeps the schema close to the current SQLite table.
The app can continue storing monetary values as decimal text to preserve
existing JSON response behaviour and avoid introducing rounding changes.

**Alternatives considered**:

- **RDS MySQL**: Also viable, but does not provide a meaningful advantage for
  this project and would require a different driver.
- **Aurora**: More operational capability than needed for a single demo
  environment.
- **SQLite on container disk or network storage**: Does not satisfy the RDS
  requirement and weakens task replacement persistence.

## Decision: Select Storage By Runtime Configuration

**Rationale**: A repository factory can choose the deployed PostgreSQL
repository when `DATABASE_URL` or `LOAN_DATABASE_URL` is configured, while
preserving the existing SQLite repository for local development and isolated
tests. Deployed ECS runtime will be configured to require the RDS-backed URL so
the cloud service does not silently fall back to SQLite.

**Alternatives considered**:

- **Remove SQLite entirely**: Makes local development and automated tests depend
  on a running database service, increasing setup cost for reviewers.
- **Keep only SQLite and sync elsewhere**: Does not satisfy the requirement to
  use RDS as the deployed durable store.
- **Use an ORM**: Adds abstraction and dependency weight that is not needed for
  one table and five CRUD-style workflows.

## Decision: Use ECS Fargate Behind An Application Load Balancer

**Rationale**: Fargate keeps the deployment focused on the containerized Flask
service without EC2 host management. An Application Load Balancer provides a
stable HTTP endpoint and health checks for `/health`. This directly satisfies
the ECS requirement while keeping operations explainable.

**Alternatives considered**:

- **ECS on EC2**: Adds instance lifecycle, AMI, patching, and capacity concerns
  that are not needed for the demo.
- **Elastic Beanstalk or App Runner**: Simpler in some cases, but does not make
  ECS the primary runtime as requested.
- **Kubernetes/EKS**: Explicitly out of scope and too heavy for this project.

## Decision: Publish Versioned Images To ECR

**Rationale**: ECR is the requested registry and integrates with ECS task
definitions. Tagging images with a stable value such as the git SHA makes
deployments and rollbacks easier to explain than mutable-only tags.

**Alternatives considered**:

- **Docker Hub or GitHub Container Registry**: Would not satisfy the requested
  ECR usage.
- **Build image directly inside ECS**: ECS runs images; it does not replace a
  registry-backed image release flow.

## Decision: Use Terraform For Minimal AWS Infrastructure

**Rationale**: Terraform gives a reviewable, repeatable definition for ECR, ECS,
RDS, networking, security groups, load balancer, task definition, and service
outputs. Splitting `infra/aws/bootstrap` and `infra/aws/app` keeps first-image
publishing understandable.

**Alternatives considered**:

- **Manual AWS Console setup**: Fast once, but hard to reproduce, review, or
  teardown.
- **Ad hoc AWS CLI scripts only**: Scriptable but more brittle for dependency
  ordering and stateful infrastructure.
- **AWS Copilot**: Useful for ECS apps, but it hides enough infrastructure that
  the RDS/ECR/ECS design is harder to inspect in a technical-test repository.

## Decision: Keep Secrets Out Of Source And Document State Risk

**Rationale**: Auth0 client secret, Flask secret key, and database credentials
must not be committed. ECS task secrets should read values from managed secret
storage. If Terraform creates non-production secrets, the Terraform state must
be protected and ignored by git because state can contain sensitive values.

**Alternatives considered**:

- **Plain environment variables in committed task definitions**: Exposes
  secrets and violates the feature requirements.
- **Hard-coded demo credentials**: Simpler but not defensible.
- **Manual edits after deploy**: Makes the release process less repeatable.
