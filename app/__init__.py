from flask import Flask

from app.auth import init_auth, load_auth_environment
from app.routes import api
from app.services.loan_service import LoanService


def create_app(test_config=None):
    load_auth_environment()
    app = Flask(__name__)
    app.config["LOAN_SERVICE"] = LoanService()

    if test_config:
        app.config.update(test_config)

    init_auth(app)
    app.register_blueprint(api)
    return app
