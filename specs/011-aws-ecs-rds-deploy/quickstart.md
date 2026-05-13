# Quickstart: AWS ECS RDS Deployment

This quickstart keeps the AWS flow small and repeatable: create ECR, push one
image, deploy one ECS service with one RDS database, verify, and tear down.

## Prerequisites

- AWS account with permissions to create ECR, ECS, RDS, IAM, VPC, security
  group, load balancer, and secret resources
- AWS CLI authenticated to the target account
- Docker installed and running locally
- Terraform 1.5 or newer installed locally
- Existing Auth0 application and API configuration
- Python virtual environment for running repository tests locally

## Local Verification Before Deployment

```bash
source .venv/bin/activate
.venv/bin/python -m pytest --cov=app --cov-report=term-missing --cov-fail-under=80
```

## Bootstrap ECR

```bash
cd infra/aws/bootstrap
terraform init
terraform apply \
  -var='aws_region=eu-west-2' \
  -var='project_name=yl-loans' \
  -var='environment=demo'
```

Capture the `ecr_repository_url` output.

## Build And Push Image

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

## Deploy ECS And RDS Runtime

Create `infra/aws/app/terraform.tfvars` locally. It is ignored by git because
it contains secrets:

```hcl
aws_region          = "eu-west-2"
project_name        = "yl-loans"
environment         = "demo"
image_uri           = "<ecr_repository_url>:<image_tag>"
auth0_domain        = "your-tenant.auth0.com"
auth0_client_id     = "your-client-id"
auth0_audience      = "https://your-loan-api"
auth0_client_secret = "provide-securely"
app_secret_key      = "provide-securely"
```

Then apply the app module:

```bash
cd ../app
terraform init
terraform apply
```

Capture the `service_url` output.

Terraform state can contain sensitive values. Keep local state and tfvars out
of git, and do not paste state output into tickets or chats.

## Update Auth0 URLs

In Auth0, add the deployed service URL:

- Allowed Callback URLs: `<service_url>/callback`
- Allowed Logout URLs: `<service_url>/`
- Allowed Web Origins: `<service_url>`

## Smoke Test

```bash
curl -i "<service_url>/health"
```

Expected response:

```json
{
  "status": "ok"
}
```

Then open `<service_url>/`, sign in, and run the website demo flow from the
README against the deployed environment.

## Persistence Replacement Test

1. Create loan `LN-AWS-001` for borrower `Jane Smith`.
2. Verify lookup, listing, and borrower search return the loan.
3. Force an ECS task replacement:

```bash
aws ecs update-service \
  --cluster "<ecs_cluster_name>" \
  --service "<ecs_service_name>" \
  --force-new-deployment \
  --region "$AWS_REGION"
```

4. Wait for the service to stabilize.
5. Verify lookup, listing, and borrower search still return `LN-AWS-001`.
6. Delete `LN-AWS-001`, force another replacement, and verify it remains absent.

## Rollback

Redeploy the previous known-good image tag by applying the app Terraform module
with the previous `image_uri`, then repeat the health check and persistence
verification.

```bash
cd infra/aws/app
# Edit local terraform.tfvars so image_uri points to the previous tag.
terraform apply
curl -i "<service_url>/health"
```

## Teardown

For a disposable demo environment:

```bash
cd infra/aws/app
terraform destroy

cd ../bootstrap
terraform destroy
```

Before teardown, confirm no reviewer needs the demo loan data.
