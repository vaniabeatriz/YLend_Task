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


def test_get_loans_returns_all_current_loans_after_multiple_creates(client):
    first = client.post(
        "/loans",
        json=valid_payload(loanId="  LN-001  ", borrowerName="  Jane Smith  "),
    )
    second = client.post(
        "/loans",
        json=valid_payload(
            loanId="ln-001",
            borrowerName="  Alex Doe  ",
            fundingAmount=500.0,
            repaymentAmount=650.0,
        ),
    )

    started_at = perf_counter()
    response = client.get("/loans")
    elapsed = perf_counter() - started_at

    assert first.status_code == 201
    assert second.status_code == 201
    assert response.status_code == 200
    assert elapsed < 2
    assert response.get_json() == {
        "loans": [
            {
                "loanId": "LN-001",
                "borrowerName": "Jane Smith",
                "fundingAmount": 1000.0,
                "repaymentAmount": 1200.0,
            },
            {
                "loanId": "ln-001",
                "borrowerName": "Alex Doe",
                "fundingAmount": 500.0,
                "repaymentAmount": 650.0,
            },
        ]
    }


def test_get_loans_excludes_rejected_validation_and_duplicate_create_attempts(client):
    created = client.post("/loans", json=valid_payload(loanId="LN-VALID"))
    invalid = client.post(
        "/loans",
        json=valid_payload(loanId="LN-INVALID", fundingAmount=0),
    )
    duplicate = client.post(
        "/loans",
        json=valid_payload(loanId="LN-VALID", borrowerName="Different Borrower"),
    )

    started_at = perf_counter()
    response = client.get("/loans")
    elapsed = perf_counter() - started_at

    assert created.status_code == 201
    assert invalid.status_code == 400
    assert duplicate.status_code == 409
    assert response.status_code == 200
    assert elapsed < 2
    assert response.get_json() == {
        "loans": [
            {
                "loanId": "LN-VALID",
                "borrowerName": "Jane Smith",
                "fundingAmount": 1000.0,
                "repaymentAmount": 1200.0,
            }
        ]
    }


def test_get_loans_returns_empty_collection_for_fresh_session(client):
    started_at = perf_counter()
    response = client.get("/loans")
    elapsed = perf_counter() - started_at

    assert response.status_code == 200
    assert elapsed < 2
    assert response.get_json() == {"loans": []}


def test_get_loans_returns_persisted_collection_after_new_app_session(tmp_path):
    config = {"TESTING": True, "LOAN_DATABASE_PATH": str(tmp_path / "loans.sqlite3")}
    first_client = create_app(config).test_client()

    created = first_client.post("/loans", json=valid_payload(loanId="LN-RESTART"))
    listed_before_restart = first_client.get("/loans")

    restarted_client = create_app(config).test_client()
    started_at = perf_counter()
    listed_after_restart = restarted_client.get("/loans")
    elapsed = perf_counter() - started_at

    assert created.status_code == 201
    assert listed_before_restart.status_code == 200
    assert listed_before_restart.get_json()["loans"][0]["loanId"] == "LN-RESTART"
    assert listed_after_restart.status_code == 200
    assert elapsed < 2
    assert listed_after_restart.get_json()["loans"][0]["loanId"] == "LN-RESTART"
