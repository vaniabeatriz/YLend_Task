from time import perf_counter

from app import create_app


def valid_payload(**overrides):
    payload = {
        "loanId": "LN-001",
        "borrowerName": "Jane Smith",
        "fundingAmount": 1000.0,
        "repaymentAmount": 1200.0,
    }
    payload.update(overrides)
    return payload


def test_post_loans_creates_loan_and_returns_stored_record(client):
    response = client.post(
        "/loans",
        json=valid_payload(loanId="  LN-001  ", borrowerName="  Jane Smith  "),
    )

    assert response.status_code == 201
    assert response.get_json() == {
        "loanId": "LN-001",
        "borrowerName": "Jane Smith",
        "fundingAmount": 1000.0,
        "repaymentAmount": 1200.0,
    }


def test_post_loans_rejects_invalid_payload(client):
    started = perf_counter()
    response = client.post("/loans", json=valid_payload(fundingAmount=0))
    elapsed = perf_counter() - started

    assert response.status_code == 400
    assert elapsed < 2
    assert response.get_json() == {
        "error": "validation_error",
        "message": "Loan could not be created because one or more fields are invalid.",
        "details": [
            {"field": "fundingAmount", "message": "fundingAmount must be greater than 0."}
        ],
    }


def test_post_loans_rejects_duplicate_loan_id(client):
    first = client.post("/loans", json=valid_payload(loanId="LN-001"))
    started = perf_counter()
    duplicate = client.post("/loans", json=valid_payload(loanId="  LN-001  "))
    elapsed = perf_counter() - started

    assert first.status_code == 201
    assert duplicate.status_code == 409
    assert elapsed < 2
    assert duplicate.get_json() == {
        "error": "duplicate_loan_id",
        "message": "A loan with this loan ID already exists.",
    }


def test_post_loans_rejects_non_json_request(client):
    response = client.post("/loans", data="not-json", content_type="text/plain")

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "validation_error",
        "message": "Request body must be valid JSON.",
    }


def test_post_loans_rejects_extra_fields(client):
    response = client.post("/loans", json=valid_payload(extraField="not allowed"))

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "validation_error",
        "message": "Loan could not be created because one or more fields are invalid.",
        "details": [
            {"field": "extraField", "message": "extraField is not allowed."}
        ],
    }


def test_durable_store_rejects_duplicate_after_new_app_session(tmp_path):
    config = {"TESTING": True, "LOAN_DATABASE_PATH": str(tmp_path / "loans.sqlite3")}
    first_client = create_app(config).test_client()

    created = first_client.post("/loans", json=valid_payload(loanId="LN-RESTART"))
    duplicate_before_restart = first_client.post(
        "/loans", json=valid_payload(loanId="LN-RESTART")
    )
    restarted_client = create_app(config).test_client()
    created_after_restart = restarted_client.post(
        "/loans", json=valid_payload(loanId="LN-RESTART")
    )

    assert created.status_code == 201
    assert duplicate_before_restart.status_code == 409
    assert created_after_restart.status_code == 409
