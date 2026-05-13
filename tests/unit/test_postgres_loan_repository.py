from decimal import Decimal

import pytest

from app.models.loan import Loan
from app.repositories.loan_repository import LoanStorageError
from app.repositories.postgres_loan_repository import PostgresLoanRepository


class FakeIntegrityError(Exception):
    pass


class FakeDatabaseError(Exception):
    pass


class FakeCursor:
    def __init__(self, row=None, rows=None):
        self._row = row
        self._rows = rows or []

    def fetchone(self):
        return self._row

    def fetchall(self):
        return self._rows


class FakePostgresConnection:
    def __init__(self, store, fail_on=None):
        self._store = store
        self._fail_on = fail_on
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def close(self):
        self.closed = True

    def execute(self, sql, params=None):
        normalized = " ".join(sql.split()).lower()
        if self._fail_on and self._fail_on in normalized:
            raise FakeDatabaseError("database failed")

        if normalized.startswith("create table"):
            self._store["initialized"] = True
            return FakeCursor()

        if normalized.startswith("insert into loans"):
            loan_id = params[0]
            if any(row["loan_id"] == loan_id for row in self._store["rows"]):
                raise FakeIntegrityError("duplicate loan id")
            self._store["sequence"] += 1
            self._store["rows"].append(
                {
                    "sequence": self._store["sequence"],
                    "loan_id": loan_id,
                    "borrower_name": params[1],
                    "funding_amount": params[2],
                    "repayment_amount": params[3],
                }
            )
            return FakeCursor()

        if normalized.startswith("select") and "where loan_id = %s" in normalized:
            row = next(
                (row for row in self._store["rows"] if row["loan_id"] == params[0]),
                None,
            )
            return FakeCursor(row=row)

        if normalized.startswith("select") and "where borrower_name = %s" in normalized:
            rows = [
                row
                for row in self._ordered_rows()
                if row["borrower_name"] == params[0]
            ]
            return FakeCursor(rows=rows)

        if normalized.startswith("select") and "order by sequence asc" in normalized:
            return FakeCursor(rows=self._ordered_rows())

        if normalized.startswith("delete from loans"):
            self._store["rows"] = [
                row for row in self._store["rows"] if row["loan_id"] != params[0]
            ]
            return FakeCursor()

        raise AssertionError(f"Unexpected SQL: {sql}")

    def _ordered_rows(self):
        return sorted(self._store["rows"], key=lambda row: row["sequence"])


class FakePostgresFactory:
    def __init__(self, fail_on=None):
        self.store = {"initialized": False, "sequence": 0, "rows": []}
        self.fail_on = fail_on

    def __call__(self, database_url):
        assert database_url == "postgresql://example/db"
        return FakePostgresConnection(self.store, fail_on=self.fail_on)


def make_loan(
    loan_id="LN-001",
    borrower_name="Jane Smith",
    funding_amount="1000.0",
    repayment_amount="1200.0",
):
    return Loan(
        loan_id=loan_id,
        borrower_name=borrower_name,
        funding_amount=Decimal(funding_amount),
        repayment_amount=Decimal(repayment_amount),
    )


def repository(factory):
    repo = PostgresLoanRepository("postgresql://example/db", factory)
    repo.initialize()
    return repo


def test_initialize_prepares_empty_schema():
    repo = repository(FakePostgresFactory())

    assert repo.list_all() == []
    assert repo.list_by_borrower_name("Jane Smith") == []
    assert repo.get("LN-MISSING") is None
    assert repo.delete("LN-MISSING") is None


def test_create_get_list_and_search_persist_across_connections():
    factory = FakePostgresFactory()
    first_repo = repository(factory)
    first = make_loan(loan_id="LN-001", borrower_name="Jane Smith")
    second = make_loan(
        loan_id="ln-001",
        borrower_name="Alex Doe",
        funding_amount="500.0",
        repayment_amount="650.0",
    )

    assert first_repo.create(first) is True
    assert first_repo.create(second) is True

    restarted_repo = repository(factory)

    assert restarted_repo.get("LN-001") == first
    assert restarted_repo.list_all() == [first, second]
    assert restarted_repo.list_by_borrower_name("Jane Smith") == [first]
    assert restarted_repo.list_by_borrower_name("No Match") == []


def test_create_returns_false_for_duplicate_loan_id():
    repo = repository(FakePostgresFactory())

    assert repo.create(make_loan(loan_id="LN-001")) is True
    assert repo.create(make_loan(loan_id="LN-001")) is False
    assert repo.create(make_loan(loan_id="ln-001")) is True


def test_delete_removes_record_across_connections():
    factory = FakePostgresFactory()
    repo = repository(factory)
    deleted = make_loan(loan_id="LN-DELETE")
    repo.create(deleted)
    repo.create(make_loan(loan_id="ln-delete", borrower_name="Alex Doe"))

    assert repo.delete("LN-DELETE") == deleted

    restarted_repo = repository(factory)

    assert restarted_repo.get("LN-DELETE") is None
    assert [loan.loan_id for loan in restarted_repo.list_all()] == ["ln-delete"]


def test_database_errors_are_mapped_to_storage_error():
    repo = repository(FakePostgresFactory(fail_on="order by sequence asc"))

    with pytest.raises(LoanStorageError, match="list loans"):
        repo.list_all()
