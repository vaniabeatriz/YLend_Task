import pytest

from app.repositories.loan_repository import SQLiteLoanRepository
from app.services.loan_service import (
    DuplicateLoanError,
    LoanNotFoundError,
    LoanService,
    LoanValidationError,
)


def valid_payload(**overrides):
    payload = {
        "loanId": "LN-001",
        "borrowerName": "Jane Smith",
        "fundingAmount": 1000.0,
        "repaymentAmount": 1200.0,
    }
    payload.update(overrides)
    return payload


@pytest.fixture
def service(tmp_path):
    repository = SQLiteLoanRepository(tmp_path / "loans.sqlite3")
    repository.initialize()
    return LoanService(repository)


def test_create_loan_trims_text_and_returns_stored_record(service):

    loan = service.create_loan(
        valid_payload(
            loanId="  LN-001  ",
            borrowerName="  Jane Smith  ",
            fundingAmount=1000.50,
            repaymentAmount=1200.75,
        )
    )

    assert loan == {
        "loanId": "LN-001",
        "borrowerName": "Jane Smith",
        "fundingAmount": 1000.50,
        "repaymentAmount": 1200.75,
    }


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("loanId", ""),
        ("loanId", "   "),
        ("borrowerName", ""),
        ("borrowerName", "   "),
    ],
)
def test_create_loan_rejects_missing_or_blank_text_fields(service, field, value):

    with pytest.raises(LoanValidationError) as error:
        service.create_loan(valid_payload(**{field: value}))

    assert error.value.details == [
        {"field": field, "message": f"{field} is required."}
    ]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("fundingAmount", 0),
        ("fundingAmount", -1),
        ("fundingAmount", float("nan")),
        ("fundingAmount", float("inf")),
        ("fundingAmount", "not-a-number"),
        ("repaymentAmount", 0),
        ("repaymentAmount", -1),
        ("repaymentAmount", float("nan")),
        ("repaymentAmount", float("inf")),
        ("repaymentAmount", "not-a-number"),
    ],
)
def test_create_loan_rejects_invalid_amounts(service, field, value):

    with pytest.raises(LoanValidationError) as error:
        service.create_loan(valid_payload(**{field: value}))

    assert error.value.details == [
        {"field": field, "message": f"{field} must be greater than 0."}
    ]


def test_create_loan_rejects_extra_fields(service):

    with pytest.raises(LoanValidationError) as error:
        service.create_loan(valid_payload(extraField="not allowed"))

    assert error.value.details == [
        {"field": "extraField", "message": "extraField is not allowed."}
    ]


def test_create_loan_rejects_duplicate_trimmed_case_sensitive_loan_id(service):
    service.create_loan(valid_payload(loanId="LN-001"))

    with pytest.raises(DuplicateLoanError) as error:
        service.create_loan(valid_payload(loanId="  LN-001  "))

    assert str(error.value) == "A loan with this loan ID already exists."


def test_create_loan_allows_ids_that_differ_only_by_case(service):
    first = service.create_loan(valid_payload(loanId="LN-001"))
    second = service.create_loan(valid_payload(loanId="ln-001"))

    assert first["loanId"] == "LN-001"
    assert second["loanId"] == "ln-001"


def test_get_loan_returns_existing_record_after_trimming_loan_id(service):
    created = service.create_loan(valid_payload(loanId="LN-LOOKUP"))

    found = service.get_loan("  LN-LOOKUP  ")

    assert found == created


@pytest.mark.parametrize("loan_id", ["LN-MISSING", "ln-001", "", "   "])
def test_get_loan_rejects_missing_blank_or_case_mismatched_loan_id(service, loan_id):
    service.create_loan(valid_payload(loanId="LN-001"))

    with pytest.raises(LoanNotFoundError) as error:
        service.get_loan(loan_id)

    assert str(error.value) == "No loan exists for this loan ID."


def test_delete_loan_returns_deleted_record_and_removes_only_trimmed_case_sensitive_match(
    service,
):
    deleted = service.create_loan(valid_payload(loanId="LN-DELETE"))
    case_different = service.create_loan(
        valid_payload(
            loanId="ln-delete",
            borrowerName="Alex Doe",
            fundingAmount=500.0,
            repaymentAmount=650.0,
        )
    )

    result = service.delete_loan("  LN-DELETE  ")

    assert result == deleted
    assert service.list_loans() == [case_different]
    assert service.get_loan("ln-delete") == case_different
    with pytest.raises(LoanNotFoundError):
        service.get_loan("LN-DELETE")


@pytest.mark.parametrize("loan_id", ["LN-MISSING", "ln-delete", "", "   "])
def test_delete_loan_rejects_missing_blank_or_case_mismatched_loan_id(
    service,
    loan_id,
):
    current = service.create_loan(valid_payload(loanId="LN-DELETE"))

    with pytest.raises(LoanNotFoundError) as error:
        service.delete_loan(loan_id)

    assert str(error.value) == "No loan exists for this loan ID."
    assert service.list_loans() == [current]


def test_delete_loan_rejects_already_deleted_loan_id(service):
    service.create_loan(valid_payload(loanId="LN-DELETE"))
    service.delete_loan("LN-DELETE")

    with pytest.raises(LoanNotFoundError) as error:
        service.delete_loan("LN-DELETE")

    assert str(error.value) == "No loan exists for this loan ID."
    assert service.list_loans() == []


def test_list_loans_returns_all_current_loans_with_trimmed_values_and_case_sensitive_ids(
    service,
):
    first = service.create_loan(
        valid_payload(loanId="  LN-001  ", borrowerName="  Jane Smith  ")
    )
    second = service.create_loan(
        valid_payload(
            loanId="ln-001",
            borrowerName="  Alex Doe  ",
            fundingAmount=500.0,
            repaymentAmount=650.0,
        )
    )

    assert service.list_loans() == [first, second]


def test_list_loans_returns_empty_list_for_new_service(service):

    assert service.list_loans() == []


def test_list_loans_by_borrower_name_returns_matching_loans_with_trimmed_search_and_case_sensitive_matching(
    service,
):
    first = service.create_loan(valid_payload(loanId="LN-001"))
    service.create_loan(
        valid_payload(
            loanId="LN-002",
            borrowerName="Alex Doe",
            fundingAmount=500.0,
            repaymentAmount=650.0,
        )
    )
    second = service.create_loan(
        valid_payload(
            loanId="LN-003",
            borrowerName="Jane Smith",
            fundingAmount=700.0,
            repaymentAmount=850.0,
        )
    )
    service.create_loan(
        valid_payload(
            loanId="LN-004",
            borrowerName="jane smith",
            fundingAmount=300.0,
            repaymentAmount=360.0,
        )
    )

    assert service.list_loans_by_borrower_name("  Jane Smith  ") == [first, second]


def test_list_loans_by_borrower_name_returns_empty_list_when_no_matches(service):
    service.create_loan(valid_payload(loanId="LN-001"))

    assert service.list_loans_by_borrower_name("No Match") == []


@pytest.mark.parametrize("borrower_name", ["", "   "])
def test_list_loans_by_borrower_name_rejects_blank_search_terms(
    service,
    borrower_name,
):

    with pytest.raises(LoanValidationError) as error:
        service.list_loans_by_borrower_name(borrower_name)

    assert error.value.details == [
        {"field": "borrowerName", "message": "borrowerName is required."}
    ]
