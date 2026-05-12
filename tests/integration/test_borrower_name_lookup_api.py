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


def seed_borrower_lookup_loans(client):
    first = client.post("/loans", json=valid_payload(loanId="LN-001"))
    different_borrower = client.post(
        "/loans",
        json=valid_payload(
            loanId="LN-002",
            borrowerName="Alex Doe",
            fundingAmount=500.0,
            repaymentAmount=650.0,
        ),
    )
    second = client.post(
        "/loans",
        json=valid_payload(
            loanId="LN-003",
            borrowerName="Jane Smith",
            fundingAmount=700.0,
            repaymentAmount=850.0,
        ),
    )
    case_mismatch = client.post(
        "/loans",
        json=valid_payload(
            loanId="LN-004",
            borrowerName="jane smith",
            fundingAmount=300.0,
            repaymentAmount=360.0,
        ),
    )

    assert first.status_code == 201
    assert different_borrower.status_code == 201
    assert second.status_code == 201
    assert case_mismatch.status_code == 201


def test_get_loans_by_borrower_name_returns_matching_current_loans(client):
    seed_borrower_lookup_loans(client)

    started_at = perf_counter()
    response = client.get("/loans?borrowerName=%20%20Jane%20Smith%20%20")
    elapsed = perf_counter() - started_at

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
                "loanId": "LN-003",
                "borrowerName": "Jane Smith",
                "fundingAmount": 700.0,
                "repaymentAmount": 850.0,
            },
        ]
    }


def test_get_loans_without_borrower_name_still_lists_all_and_id_lookup_still_returns_one(
    client,
):
    seed_borrower_lookup_loans(client)

    listed = client.get("/loans")
    found = client.get("/loans/LN-002")

    assert listed.status_code == 200
    assert [loan["loanId"] for loan in listed.get_json()["loans"]] == [
        "LN-001",
        "LN-002",
        "LN-003",
        "LN-004",
    ]
    assert found.status_code == 200
    assert found.get_json() == {
        "loanId": "LN-002",
        "borrowerName": "Alex Doe",
        "fundingAmount": 500.0,
        "repaymentAmount": 650.0,
    }


def test_get_loans_by_unknown_borrower_name_returns_empty_collection(client):
    seed_borrower_lookup_loans(client)

    started_at = perf_counter()
    response = client.get("/loans?borrowerName=No%20Match")
    elapsed = perf_counter() - started_at

    assert response.status_code == 200
    assert elapsed < 2
    assert response.get_json() == {"loans": []}


def test_get_loans_by_borrower_name_returns_persisted_matches_after_new_app_session(
    tmp_path,
):
    config = {"TESTING": True, "LOAN_DATABASE_PATH": str(tmp_path / "loans.sqlite3")}
    first_client = create_app(config).test_client()

    created = first_client.post("/loans", json=valid_payload(loanId="LN-RESTART"))
    listed_before_restart = first_client.get("/loans?borrowerName=Jane%20Smith")

    restarted_client = create_app(config).test_client()
    started_at = perf_counter()
    listed_after_restart = restarted_client.get("/loans?borrowerName=Jane%20Smith")
    elapsed = perf_counter() - started_at

    assert created.status_code == 201
    assert listed_before_restart.status_code == 200
    assert listed_before_restart.get_json()["loans"][0]["loanId"] == "LN-RESTART"
    assert listed_after_restart.status_code == 200
    assert elapsed < 2
    assert listed_after_restart.get_json()["loans"][0]["loanId"] == "LN-RESTART"


def test_get_loans_by_empty_borrower_name_returns_validation_error(client):
    started_at = perf_counter()
    response = client.get("/loans?borrowerName=")
    elapsed = perf_counter() - started_at

    assert response.status_code == 400
    assert elapsed < 2
    assert response.get_json() == {
        "error": "validation_error",
        "message": "borrowerName is required.",
        "details": [
            {"field": "borrowerName", "message": "borrowerName is required."}
        ],
    }


def test_get_loans_by_whitespace_only_borrower_name_returns_validation_error(client):
    started_at = perf_counter()
    response = client.get("/loans?borrowerName=%20%20%20")
    elapsed = perf_counter() - started_at

    assert response.status_code == 400
    assert elapsed < 2
    assert response.get_json() == {
        "error": "validation_error",
        "message": "borrowerName is required.",
        "details": [
            {"field": "borrowerName", "message": "borrowerName is required."}
        ],
    }
