import pytest

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


def test_create_loan_trims_text_and_returns_stored_record():
    service = LoanService()

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
def test_create_loan_rejects_missing_or_blank_text_fields(field, value):
    service = LoanService()

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
def test_create_loan_rejects_invalid_amounts(field, value):
    service = LoanService()

    with pytest.raises(LoanValidationError) as error:
        service.create_loan(valid_payload(**{field: value}))

    assert error.value.details == [
        {"field": field, "message": f"{field} must be greater than 0."}
    ]


def test_create_loan_rejects_extra_fields():
    service = LoanService()

    with pytest.raises(LoanValidationError) as error:
        service.create_loan(valid_payload(extraField="not allowed"))

    assert error.value.details == [
        {"field": "extraField", "message": "extraField is not allowed."}
    ]


def test_create_loan_rejects_duplicate_trimmed_case_sensitive_loan_id():
    service = LoanService()
    service.create_loan(valid_payload(loanId="LN-001"))

    with pytest.raises(DuplicateLoanError) as error:
        service.create_loan(valid_payload(loanId="  LN-001  "))

    assert str(error.value) == "A loan with this loan ID already exists."


def test_create_loan_allows_ids_that_differ_only_by_case():
    service = LoanService()
    first = service.create_loan(valid_payload(loanId="LN-001"))
    second = service.create_loan(valid_payload(loanId="ln-001"))

    assert first["loanId"] == "LN-001"
    assert second["loanId"] == "ln-001"


def test_get_loan_returns_existing_record_after_trimming_loan_id():
    service = LoanService()
    created = service.create_loan(valid_payload(loanId="LN-LOOKUP"))

    found = service.get_loan("  LN-LOOKUP  ")

    assert found == created


@pytest.mark.parametrize("loan_id", ["LN-MISSING", "ln-001", "", "   "])
def test_get_loan_rejects_missing_blank_or_case_mismatched_loan_id(loan_id):
    service = LoanService()
    service.create_loan(valid_payload(loanId="LN-001"))

    with pytest.raises(LoanNotFoundError) as error:
        service.get_loan(loan_id)

    assert str(error.value) == "No loan exists for this loan ID."
