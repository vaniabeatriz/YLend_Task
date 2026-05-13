# Loan Management API and Website

Flask app for the YouLend technical task. It provides a small website and
authenticated JSON API for creating, listing, searching, looking up, and
deleting loan records.

## Endpoints

- `GET /`
- `GET /login`
- `GET /callback`
- `GET /logout`
- `GET /auth/status`
- `GET /health`
- `POST /loans`
- `GET /loans`
- `GET /loans?borrowerName=<borrowerName>`
- `GET /loans/<loanId>`
- `DELETE /loans/<loanId>`

Loan endpoints require a valid Auth0 bearer token. `/`, `/login`, `/callback`,
`/logout`, `/auth/status`, and `/health` are public.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Auth0

Create an Auth0 Regular Web Application and an Auth0 API.

Local application URLs:

- Allowed Callback URLs: `http://127.0.0.1:5000/callback`
- Allowed Logout URLs: `http://127.0.0.1:5000/`
- Allowed Web Origins: `http://127.0.0.1:5000`

Use the Auth0 API `Identifier` as `AUTH0_AUDIENCE`.

Local environment:

```bash
export AUTH0_DOMAIN="your-tenant.auth0.com"
export AUTH0_CLIENT_ID="your-client-id"
export AUTH0_CLIENT_SECRET="your-client-secret"
export AUTH0_AUDIENCE="https://your-loan-api"
export AUTH0_CALLBACK_URL="http://127.0.0.1:5000/callback"
export AUTH0_LOGOUT_RETURN_URL="http://127.0.0.1:5000/"
export APP_SECRET_KEY="$(openssl rand -hex 32)"
```

`.env` files are ignored by git.

## Storage

Local runs use SQLite by default:

```bash
export LOAN_DATABASE_PATH="instance/loans.sqlite3"
```

AWS ECS uses PostgreSQL/RDS when `DATABASE_URL` or `LOAN_DATABASE_URL` is set.
The ECS task also sets:

```bash
LOAN_REQUIRE_DATABASE_URL=true
```

This prevents the deployed app from falling back to container-local SQLite.

## Run Locally

```bash
flask --app app run --debug
```

Open:

```text
http://127.0.0.1:5000/
```

Health check:

```bash
curl -i http://127.0.0.1:5000/health
```

Expected response:

```json
{"status":"ok"}
```

## Docker

```bash
docker build -t yl-loans:local .
docker run --rm -p 5000:5000 \
  -e LOAN_DATABASE_PATH=/tmp/loans.sqlite3 \
  yl-loans:local
```

If local port `5000` is busy:

```bash
docker run --rm -p 5001:5000 \
  -e LOAN_DATABASE_PATH=/tmp/loans.sqlite3 \
  yl-loans:local
```

## AWS

Infrastructure lives under `infra/aws`.

- `infra/aws/bootstrap`: creates the ECR repository.
- `infra/aws/app`: creates ALB, ECS Fargate, RDS PostgreSQL, Secrets Manager,
  and CloudWatch logs.

Local Terraform state, plans, `.env`, `terraform.tfvars`, and local databases
are ignored by git.

Create ECR:

```bash
cd infra/aws/bootstrap
terraform init
terraform apply \
  -var='aws_region=eu-west-2' \
  -var='project_name=yl-loans' \
  -var='environment=demo'
```

Build and push the image:

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

Create `infra/aws/app/terraform.tfvars` locally with the required image URI,
Auth0 values, and secrets. Then deploy:

```bash
cd ../app
terraform init
terraform apply
```

After deployment, add the `service_url` output to the Auth0 application:

- Allowed Callback URLs: `<service_url>/callback`
- Allowed Logout URLs: `<service_url>/`
- Allowed Web Origins: `<service_url>`

Check the deployed app:

```bash
curl -i "<service_url>/health"
```

## Persistence Check

1. Sign in on the deployed site.
2. Create loan `LN-AWS-001`.
3. Confirm it appears in list, borrower search, and loan ID lookup.
4. Force a new ECS deployment:

```bash
aws ecs update-service \
  --cluster "<ecs_cluster_name>" \
  --service "<ecs_service_name>" \
  --force-new-deployment \
  --region "$AWS_REGION"
```

5. Wait for the service to stabilize.
6. Confirm `LN-AWS-001` is still available.

That verifies loan data is stored in RDS, not in the ECS task.

## Tests

```bash
pytest --cov=app --cov-report=term-missing --cov-fail-under=80
```

Latest local result: `128 passed`; total coverage `86.89%`.

## Architecture

- `app/auth.py`: Auth0 login, logout, sessions, and token validation.
- `app/routes.py`: Flask routes and JSON responses.
- `app/services/loan_service.py`: validation and loan workflow rules.
- `app/repositories/loan_repository.py`: SQLite repository.
- `app/repositories/postgres_loan_repository.py`: PostgreSQL/RDS repository.
- `app/repositories/repository_factory.py`: runtime storage selection.
- `app/templates/index.html`: website.
- `app/static/`: website CSS and JavaScript.
- `infra/aws/`: Terraform for ECR, ECS, ALB, RDS, secrets, and logs.
- `tests/`: unit and integration tests.
