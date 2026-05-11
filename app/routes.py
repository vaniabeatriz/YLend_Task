from flask import Blueprint, current_app, jsonify, request

from app.services.loan_service import (
    DuplicateLoanError,
    LoanNotFoundError,
    LoanValidationError,
)

api = Blueprint("api", __name__)


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


@api.get("/health")
def health():
    return jsonify({"status": "ok"})
