import sqlite3
from contextlib import contextmanager
from decimal import Decimal
from pathlib import Path

from app.models.loan import Loan


class LoanStorageError(Exception):
    """Raised when durable loan storage cannot be prepared or accessed."""


class SQLiteLoanRepository:
    def __init__(self, database_path):
        self.database_path = str(database_path)

    def initialize(self):
        try:
            self._ensure_parent_directory()
            with self._connection() as connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS loans (
                        sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                        loan_id TEXT NOT NULL UNIQUE,
                        borrower_name TEXT NOT NULL,
                        funding_amount TEXT NOT NULL,
                        repayment_amount TEXT NOT NULL
                    )
                    """
                )
        except (OSError, sqlite3.Error) as exc:
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
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        loan.loan_id,
                        loan.borrower_name,
                        str(loan.funding_amount),
                        str(loan.repayment_amount),
                    ),
                )
            return True
        except sqlite3.IntegrityError:
            return False
        except sqlite3.Error as exc:
            raise LoanStorageError("Loan storage could not create the loan.") from exc

    def get(self, loan_id):
        try:
            with self._connection() as connection:
                row = connection.execute(
                    """
                    SELECT loan_id, borrower_name, funding_amount, repayment_amount
                    FROM loans
                    WHERE loan_id = ?
                    """,
                    (loan_id,),
                ).fetchone()
        except sqlite3.Error as exc:
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
                    WHERE loan_id = ?
                    """,
                    (loan_id,),
                ).fetchone()
                if row is None:
                    return None
                connection.execute("DELETE FROM loans WHERE loan_id = ?", (loan_id,))
        except sqlite3.Error as exc:
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
        except sqlite3.Error as exc:
            raise LoanStorageError("Loan storage could not list loans.") from exc

        return [self._row_to_loan(row) for row in rows]

    def list_by_borrower_name(self, borrower_name):
        try:
            with self._connection() as connection:
                rows = connection.execute(
                    """
                    SELECT loan_id, borrower_name, funding_amount, repayment_amount
                    FROM loans
                    WHERE borrower_name = ?
                    ORDER BY sequence ASC
                    """,
                    (borrower_name,),
                ).fetchall()
        except sqlite3.Error as exc:
            raise LoanStorageError("Loan storage could not search loans.") from exc

        return [self._row_to_loan(row) for row in rows]

    def _ensure_parent_directory(self):
        if self.database_path == ":memory:":
            return
        Path(self.database_path).expanduser().parent.mkdir(parents=True, exist_ok=True)

    def _connect(self):
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

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
