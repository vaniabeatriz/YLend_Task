# Data Model: AWS ECS RDS Deployment

## Durable Loan Record

Represents the current loan data already exposed through the API and website.

**Fields**:

- `sequence`: database-generated insertion-order value used for stable listing
- `loan_id`: unique loan identifier, required
- `borrower_name`: normalized borrower name, required
- `funding_amount`: decimal amount stored without floating-point rounding loss
- `repayment_amount`: decimal amount stored without floating-point rounding loss

**Validation Rules**:

- `loan_id`, `borrower_name`, `funding_amount`, and `repayment_amount` keep the
  existing service validation rules.
- `loan_id` remains globally unique across current records.
- Failed validation, authentication, and duplicate requests must not create or
  mutate records.

**State Transitions**:

- Created: authenticated create request inserts a new durable record.
- Current: record appears in listing, borrower search, and loan ID lookup.
- Deleted: authenticated delete request removes the record and returns the
  deleted loan response; record remains absent after task replacement.

## Managed Loan Database

Represents the deployed relational database that stores `Durable Loan Record`
rows outside ECS task storage.

**Fields/Attributes**:

- database endpoint and port
- database name
- application database user
- secret reference for credentials or connection URL
- storage schema version implied by table definition

**Validation Rules**:

- Must be reachable only from the deployed application service security group.
- Must not require manual table edits before the app can serve loan workflows.
- Must not be replaced during normal application image deployments.

## Application Release

Represents a versioned container image published before updating the deployed
service.

**Fields/Attributes**:

- image repository URL
- image tag
- source revision used to build the image
- deployment timestamp

**Validation Rules**:

- The release tag must be documented or discoverable before service update.
- The service must verify health after switching to the release.
- A previous known-good image tag must be usable for rollback.

## Cloud Service

Represents the running deployed application.

**Fields/Attributes**:

- public service URL
- ECS cluster name
- ECS service name
- task definition revision
- desired task count
- health check path

**Validation Rules**:

- Health check path must use the existing public health endpoint.
- Runtime configuration must include authentication settings, secret key, and
  managed database connection information.
- Protected workflows must fail closed when required configuration is missing.
