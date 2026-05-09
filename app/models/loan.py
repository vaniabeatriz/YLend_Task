from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Loan:
    loan_id: str
    borrower_name: str
    funding_amount: Decimal
    repayment_amount: Decimal

    def to_dict(self):
        return {
            "loanId": self.loan_id,
            "borrowerName": self.borrower_name,
            "fundingAmount": float(self.funding_amount),
            "repaymentAmount": float(self.repayment_amount),
        }
