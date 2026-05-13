from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_readme_documents_core_commands_and_aws_flow():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "pip install -r requirements.txt" in readme
    assert "flask --app app run --debug" in readme
    assert "pytest --cov=app --cov-report=term-missing --cov-fail-under=80" in readme
    assert "AUTH0_DOMAIN" in readme
    assert "AUTH0_CLIENT_ID" in readme
    assert "AUTH0_CLIENT_SECRET" in readme
    assert "AUTH0_AUDIENCE" in readme
    assert "APP_SECRET_KEY" in readme
    assert ".env` files are ignored by git" in readme
    assert "LOAN_DATABASE_PATH" in readme
    assert "DATABASE_URL" in readme
    assert "LOAN_REQUIRE_DATABASE_URL=true" in readme
    assert "instance/loans.sqlite3" in readme
    assert "SQLite" in readme
    assert "PostgreSQL/RDS" in readme
    assert "infra/aws/bootstrap" in readme
    assert "infra/aws/app" in readme
    assert "terraform apply" in readme
    assert "ecr_repository_url" in readme
    assert "service_url" in readme
    assert "ecs_cluster_name" in readme
    assert "ecs_service_name" in readme
    assert "GET /" in readme
    assert "GET /login" in readme
    assert "GET /auth/status" in readme
    assert "POST /loans" in readme
    assert "GET /loans?borrowerName=<borrowerName>" in readme
    assert "DELETE /loans/<loanId>" in readme
    assert "curl -i http://127.0.0.1:5000/health" in readme
    assert "docker build -t yl-loans:local ." in readme
    assert "docker push" in readme
    assert "app/auth.py" in readme
    assert "app/repositories/loan_repository.py" in readme
    assert "app/repositories/postgres_loan_repository.py" in readme
    assert "app/repositories/repository_factory.py" in readme
    assert "aws ecs update-service" in readme
    assert "force-new-deployment" in readme
    assert "Trade-Offs and Assumptions" not in readme
    assert "Out of scope" not in readme
    assert "Demo:" not in readme
    assert "process-local" not in readme


def test_aws_deployment_contract_documents_required_runtime_and_outputs():
    contract = (
        ROOT
        / "specs"
        / "011-aws-ecs-rds-deploy"
        / "contracts"
        / "deployment-config.md"
    ).read_text(encoding="utf-8")
    quickstart = (
        ROOT / "specs" / "011-aws-ecs-rds-deploy" / "quickstart.md"
    ).read_text(encoding="utf-8")

    for required in (
        "DATABASE_URL",
        "AUTH0_DOMAIN",
        "AUTH0_CLIENT_ID",
        "AUTH0_CLIENT_SECRET",
        "AUTH0_AUDIENCE",
        "APP_SECRET_KEY",
        "LOAN_REQUIRE_DATABASE_URL",
        "image_uri",
        "service_url",
        "ecs_cluster_name",
        "ecs_service_name",
        "rds_endpoint",
    ):
        assert required in contract

    assert "terraform.tfvars" in quickstart
    assert "docker build" in quickstart
    assert "docker push" in quickstart
    assert "terraform apply" in quickstart
    assert "terraform destroy" in quickstart
    assert "aws ecs update-service" in quickstart
    assert "force-new-deployment" in quickstart


def test_loan_website_quickstart_documents_browser_demo_and_validation():
    quickstart = (
        ROOT / "specs" / "006-loan-website" / "quickstart.md"
    ).read_text(encoding="utf-8")

    assert "pip install -r requirements.txt" in quickstart
    assert "flask --app app run --debug" in quickstart
    assert "Open `http://127.0.0.1:5000/` in a browser." in quickstart
    assert "Loan ID: LN-001" in quickstart
    assert "Borrower name: Jane Smith" in quickstart
    assert "duplicate-loan feedback" in quickstart
    assert "Search by borrower name `Jane Smith`" in quickstart
    assert "Look up loan ID `LN-001`" in quickstart
    assert "Delete loan ID `LN-001`" in quickstart
    assert "No primary workflow requires horizontal scrolling." in quickstart
    assert "within 2 seconds" in quickstart
    assert "pytest --cov=app --cov-report=term-missing --cov-fail-under=80" in quickstart


def test_loan_deletion_quickstart_documents_core_commands_and_demo_flow():
    quickstart = (
        ROOT / "specs" / "005-loan-deletion" / "quickstart.md"
    ).read_text(encoding="utf-8")

    assert "pip install -r requirements.txt" in quickstart
    assert "flask --app app run --debug" in quickstart
    assert "pytest --cov=app --cov-report=term-missing --cov-fail-under=80" in quickstart
    assert "POST http://127.0.0.1:5000/loans" in quickstart
    assert "curl -i http://127.0.0.1:5000/loans" in quickstart
    assert "curl -i -X DELETE http://127.0.0.1:5000/loans/LN-001" in quickstart
    assert "curl -i -X DELETE http://127.0.0.1:5000/loans/LN-MISSING" in quickstart
    assert 'curl -i "http://127.0.0.1:5000/loans?borrowerName=Jane%20Smith"' in quickstart
    assert "deleted loan record" in quickstart
    assert "404 Not Found" in quickstart
    assert "without `LN-001`" in quickstart
    assert "Restart Behavior" in quickstart
    assert "201 Created" in quickstart
