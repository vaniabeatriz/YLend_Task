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


def test_delete_loan_returns_deleted_record_and_trims_encoded_loan_id(client):
    created = client.post("/loans", json=valid_payload(loanId="LN-DELETE"))

    started_at = perf_counter()
    response = client.delete("/loans/%20LN-DELETE%20")
    elapsed = perf_counter() - started_at

    assert created.status_code == 201
    assert response.status_code == 200
    assert elapsed < 2
    assert response.get_json() == {
        "loanId": "LN-DELETE",
        "borrowerName": "Jane Smith",
        "fundingAmount": 1000.0,
        "repaymentAmount": 1200.0,
    }


def test_deleted_loan_is_absent_from_id_lookup_full_listing_and_borrower_lookup(
    client,
):
    first = client.post("/loans", json=valid_payload(loanId="LN-001"))
    second = client.post(
        "/loans",
        json=valid_payload(
            loanId="LN-002",
            fundingAmount=700.0,
            repaymentAmount=850.0,
        ),
    )

    deleted = client.delete("/loans/LN-001")
    found = client.get("/loans/LN-001")
    listed = client.get("/loans")
    borrower_matches = client.get("/loans?borrowerName=Jane%20Smith")

    assert first.status_code == 201
    assert second.status_code == 201
    assert deleted.status_code == 200
    assert found.status_code == 404
    assert found.get_json() == {
        "error": "loan_not_found",
        "message": "No loan exists for this loan ID.",
    }
    assert listed.status_code == 200
    assert listed.get_json() == {
        "loans": [
            {
                "loanId": "LN-002",
                "borrowerName": "Jane Smith",
                "fundingAmount": 700.0,
                "repaymentAmount": 850.0,
            }
        ]
    }
    assert borrower_matches.status_code == 200
    assert borrower_matches.get_json() == listed.get_json()


def test_delete_preserves_existing_workflows_for_non_deleted_loans(client):
    deleted_candidate = client.post("/loans", json=valid_payload(loanId="LN-001"))
    survivor = client.post(
        "/loans",
        json=valid_payload(
            loanId="LN-002",
            borrowerName="Alex Doe",
            fundingAmount=500.0,
            repaymentAmount=650.0,
        ),
    )
    deleted = client.delete("/loans/LN-001")
    new_loan = client.post(
        "/loans",
        json=valid_payload(
            loanId="LN-003",
            borrowerName="Alex Doe",
            fundingAmount=300.0,
            repaymentAmount=360.0,
        ),
    )

    found_survivor = client.get("/loans/LN-002")
    listed = client.get("/loans")
    borrower_matches = client.get("/loans?borrowerName=Alex%20Doe")

    assert deleted_candidate.status_code == 201
    assert survivor.status_code == 201
    assert deleted.status_code == 200
    assert new_loan.status_code == 201
    assert found_survivor.status_code == 200
    assert found_survivor.get_json() == {
        "loanId": "LN-002",
        "borrowerName": "Alex Doe",
        "fundingAmount": 500.0,
        "repaymentAmount": 650.0,
    }
    assert listed.status_code == 200
    assert [loan["loanId"] for loan in listed.get_json()["loans"]] == [
        "LN-002",
        "LN-003",
    ]
    assert borrower_matches.status_code == 200
    assert [loan["loanId"] for loan in borrower_matches.get_json()["loans"]] == [
        "LN-002",
        "LN-003",
    ]


def test_delete_unknown_and_whitespace_only_loan_ids_return_not_found(client):
    for path in ["/loans/LN-MISSING", "/loans/%20%20%20"]:
        started_at = perf_counter()
        response = client.delete(path)
        elapsed = perf_counter() - started_at

        assert response.status_code == 404
        assert elapsed < 2
        assert response.get_json() == {
            "error": "loan_not_found",
            "message": "No loan exists for this loan ID.",
        }


def test_delete_already_deleted_loan_returns_not_found_and_preserves_remaining_loans(
    client,
):
    first = client.post("/loans", json=valid_payload(loanId="LN-001"))
    second = client.post(
        "/loans",
        json=valid_payload(
            loanId="LN-002",
            borrowerName="Alex Doe",
            fundingAmount=500.0,
            repaymentAmount=650.0,
        ),
    )
    first_delete = client.delete("/loans/LN-001")

    started_at = perf_counter()
    second_delete = client.delete("/loans/LN-001")
    elapsed = perf_counter() - started_at
    listed = client.get("/loans")

    assert first.status_code == 201
    assert second.status_code == 201
    assert first_delete.status_code == 200
    assert second_delete.status_code == 404
    assert elapsed < 2
    assert second_delete.get_json() == {
        "error": "loan_not_found",
        "message": "No loan exists for this loan ID.",
    }
    assert listed.status_code == 200
    assert listed.get_json() == {
        "loans": [
            {
                "loanId": "LN-002",
                "borrowerName": "Alex Doe",
                "fundingAmount": 500.0,
                "repaymentAmount": 650.0,
            }
        ]
    }


def test_delete_loan_returns_not_found_after_new_app_session():
    first_client = create_app({"TESTING": True}).test_client()
    restarted_client = create_app({"TESTING": True}).test_client()

    created = first_client.post("/loans", json=valid_payload(loanId="LN-RESTART"))
    found_before_restart = first_client.get("/loans/LN-RESTART")

    started_at = perf_counter()
    deleted_after_restart = restarted_client.delete("/loans/LN-RESTART")
    elapsed = perf_counter() - started_at

    assert created.status_code == 201
    assert found_before_restart.status_code == 200
    assert deleted_after_restart.status_code == 404
    assert elapsed < 2
    assert deleted_after_restart.get_json() == {
        "error": "loan_not_found",
        "message": "No loan exists for this loan ID.",
    }
