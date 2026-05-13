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


def test_get_loan_returns_stored_record(client):
    created = client.post("/loans", json=valid_payload(loanId="LN-LOOKUP"))
    started = perf_counter()
    response = client.get("/loans/LN-LOOKUP")
    elapsed = perf_counter() - started

    assert created.status_code == 201
    assert response.status_code == 200
    assert elapsed < 2
    assert response.get_json() == {
        "loanId": "LN-LOOKUP",
        "borrowerName": "Jane Smith",
        "fundingAmount": 1000.0,
        "repaymentAmount": 1200.0,
    }


def test_get_loan_trims_loan_id_and_keeps_case_sensitive_lookup(client):
    created = client.post("/loans", json=valid_payload(loanId="LN-LOOKUP"))
    trimmed_match = client.get("/loans/%20LN-LOOKUP%20")
    case_mismatch = client.get("/loans/ln-lookup")

    assert created.status_code == 201
    assert trimmed_match.status_code == 200
    assert trimmed_match.get_json()["loanId"] == "LN-LOOKUP"
    assert case_mismatch.status_code == 404
    assert case_mismatch.get_json() == {
        "error": "loan_not_found",
        "message": "No loan exists for this loan ID.",
    }


def test_get_loan_returns_not_found_for_unknown_loan_id(client):
    started = perf_counter()
    response = client.get("/loans/LN-MISSING")
    elapsed = perf_counter() - started

    assert response.status_code == 404
    assert elapsed < 2
    assert response.get_json() == {
        "error": "loan_not_found",
        "message": "No loan exists for this loan ID.",
    }


def test_get_loan_returns_persisted_record_after_new_app_session(tmp_path):
    config = {"TESTING": True, "LOAN_DATABASE_PATH": str(tmp_path / "loans.sqlite3")}
    first_client = create_app(config).test_client()

    created = first_client.post("/loans", json=valid_payload(loanId="LN-RESTART"))
    found_before_restart = first_client.get("/loans/LN-RESTART")
    restarted_client = create_app(config).test_client()
    found_after_restart = restarted_client.get("/loans/LN-RESTART")

    assert created.status_code == 201
    assert found_before_restart.status_code == 200
    assert found_after_restart.status_code == 200
    assert found_after_restart.get_json()["loanId"] == "LN-RESTART"
