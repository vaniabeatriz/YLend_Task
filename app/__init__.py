from flask import Flask

from app.auth import init_auth, load_auth_environment
from app.repositories.loan_repository import LoanStorageError
from app.repositories.repository_factory import (
    UnavailableLoanRepository,
    create_loan_repository,
)
from app.routes import api
from app.services.loan_service import LoanService


def create_app(test_config=None):
    load_auth_environment()
    app = Flask(__name__)

    if test_config:
        app.config.update(test_config)

    repository = app.config.get("LOAN_REPOSITORY")
    storage_setup_error = None
    app.config["INSTANCE_PATH"] = app.instance_path

    try:
        if repository is None:
            repository = create_loan_repository(app.config)
        if hasattr(repository, "initialize"):
            repository.initialize()
    except LoanStorageError as exc:
        storage_setup_error = str(exc)
        if repository is None:
            repository = UnavailableLoanRepository()

    app.config["LOAN_SERVICE"] = LoanService(
        repository,
        storage_setup_error=storage_setup_error,
    )
    init_auth(app)
    app.register_blueprint(api)
    return app
