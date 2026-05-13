from contextlib import contextmanager
from decimal import Decimal

from app.models.loan import Loan
from app.repositories.loan_repository import LoanStorageError


class PostgresLoanRepository:
    def __init__(self, database_url, connection_factory=None):
        self.database_url = database_url
        self._connection_factory = connection_factory

    def initialize(self):
        try:
            with self._connection() as connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS loans (
                        sequence BIGSERIAL PRIMARY KEY,
                        loan_id TEXT NOT NULL UNIQUE,
                        borrower_name TEXT NOT NULL,
                        funding_amount TEXT NOT NULL,
                        repayment_amount TEXT NOT NULL
                    )
                    """
                )
        except Exception as exc:
            raise LoanStorageError("Loan storage could not be initialized.") from exc

    def create(self, loan):
        try:
            with self._connection() as connection:
                connection.execute(
                    """
                    INSERT INTO loans (
                        loan_id,
                        borrower_name,
                        funding_amount,
                        repayment_amount
                    )
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        loan.loan_id,
                        loan.borrower_name,
                        str(loan.funding_amount),
                        str(loan.repayment_amount),
                    ),
                )
            return True
        except Exception as exc:
            if _is_integrity_error(exc):
                return False
            raise LoanStorageError("Loan storage could not create the loan.") from exc

    def get(self, loan_id):
        try:
            with self._connection() as connection:
                row = connection.execute(
                    """
                    SELECT loan_id, borrower_name, funding_amount, repayment_amount
                    FROM loans
                    WHERE loan_id = %s
                    """,
                    (loan_id,),
                ).fetchone()
        except Exception as exc:
            raise LoanStorageError("Loan storage could not look up the loan.") from exc

        if row is None:
            return None
        return self._row_to_loan(row)

    def delete(self, loan_id):
        try:
            with self._connection() as connection:
                row = connection.execute(
                    """
                    SELECT loan_id, borrower_name, funding_amount, repayment_amount
                    FROM loans
                    WHERE loan_id = %s
                    """,
                    (loan_id,),
                ).fetchone()
                if row is None:
                    return None
                connection.execute("DELETE FROM loans WHERE loan_id = %s", (loan_id,))
        except Exception as exc:
            raise LoanStorageError("Loan storage could not delete the loan.") from exc

        return self._row_to_loan(row)

    def list_all(self):
        try:
            with self._connection() as connection:
                rows = connection.execute(
                    """
                    SELECT loan_id, borrower_name, funding_amount, repayment_amount
                    FROM loans
                    ORDER BY sequence ASC
                    """
                ).fetchall()
        except Exception as exc:
            raise LoanStorageError("Loan storage could not list loans.") from exc

        return [self._row_to_loan(row) for row in rows]

    def list_by_borrower_name(self, borrower_name):
        try:
            with self._connection() as connection:
                rows = connection.execute(
                    """
                    SELECT loan_id, borrower_name, funding_amount, repayment_amount
                    FROM loans
                    WHERE borrower_name = %s
                    ORDER BY sequence ASC
                    """,
                    (borrower_name,),
                ).fetchall()
        except Exception as exc:
            raise LoanStorageError("Loan storage could not search loans.") from exc

        return [self._row_to_loan(row) for row in rows]

    def _connect(self):
        if self._connection_factory:
            return self._connection_factory(self.database_url)

        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError as exc:
            raise LoanStorageError("PostgreSQL support is not installed.") from exc

        return psycopg.connect(
            self.database_url,
            connect_timeout=5,
            row_factory=dict_row,
        )

    @contextmanager
    def _connection(self):
        connection = self._connect()
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    @staticmethod
    def _row_to_loan(row):
        return Loan(
            loan_id=row["loan_id"],
            borrower_name=row["borrower_name"],
            funding_amount=Decimal(row["funding_amount"]),
            repayment_amount=Decimal(row["repayment_amount"]),
        )


def _is_integrity_error(exc):
    names = {type(exc).__name__}
    names.update(base.__name__ for base in type(exc).__mro__)
    return bool(names & {"IntegrityError", "UniqueViolation"}) or any(
        name.endswith("IntegrityError") for name in names
    )
