from decimal import Decimal, InvalidOperation

from app.models.loan import Loan
from app.repositories.loan_repository import LoanStorageError

ALLOWED_FIELDS = {"loanId", "borrowerName", "fundingAmount", "repaymentAmount"}


class LoanValidationError(Exception):
    def __init__(self, details):
        super().__init__("Loan could not be created because one or more fields are invalid.")
        self.details = details


class DuplicateLoanError(Exception):
    """Raised when a loan ID already exists in the current durable store."""


class LoanNotFoundError(Exception):
    """Raised when a loan ID is absent from the current durable store."""


class LoanService:
    def __init__(self, repository, storage_setup_error=None):
        self._repository = repository
        self._storage_setup_error = storage_setup_error

    def create_loan(self, payload):
        if not isinstance(payload, dict):
            raise LoanValidationError([])

        details = []
        for field in sorted(set(payload) - ALLOWED_FIELDS):
            details.append({"field": field, "message": f"{field} is not allowed."})

        loan_id = self._clean_required_text(payload.get("loanId"), "loanId", details)
        borrower_name = self._clean_required_text(
            payload.get("borrowerName"), "borrowerName", details
        )
        funding_amount = self._parse_positive_decimal(
            payload.get("fundingAmount"), "fundingAmount", details
        )
        repayment_amount = self._parse_positive_decimal(
            payload.get("repaymentAmount"), "repaymentAmount", details
        )

        if details:
            raise LoanValidationError(details)

        loan = Loan(
            loan_id=loan_id,
            borrower_name=borrower_name,
            funding_amount=funding_amount,
            repayment_amount=repayment_amount,
        )
        self._ensure_storage_ready()
        if not self._repository.create(loan):
            raise DuplicateLoanError("A loan with this loan ID already exists.")
        return loan.to_dict()

    def get_loan(self, loan_id):
        if not isinstance(loan_id, str):
            raise LoanNotFoundError("No loan exists for this loan ID.")

        normalized_loan_id = loan_id.strip()
        if not normalized_loan_id:
            raise LoanNotFoundError("No loan exists for this loan ID.")

        self._ensure_storage_ready()
        loan = self._repository.get(normalized_loan_id)
        if loan is None:
            raise LoanNotFoundError("No loan exists for this loan ID.")

        return loan.to_dict()

    def delete_loan(self, loan_id):
        if not isinstance(loan_id, str):
            raise LoanNotFoundError("No loan exists for this loan ID.")

        normalized_loan_id = loan_id.strip()
        if not normalized_loan_id:
            raise LoanNotFoundError("No loan exists for this loan ID.")

        self._ensure_storage_ready()
        loan = self._repository.delete(normalized_loan_id)
        if loan is None:
            raise LoanNotFoundError("No loan exists for this loan ID.")

        return loan.to_dict()

    def list_loans(self):
        self._ensure_storage_ready()
        return [loan.to_dict() for loan in self._repository.list_all()]

    def list_loans_by_borrower_name(self, borrower_name):
        details = []
        normalized_borrower_name = self._clean_required_text(
            borrower_name, "borrowerName", details
        )

        if details:
            raise LoanValidationError(details)

        self._ensure_storage_ready()
        return [
            loan.to_dict()
            for loan in self._repository.list_by_borrower_name(normalized_borrower_name)
        ]

    def _ensure_storage_ready(self):
        if self._storage_setup_error:
            raise LoanStorageError(self._storage_setup_error)

    @staticmethod
    def _clean_required_text(value, field, details):
        if not isinstance(value, str):
            details.append({"field": field, "message": f"{field} is required."})
            return None

        cleaned = value.strip()
        if not cleaned:
            details.append({"field": field, "message": f"{field} is required."})
            return None

        return cleaned

    @staticmethod
    def _parse_positive_decimal(value, field, details):
        if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
            details.append({"field": field, "message": f"{field} must be greater than 0."})
            return None

        try:
            amount = Decimal(str(value))
        except (InvalidOperation, ValueError):
            details.append({"field": field, "message": f"{field} must be greater than 0."})
            return None

        if not amount.is_finite() or amount <= 0:
            details.append({"field": field, "message": f"{field} must be greater than 0."})
            return None

        return amount
