from flask import Flask

from app.routes import api
from app.services.loan_service import LoanService


def create_app(test_config=None):
    app = Flask(__name__)
    app.config["LOAN_SERVICE"] = LoanService()

    if test_config:
        app.config.update(test_config)

    app.register_blueprint(api)
    return app
