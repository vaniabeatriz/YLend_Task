# Loan Management API and Website

Flask app for the YouLend technical task. It provides a small browser website
and an Auth0 protected JSON API for creating, listing, searching, looking up,
and deleting loan records.

The project can run in two ways:

- Locally, with SQLite stored under `instance/`.
- On AWS, with a Docker image in ECR, the app running on ECS Fargate behind an
  App Load Balancer, and loan data stored in PostgreSQL/RDS.

## What This App Does

- Serves the website at `GET /`.
- Uses Auth0 for sign-in and API token validation.
- Stores local development data in SQLite by default.
- Stores deployed AWS data in PostgreSQL/RDS when `DATABASE_URL` or
  `LOAN_DATABASE_URL` is configured.
- Provides a public health check at `GET /health`.

## Endpoints

Public endpoints:

- `GET /`
- `GET /login`
- `GET /callback`
- `GET /logout`
- `GET /auth/status`
- `GET /health`

Protected loan endpoints:

- `POST /loans`
- `GET /loans`
- `GET /loans?borrowerName=<borrowerName>`
- `GET /loans/<loanId>`
- `DELETE /loans/<loanId>`

All loan endpoints require a valid Auth0 bearer token. The website gets that
token through the Auth0 login flow. Direct `curl` calls must send:

```bash
Authorization: Bearer <access-token>
```

## Prerequisites

For local development:

- Python 3.11 or newer
- `pip`
- An Auth0 Regular Web Application
- An Auth0 API

For Docker:

- Docker installed and running

For AWS deployment:

- AWS CLI authenticated to the target account
- Docker installed and running
- Terraform 1.5 or newer
- AWS permissions to create ECR, ECS, RDS, IAM, VPC, security groups, load
  balancer, Secrets Manager, and CloudWatch log resources

## Local Setup

Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a local `.env` file. `.env` files are ignored by git, so secrets stay
out of the repository.

```bash
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret
AUTH0_AUDIENCE=https://your-loan-api
AUTH0_CALLBACK_URL=http://127.0.0.1:5000/callback
AUTH0_LOGOUT_RETURN_URL=http://127.0.0.1:5000/
APP_SECRET_KEY=replace-with-a-long-random-value
LOAN_DATABASE_PATH=instance/loans.sqlite3
```

You can generate a local Flask secret with:

```bash
openssl rand -hex 32
```

## Auth0 Local Configuration

Create or reuse:

- An Auth0 Regular Web Application for browser login.
- An Auth0 API for validating access tokens.

In the Auth0 application, add these local URLs:

- Allowed Callback URLs: `http://127.0.0.1:5000/callback`
- Allowed Logout URLs: `http://127.0.0.1:5000/`
- Allowed Web Origins: `http://127.0.0.1:5000`

Use the Auth0 API `Identifier` as `AUTH0_AUDIENCE`.

## Run Locally

Start the Flask development server:

```bash
source .venv/bin/activate
flask --app app run --debug
```

Open the website:

```text
http://127.0.0.1:5000/
```

Check the health endpoint:

```bash
curl -i http://127.0.0.1:5000/health
```

Expected response body:

```json
{"status":"ok"}
```

Local data is written to:

```text
instance/loans.sqlite3
```

That file is intentionally ignored by git. If AWS is offline, this local setup
is enough to review the main website, Auth0 login, and loan workflows.

## Local Workflow To Review The App

1. Start the app with `flask --app app run --debug`.
2. Open `http://127.0.0.1:5000/`.
3. Sign in through Auth0.
4. Create a loan, for example `LN-001` for borrower `Jane Smith`.
5. Confirm the loan appears in the full list.
6. Search by borrower name.
7. Look up the loan by ID.
8. Delete the loan.
9. Refresh the list and confirm the loan is gone.

## Example API Calls

These examples assume you already have an Auth0 access token for the configured
API audience:

```bash
export TOKEN="<access-token>"
```

Create a loan:

```bash
curl -i -X POST http://127.0.0.1:5000/loans \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "loanId": "LN-001",
    "borrowerName": "Jane Smith",
    "fundingAmount": 1000.0,
    "repaymentAmount": 1200.0
  }'
```

List loans:

```bash
curl -i http://127.0.0.1:5000/loans \
  -H "Authorization: Bearer $TOKEN"
```

Search by borrower name:

```bash
curl -i "http://127.0.0.1:5000/loans?borrowerName=Jane%20Smith" \
  -H "Authorization: Bearer $TOKEN"
```

Look up one loan:

```bash
curl -i http://127.0.0.1:5000/loans/LN-001 \
  -H "Authorization: Bearer $TOKEN"
```

Delete one loan:

```bash
curl -i -X DELETE http://127.0.0.1:5000/loans/LN-001 \
  -H "Authorization: Bearer $TOKEN"
```

## Storage Modes

Local mode uses SQLite:

```bash
LOAN_DATABASE_PATH=instance/loans.sqlite3
```

AWS mode uses PostgreSQL/RDS:

```bash
DATABASE_URL=postgresql://...
```

or:

```bash
LOAN_DATABASE_URL=postgresql://...
```

The ECS task also sets:

```bash
LOAN_REQUIRE_DATABASE_URL=true
```


## Docker

Build the image:

```bash
docker build -t yl-loans:local .
```

Run the image locally with SQLite:

```bash
docker run --rm -p 5000:5000 \
  -e AUTH0_DOMAIN="your-tenant.auth0.com" \
  -e AUTH0_CLIENT_ID="your-client-id" \
  -e AUTH0_CLIENT_SECRET="your-client-secret" \
  -e AUTH0_AUDIENCE="https://your-loan-api" \
  -e AUTH0_CALLBACK_URL="http://127.0.0.1:5000/callback" \
  -e AUTH0_LOGOUT_RETURN_URL="http://127.0.0.1:5000/" \
  -e APP_SECRET_KEY="$(openssl rand -hex 32)" \
  -e LOAN_DATABASE_PATH=/tmp/loans.sqlite3 \
  yl-loans:local
```

The container runs Gunicorn on port `5000`.

## Tests

Run the full test suite with the required coverage gate:

```bash
source .venv/bin/activate
pytest --cov=app --cov-report=term-missing --cov-fail-under=80
```

The tests configure authentication for test scenarios and do not require a real
Auth0 login.

## AWS Overview

Infrastructure lives under `infra/aws`.

- `infra/aws/bootstrap` creates the ECR repository first.
- `infra/aws/app` creates the ECS Fargate service, ALB, RDS PostgreSQL database,
  Secrets Manager values, security groups, IAM roles, and CloudWatch logs.

The AWS environment is a non-production demo environment. It uses HTTP on the
load balancer and a small RDS instance. 

Local Terraform state, plans, `.env`, `terraform.tfvars`, and local databases
are ignored by git.

## Why The AWS Demo Uses HTTP

HTTPS was intentionally left out of this demo deployment to keep the cloud
setup small, fast to explain, and easy to recreate. The requirement being
demonstrated here is the application running on AWS with ECR, ECS Fargate, an
Application Load Balancer, and durable RDS PostgreSQL storage. Adding HTTPS
would require extra infrastructure that is not needed to prove that path, such
as a custom domain, DNS validation, an ACM certificate, a `443` load balancer
listener, and an HTTP-to-HTTPS redirect.

For a production deployment, HTTPS should be added before real users or real
data are used. The expected production change would be:

1. Register or reuse a domain.
2. Create an ACM certificate in the same AWS region as the load balancer.
3. Validate the certificate through DNS.
4. Add an HTTPS listener on port `443`.
5. Redirect port `80` traffic to HTTPS.
6. Update Auth0 callback, logout, and web origin URLs to use `https://`.
7. Set secure session cookie settings for the HTTPS environment.

## AWS Step 1: Create ECR

```bash
cd infra/aws/bootstrap
terraform init
terraform apply \
  -var='aws_region=eu-west-2' \
  -var='project_name=yl-loans' \
  -var='environment=demo'
```

Capture the output:

```bash
terraform output -raw ecr_repository_url
```

## AWS Step 2: Build And Push The Image

From the repository root:

```bash
export AWS_REGION=eu-west-2
export ECR_REPOSITORY_URL="<ecr_repository_url>"
export IMAGE_TAG="$(git rev-parse --short HEAD)"

aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "$ECR_REPOSITORY_URL"

docker build -t "yl-loans:$IMAGE_TAG" .
docker tag "yl-loans:$IMAGE_TAG" "$ECR_REPOSITORY_URL:$IMAGE_TAG"
docker push "$ECR_REPOSITORY_URL:$IMAGE_TAG"
```

The final image URI will look like:

```text
<ecr_repository_url>:<image_tag>
```

## AWS Step 3: Create App Terraform Variables

Create `infra/aws/app/terraform.tfvars` locally:

```hcl
aws_region          = "eu-west-2"
project_name        = "yl-loans"
environment         = "demo"
image_uri           = "<ecr_repository_url>:<image_tag>"
auth0_domain        = "your-tenant.auth0.com"
auth0_client_id     = "your-client-id"
auth0_audience      = "https://your-loan-api"
auth0_client_secret = "your-client-secret"
app_secret_key      = "replace-with-a-long-random-value"
```

Optional sizing values:

```hcl
desired_count     = 1
task_cpu          = 256
task_memory       = 512
db_instance_class = "db.t4g.micro"
```

Do not commit `terraform.tfvars`. Terraform state can also contain sensitive
values, so keep local state files private.

## AWS Step 4: Deploy ECS And RDS

```bash
cd infra/aws/app
terraform init
terraform apply
```

Capture the main outputs:

```bash
terraform output -raw service_url
terraform output -raw ecs_cluster_name
terraform output -raw ecs_service_name
terraform output -raw rds_endpoint
terraform output -raw image_uri
```

## AWS Step 5: Update Auth0 For The AWS URL

After deployment, add the deployed `service_url` to the Auth0 application:

- Allowed Callback URLs: `<service_url>/callback`
- Allowed Logout URLs: `<service_url>/`
- Allowed Web Origins: `<service_url>`

Then open `<service_url>/` in the browser and sign in.

## AWS Step 6: Verify The Deployment

Health check:

```bash
curl -i "<service_url>/health"
```

Expected response body:

```json
{"status":"ok"}
```

Website verification:

1. Open `<service_url>/`.
2. Sign in with Auth0.
3. Create a loan.
4. List loans.
5. Search by borrower name.
6. Look up the loan by ID.
7. Delete the loan.

Persistence verification:

1. Create a loan, for example `LN-AWS-001` for borrower `Jane Smith`.
2. Confirm lookup, listing, and borrower search all return the loan.
3. Force an ECS task replacement:

```bash
aws ecs update-service \
  --cluster "<ecs_cluster_name>" \
  --service "<ecs_service_name>" \
  --force-new-deployment \
  --region "$AWS_REGION"
```

4. Wait for the ECS service to stabilize.
5. Confirm the same loan is still available.
6. Delete the loan.
7. Force another task replacement and confirm the loan remains deleted.

This proves that AWS is using RDS, not temporary container storage.

## AWS Rollback

To roll back, point `image_uri` in `infra/aws/app/terraform.tfvars` to a previous
known-good ECR image tag and apply again:

```bash
cd infra/aws/app
terraform apply
curl -i "<service_url>/health"
```

After rollback, repeat the website workflow and persistence verification.

## AWS Shutdown

To stop AWS costs for this disposable environment, destroy the app resources
first, then the bootstrap resources:

```bash
cd infra/aws/app
terraform destroy

cd ../bootstrap
terraform destroy
```

Destroying the app module removes the ECS service, ALB, RDS database, secrets,
logs, and network resources. RDS is configured with `skip_final_snapshot = true`
for this demo environment, so data is not preserved after destroy.

If reviewers need to run the project while AWS is shut down, use the local setup
section. If AWS needs to be restored, rerun the AWS steps from ECR creation,
image push, app deploy, and Auth0 URL update.

## Troubleshooting

If the website loads but login does not start, check the Auth0 values in `.env`
or `terraform.tfvars`.

If login succeeds but API calls return `401`, check that `AUTH0_AUDIENCE`
matches the Auth0 API Identifier and that the token was issued for that
audience.

If AWS health check fails, check ECS task logs in CloudWatch under:

```text
/ecs/yl-loans-demo
```

If AWS loan endpoints return a storage error, check that the ECS task has
`DATABASE_URL` injected from Secrets Manager and
`LOAN_REQUIRE_DATABASE_URL=true`.

If local loan data looks stale, stop Flask and remove the local SQLite file:

```bash
rm instance/loans.sqlite3
```

## Architecture

- `app/auth.py`: Auth0 login, logout, sessions, and bearer-token validation.
- `app/routes.py`: Flask routes and JSON responses.
- `app/services/loan_service.py`: validation and loan workflow rules.
- `app/repositories/loan_repository.py`: SQLite repository.
- `app/repositories/postgres_loan_repository.py`: PostgreSQL/RDS repository.
- `app/repositories/repository_factory.py`: runtime storage selection.
- `app/templates/index.html`: browser website.
- `app/static/`: website CSS and JavaScript.
- `infra/aws/`: Terraform for ECR, ECS, ALB, RDS, secrets, and logs.
- `tests/`: unit and integration tests.
