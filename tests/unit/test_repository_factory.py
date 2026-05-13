import pytest

from app.repositories.loan_repository import LoanStorageError, SQLiteLoanRepository
from app.repositories.postgres_loan_repository import PostgresLoanRepository
from app.repositories.repository_factory import create_loan_repository


def base_config(tmp_path, **overrides):
    config = {"INSTANCE_PATH": str(tmp_path)}
    config.update(overrides)
    return config


def clear_storage_env(monkeypatch):
    for name in (
        "DATABASE_URL",
        "LOAN_DATABASE_URL",
        "LOAN_DATABASE_PATH",
        "LOAN_REQUIRE_DATABASE_URL",
        "AWS_EXECUTION_ENV",
        "ECS_CONTAINER_METADATA_URI_V4",
    ):
        monkeypatch.delenv(name, raising=False)


def test_factory_uses_sqlite_path_for_local_runtime(tmp_path, monkeypatch):
    clear_storage_env(monkeypatch)
    config = base_config(tmp_path)

    repository = create_loan_repository(config)

    assert isinstance(repository, SQLiteLoanRepository)
    assert repository.database_path == str(tmp_path / "loans.sqlite3")
    assert config["LOAN_DATABASE_PATH"] == str(tmp_path / "loans.sqlite3")


def test_factory_uses_configured_postgres_url(tmp_path, monkeypatch):
    clear_storage_env(monkeypatch)
    config = base_config(tmp_path, LOAN_DATABASE_URL="postgresql://example/db")

    repository = create_loan_repository(config)

    assert isinstance(repository, PostgresLoanRepository)
    assert repository.database_url == "postgresql://example/db"


def test_factory_uses_database_url_environment(tmp_path, monkeypatch):
    clear_storage_env(monkeypatch)
    monkeypatch.setenv("DATABASE_URL", "postgresql://env/db")
    config = base_config(tmp_path)

    repository = create_loan_repository(config)

    assert isinstance(repository, PostgresLoanRepository)
    assert repository.database_url == "postgresql://env/db"
    assert config["LOAN_DATABASE_URL"] == "postgresql://env/db"


def test_factory_fails_closed_when_deployed_runtime_lacks_database_url(
    tmp_path,
    monkeypatch,
):
    clear_storage_env(monkeypatch)
    monkeypatch.setenv("AWS_EXECUTION_ENV", "AWS_ECS_FARGATE")

    with pytest.raises(LoanStorageError, match="RDS database URL"):
        create_loan_repository(base_config(tmp_path))


def test_factory_fails_closed_when_database_url_is_required(tmp_path, monkeypatch):
    clear_storage_env(monkeypatch)

    with pytest.raises(LoanStorageError, match="RDS database URL"):
        create_loan_repository(base_config(tmp_path, LOAN_REQUIRE_DATABASE_URL=True))
