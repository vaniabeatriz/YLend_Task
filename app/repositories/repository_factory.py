import os
from pathlib import Path

from app.repositories.loan_repository import LoanStorageError, SQLiteLoanRepository
from app.repositories.postgres_loan_repository import PostgresLoanRepository


class UnavailableLoanRepository:
    """Placeholder used when storage setup fails before a real repository exists."""

    def initialize(self):
        return None


def create_loan_repository(config):
    database_url = (
        config.get("LOAN_DATABASE_URL")
        or config.get("DATABASE_URL")
        or os.environ.get("LOAN_DATABASE_URL")
        or os.environ.get("DATABASE_URL")
    )
    if database_url:
        config["LOAN_DATABASE_URL"] = database_url
        return PostgresLoanRepository(database_url)

    if _requires_database_url(config):
        raise LoanStorageError("RDS database URL is required for deployed runtime.")

    database_path = config.get("LOAN_DATABASE_PATH") or os.environ.get(
        "LOAN_DATABASE_PATH"
    )
    if not database_path:
        database_path = str(Path(config["INSTANCE_PATH"]) / "loans.sqlite3")
    config["LOAN_DATABASE_PATH"] = database_path
    return SQLiteLoanRepository(database_path)


def _requires_database_url(config):
    configured = config.get("LOAN_REQUIRE_DATABASE_URL")
    if isinstance(configured, str):
        return configured.strip().lower() in {"1", "true", "yes", "on"}
    if configured is not None:
        return bool(configured)

    env_value = os.environ.get("LOAN_REQUIRE_DATABASE_URL")
    if env_value is not None:
        return env_value.strip().lower() in {"1", "true", "yes", "on"}

    return bool(
        os.environ.get("ECS_CONTAINER_METADATA_URI_V4")
        or os.environ.get("AWS_EXECUTION_ENV")
    )
