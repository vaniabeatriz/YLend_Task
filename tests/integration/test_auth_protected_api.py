def valid_payload(**overrides):
    payload = {
        "loanId": "LN-001",
        "borrowerName": "Jane Smith",
        "fundingAmount": 1000.0,
        "repaymentAmount": 1200.0,
    }
    payload.update(overrides)
    return payload


def assert_authentication_required(response):
    assert response.status_code == 401
    assert response.get_json() == {
        "error": "authentication_required",
        "message": "A valid Auth0 access token is required.",
    }


def assert_invalid_token(response):
    assert response.status_code == 401
    assert response.get_json() == {
        "error": "invalid_token",
        "message": "The Auth0 access token is invalid or expired.",
    }


def test_protected_loan_endpoints_require_bearer_token(protected_client):
    requests = [
        protected_client.post("/loans", json=valid_payload()),
        protected_client.get("/loans"),
        protected_client.get("/loans?borrowerName=Jane%20Smith"),
        protected_client.get("/loans/LN-001"),
        protected_client.delete("/loans/LN-001"),
    ]

    for response in requests:
        assert_authentication_required(response)


def test_protected_loan_endpoints_reject_invalid_bearer_token(protected_client):
    headers = {"Authorization": "Bearer invalid-token"}
    requests = [
        protected_client.post("/loans", json=valid_payload(), headers=headers),
        protected_client.get("/loans", headers=headers),
        protected_client.get("/loans?borrowerName=Jane%20Smith", headers=headers),
        protected_client.get("/loans/LN-001", headers=headers),
        protected_client.delete("/loans/LN-001", headers=headers),
    ]

    for response in requests:
        assert_invalid_token(response)


def test_authenticated_loan_workflows_preserve_existing_behaviour(
    protected_client,
    auth_headers,
):
    created = protected_client.post(
        "/loans",
        json=valid_payload(loanId="LN-001"),
        headers=auth_headers,
    )
    duplicate = protected_client.post(
        "/loans",
        json=valid_payload(loanId="  LN-001  "),
        headers=auth_headers,
    )
    invalid = protected_client.post(
        "/loans",
        json=valid_payload(loanId="LN-BAD", fundingAmount=0),
        headers=auth_headers,
    )
    listed = protected_client.get("/loans", headers=auth_headers)
    borrower_matches = protected_client.get(
        "/loans?borrowerName=Jane%20Smith",
        headers=auth_headers,
    )
    found = protected_client.get("/loans/LN-001", headers=auth_headers)
    missing = protected_client.get("/loans/LN-MISSING", headers=auth_headers)
    deleted = protected_client.delete("/loans/LN-001", headers=auth_headers)
    missing_after_delete = protected_client.get("/loans/LN-001", headers=auth_headers)

    assert created.status_code == 201
    assert duplicate.status_code == 409
    assert invalid.status_code == 400
    assert listed.status_code == 200
    assert borrower_matches.status_code == 200
    assert found.status_code == 200
    assert missing.status_code == 404
    assert deleted.status_code == 200
    assert missing_after_delete.status_code == 404
    assert listed.get_json()["loans"][0]["loanId"] == "LN-001"
    assert borrower_matches.get_json()["loans"][0]["borrowerName"] == "Jane Smith"
    assert found.get_json()["loanId"] == "LN-001"
    assert deleted.get_json()["loanId"] == "LN-001"


def test_missing_auth0_config_on_protected_api_returns_setup_error():
    from app import create_app

    app = create_app({"TESTING": True, "AUTH_DISABLE_FOR_TESTS": False})
    client = app.test_client()

    response = client.get("/loans", headers={"Authorization": "Bearer any-token"})

    assert response.status_code == 503
    assert response.get_json()["error"] == "auth_configuration_error"
    assert "Missing Auth0 configuration" in response.get_json()["message"]
