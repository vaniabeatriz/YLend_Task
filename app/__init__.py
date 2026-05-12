import os
from pathlib import Path

from flask import Flask

from app.auth import init_auth, load_auth_environment
from app.repositories.loan_repository import LoanStorageError, SQLiteLoanRepository
from app.routes import api
from app.services.loan_service import LoanService


def create_app(test_config=None):
    load_auth_environment()
    app = Flask(__name__)

    if test_config:
        app.config.update(test_config)

    repository = app.config.get("LOAN_REPOSITORY")
    storage_setup_error = None
    if repository is None:
        database_path = app.config.get("LOAN_DATABASE_PATH") or os.environ.get(
            "LOAN_DATABASE_PATH"
        )
        if not database_path:
            database_path = str(Path(app.instance_path) / "loans.sqlite3")
        app.config["LOAN_DATABASE_PATH"] = database_path
        repository = SQLiteLoanRepository(database_path)

    try:
        if hasattr(repository, "initialize"):
            repository.initialize()
    except LoanStorageError as exc:
        storage_setup_error = str(exc)

    app.config["LOAN_SERVICE"] = LoanService(
        repository,
        storage_setup_error=storage_setup_error,
    )
    init_auth(app)
    app.register_blueprint(api)
    return app
