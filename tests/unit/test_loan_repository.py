from decimal import Decimal

import pytest

from app.models.loan import Loan
from app.repositories.loan_repository import LoanStorageError, SQLiteLoanRepository


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


def repository(database_path):
    repo = SQLiteLoanRepository(database_path)
    repo.initialize()
    return repo


def test_initialize_creates_database_and_empty_schema(database_path):
    repo = repository(database_path)

    assert database_path.exists()
    assert repo.list_all() == []
    assert repo.list_by_borrower_name("Jane Smith") == []
    assert repo.get("LN-MISSING") is None
    assert repo.delete("LN-MISSING") is None


def test_create_get_list_and_search_persist_across_repository_instances(database_path):
    first_repo = repository(database_path)
    first = make_loan(loan_id="LN-001", borrower_name="Jane Smith")
    second = make_loan(
        loan_id="ln-001",
        borrower_name="Alex Doe",
        funding_amount="500.0",
        repayment_amount="650.0",
    )

    assert first_repo.create(first) is True
    assert first_repo.create(second) is True

    restarted_repo = repository(database_path)

    assert restarted_repo.get("LN-001") == first
    assert restarted_repo.list_all() == [first, second]
    assert restarted_repo.list_by_borrower_name("Jane Smith") == [first]
    assert restarted_repo.list_by_borrower_name("No Match") == []


def test_create_returns_false_for_duplicate_loan_id(database_path):
    repo = repository(database_path)

    assert repo.create(make_loan(loan_id="LN-001")) is True
    assert repo.create(make_loan(loan_id="LN-001")) is False
    assert repo.create(make_loan(loan_id="ln-001")) is True


def test_delete_removes_record_across_repository_instances(database_path):
    repo = repository(database_path)
    deleted = make_loan(loan_id="LN-DELETE")
    repo.create(deleted)
    repo.create(make_loan(loan_id="ln-delete", borrower_name="Alex Doe"))

    assert repo.delete("LN-DELETE") == deleted

    restarted_repo = repository(database_path)

    assert restarted_repo.get("LN-DELETE") is None
    assert [loan.loan_id for loan in restarted_repo.list_all()] == ["ln-delete"]


def test_initialize_raises_storage_error_when_parent_path_is_file(tmp_path):
    blocked_parent = tmp_path / "not-a-directory"
    blocked_parent.write_text("file blocks directory creation", encoding="utf-8")
    repo = SQLiteLoanRepository(blocked_parent / "loans.sqlite3")

    with pytest.raises(LoanStorageError):
        repo.initialize()
