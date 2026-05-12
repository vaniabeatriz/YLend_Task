from flask import Blueprint, current_app, jsonify, render_template, request

from app.auth import (
    AuthError,
    current_auth_status,
    handle_callback,
    handle_logout,
    require_auth,
    start_login,
)
from app.services.loan_service import (
    DuplicateLoanError,
    LoanNotFoundError,
    LoanValidationError,
)

api = Blueprint("api", __name__)


@api.get("/")
def index():
    return render_template("index.html", auth_setup_error=None)


@api.get("/login")
def login():
    try:
        return start_login()
    except AuthError as exc:
        return render_template("index.html", auth_setup_error=exc.message), exc.status_code


@api.get("/callback")
def callback():
    try:
        return handle_callback()
    except AuthError as exc:
        return render_template("index.html", auth_setup_error=exc.message), exc.status_code


@api.get("/logout")
def logout():
    return handle_logout()


@api.get("/auth/status")
def auth_status():
    return jsonify(current_auth_status())


def error_response(error, message, status_code, details=None):
    payload = {
        "error": error,
        "message": message,
    }
    if details:
        payload["details"] = details

    response = jsonify(payload)
    response.status_code = status_code
    return response


@api.post("/loans")
@require_auth
def create_loan():
    if not request.is_json:
        return error_response(
            "validation_error",
            "Request body must be valid JSON.",
            400,
        )

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return error_response(
            "validation_error",
            "Request body must be valid JSON.",
            400,
        )

    try:
        loan = current_app.config["LOAN_SERVICE"].create_loan(payload)
    except LoanValidationError as exc:
        return error_response(
            "validation_error",
            str(exc),
            400,
            exc.details,
        )
    except DuplicateLoanError as exc:
        return error_response(
            "duplicate_loan_id",
            str(exc),
            409,
        )

    response = jsonify(loan)
    response.status_code = 201
    return response


@api.get("/loans")
@require_auth
def list_loans():
    loan_service = current_app.config["LOAN_SERVICE"]

    if "borrowerName" in request.args:
        try:
            loans = loan_service.list_loans_by_borrower_name(
                request.args.get("borrowerName")
            )
        except LoanValidationError as exc:
            return error_response(
                "validation_error",
                "borrowerName is required.",
                400,
                exc.details,
            )
    else:
        loans = loan_service.list_loans()

    return jsonify({"loans": loans})


@api.get("/loans/<path:loan_id>")
@require_auth
def get_loan(loan_id):
    try:
        loan = current_app.config["LOAN_SERVICE"].get_loan(loan_id)
    except LoanNotFoundError as exc:
        return error_response(
            "loan_not_found",
            str(exc),
            404,
        )

    return jsonify(loan)


@api.delete("/loans/<path:loan_id>")
@require_auth
def delete_loan(loan_id):
    try:
        loan = current_app.config["LOAN_SERVICE"].delete_loan(loan_id)
    except LoanNotFoundError as exc:
        return error_response(
            "loan_not_found",
            str(exc),
            404,
        )

    return jsonify(loan)


@api.get("/health")
def health():
    return jsonify({"status": "ok"})
