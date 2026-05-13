# Deployment Configuration Contract

This contract defines the configuration surface for the AWS ECS/RDS deployment.
Existing HTTP API response contracts remain unchanged from earlier feature
specifications.

## Runtime Environment

The deployed ECS task must receive these settings through environment variables
or ECS secret injection:

| Name | Required | Secret | Purpose |
|------|----------|--------|---------|
| `DATABASE_URL` or `LOAN_DATABASE_URL` | Yes in deployed runtime | Yes | RDS PostgreSQL connection URL used by the deployed loan repository |
| `AUTH0_DOMAIN` | Yes | No | Existing Auth0 tenant domain |
| `AUTH0_CLIENT_ID` | Yes | No | Existing Auth0 application client ID |
| `AUTH0_CLIENT_SECRET` | Yes | Yes | Existing Auth0 application client secret |
| `AUTH0_AUDIENCE` | Yes | No | Existing Auth0 API audience |
| `AUTH0_CALLBACK_URL` | Yes | No | Callback URL for the deployed website |
| `AUTH0_LOGOUT_RETURN_URL` | Yes | No | Logout return URL for the deployed website |
| `APP_SECRET_KEY` | Yes | Yes | Flask session secret |
| `LOAN_REQUIRE_DATABASE_URL` | Yes in ECS | No | Forces deployed runtime to fail closed when RDS configuration is missing |
| `FLASK_ENV` | No | No | Runtime environment marker; must not enable debug in deployed runtime |

## Infrastructure Inputs

The AWS deployment plan must support these operator-provided values:

| Name | Required | Example | Purpose |
|------|----------|---------|---------|
| `aws_region` | Yes | `eu-west-2` | AWS region for all resources |
| `project_name` | Yes | `yl-loans` | Prefix for named resources |
| `environment` | Yes | `demo` | Environment label |
| `image_uri` | Yes after ECR bootstrap | `<account>.dkr.ecr.<region>.amazonaws.com/<repo>:<tag>` | Container image to run in ECS |
| `auth0_domain` | Yes | `tenant.eu.auth0.com` | Non-secret Auth0 setting |
| `auth0_client_id` | Yes | `...` | Non-secret Auth0 setting |
| `auth0_audience` | Yes | `https://your-loan-api` | Non-secret Auth0 setting |
| `auth0_client_secret` | Yes | supplied securely | Secret Auth0 setting |
| `app_secret_key` | Yes | supplied securely | Secret Flask setting |
| `desired_count` | No | `1` | Number of ECS tasks for the demo service |
| `task_cpu` | No | `256` | Fargate CPU units |
| `task_memory` | No | `512` | Fargate memory in MiB |
| `db_instance_class` | No | `db.t4g.micro` | RDS instance size for the demo database |

## Infrastructure Outputs

The AWS deployment must expose these values after apply:

| Output | Purpose |
|--------|---------|
| `ecr_repository_url` | Image repository target for Docker push |
| `service_url` | Public deployed website/API base URL |
| `ecs_cluster_name` | ECS cluster used for verification and rollback commands |
| `ecs_service_name` | ECS service used for verification and forced replacement tests |
| `rds_endpoint` | Database endpoint for operator visibility, not for public access |
| `image_uri` | Image URI currently configured in the ECS task definition |

## Health Contract

The deployed service must preserve the existing health response:

```http
GET /health
```

Expected successful response:

```json
{
  "status": "ok"
}
```

## Persistence Verification Contract

1. Create a loan in the deployed environment.
2. Force replacement of the running application task or deploy a new image.
3. Retrieve the same loan by loan ID, full listing, and borrower-name search.
4. Verify duplicate create still returns the existing duplicate response.
5. Delete the loan and verify it remains absent after another task replacement.
