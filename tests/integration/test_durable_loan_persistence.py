from pathlib import Path
from time import perf_counter

import pytest

from app import create_app
from app.repositories.loan_repository import LoanStorageError


def valid_payload(**overrides):
    payload = {
        "loanId": "LN-001",
        "borrowerName": "Jane Smith",
        "fundingAmount": 1000.0,
        "repaymentAmount": 1200.0,
    }
    payload.update(overrides)
    return payload


def test_authenticated_lookup_listing_and_search_survive_restart(
    make_protected_app,
    auth_headers,
):
    first_client = make_protected_app().test_client()
    created = first_client.post(
        "/loans",
        json=valid_payload(loanId="LN-RESTART"),
        headers=auth_headers,
    )

    restarted_client = make_protected_app().test_client()
    started = perf_counter()
    found = restarted_client.get("/loans/LN-RESTART", headers=auth_headers)
    listed = restarted_client.get("/loans", headers=auth_headers)
    searched = restarted_client.get(
        "/loans?borrowerName=Jane%20Smith",
        headers=auth_headers,
    )
    elapsed = perf_counter() - started

    assert created.status_code == 201
    assert found.status_code == 200
    assert listed.status_code == 200
    assert searched.status_code == 200
    assert elapsed < 2
    assert found.get_json()["loanId"] == "LN-RESTART"
    assert listed.get_json()["loans"][0]["loanId"] == "LN-RESTART"
    assert searched.get_json()["loans"][0]["borrowerName"] == "Jane Smith"


def test_duplicate_after_restart_preserves_existing_response(
    make_protected_app,
    auth_headers,
):
    first_client = make_protected_app().test_client()
    created = first_client.post(
        "/loans",
        json=valid_payload(loanId="LN-DUPLICATE"),
        headers=auth_headers,
    )

    restarted_client = make_protected_app().test_client()
    duplicate = restarted_client.post(
        "/loans",
        json=valid_payload(loanId="  LN-DUPLICATE  "),
        headers=auth_headers,
    )

    assert created.status_code == 201
    assert duplicate.status_code == 409
    assert duplicate.get_json() == {
        "error": "duplicate_loan_id",
        "message": "A loan with this loan ID already exists.",
    }


def test_invalid_create_after_restart_does_not_leave_partial_record(
    make_protected_app,
    auth_headers,
):
    first_client = make_protected_app().test_client()
    invalid = first_client.post(
        "/loans",
        json=valid_payload(loanId="LN-INVALID", fundingAmount=0),
        headers=auth_headers,
    )

    restarted_client = make_protected_app().test_client()
    listed = restarted_client.get("/loans", headers=auth_headers)
    missing = restarted_client.get("/loans/LN-INVALID", headers=auth_headers)

    assert invalid.status_code == 400
    assert listed.status_code == 200
    assert listed.get_json() == {"loans": []}
    assert missing.status_code == 404


def test_delete_persists_absence_after_restart(make_protected_app, auth_headers):
    first_client = make_protected_app().test_client()
    created = first_client.post(
        "/loans",
        json=valid_payload(loanId="LN-DELETE"),
        headers=auth_headers,
    )
    deleted = first_client.delete("/loans/LN-DELETE", headers=auth_headers)

    restarted_client = make_protected_app().test_client()
    missing = restarted_client.get("/loans/LN-DELETE", headers=auth_headers)
    listed = restarted_client.get("/loans", headers=auth_headers)
    searched = restarted_client.get(
        "/loans?borrowerName=Jane%20Smith",
        headers=auth_headers,
    )

    assert created.status_code == 201
    assert deleted.status_code == 200
    assert deleted.get_json()["loanId"] == "LN-DELETE"
    assert missing.status_code == 404
    assert listed.get_json() == {"loans": []}
    assert searched.get_json() == {"loans": []}


def test_app_startup_initializes_unused_database_path(database_path, auth_headers):
    assert not Path(database_path).exists()

    app = create_app(
        {
            "TESTING": True,
            "LOAN_DATABASE_PATH": str(database_path),
            "AUTH_DISABLE_FOR_TESTS": False,
            "AUTH0_DOMAIN": "test-tenant.auth0.com",
            "AUTH0_CLIENT_ID": "test-client-id",
            "AUTH0_CLIENT_SECRET": "test-client-secret",
            "AUTH0_AUDIENCE": "https://loan-api.test",
            "AUTH0_CALLBACK_URL": "http://127.0.0.1:5000/callback",
            "AUTH_TOKEN_VERIFIER": lambda token: {"sub": "auth0|test-user"},
        }
    )
    client = app.test_client()

    response = client.get("/loans", headers=auth_headers)

    assert Path(database_path).exists()
    assert response.status_code == 200
    assert response.get_json() == {"loans": []}


def test_app_factory_uses_configured_database_url_repository(
    make_protected_app,
    auth_headers,
    monkeypatch,
):
    created_repositories = []

    class CapturingPostgresRepository:
        def __init__(self, database_url):
            self.database_url = database_url
            created_repositories.append(self)

        def initialize(self):
            self.initialized = True

        def list_all(self):
            return []

    monkeypatch.setattr(
        "app.repositories.repository_factory.PostgresLoanRepository",
        CapturingPostgresRepository,
    )

    client = make_protected_app(
        LOAN_DATABASE_PATH=None,
        LOAN_DATABASE_URL="postgresql://example/db",
    ).test_client()
    response = client.get("/loans", headers=auth_headers)

    assert response.status_code == 200
    assert response.get_json() == {"loans": []}
    assert created_repositories[0].database_url == "postgresql://example/db"
    assert created_repositories[0].initialized is True


def test_deployed_runtime_without_database_url_returns_storage_error(
    make_protected_app,
    auth_headers,
):
    client = make_protected_app(
        LOAN_DATABASE_PATH=None,
        LOAN_REQUIRE_DATABASE_URL=True,
    ).test_client()

    response = client.get("/loans", headers=auth_headers)

    assert response.status_code == 503
    assert response.get_json() == {
        "error": "loan_storage_unavailable",
        "message": "Loan storage is unavailable. Check local persistence setup and retry.",
    }


class FailingLoanRepository:
    def initialize(self):
        return None

    def create(self, loan):
        raise LoanStorageError("storage failed")

    def get(self, loan_id):
        raise LoanStorageError("storage failed")

    def delete(self, loan_id):
        raise LoanStorageError("storage failed")

    def list_all(self):
        raise LoanStorageError("storage failed")

    def list_by_borrower_name(self, borrower_name):
        raise LoanStorageError("storage failed")


@pytest.mark.parametrize(
    ("method", "path", "json_payload"),
    [
        ("post", "/loans", valid_payload()),
        ("get", "/loans", None),
        ("get", "/loans?borrowerName=Jane%20Smith", None),
        ("get", "/loans/LN-001", None),
        ("delete", "/loans/LN-001", None),
    ],
)
def test_storage_unavailable_returns_service_error_without_changing_auth(
    make_protected_app,
    auth_headers,
    method,
    path,
    json_payload,
):
    client = make_protected_app(
        LOAN_REPOSITORY=FailingLoanRepository(),
    ).test_client()

    request = getattr(client, method)
    kwargs = {"headers": auth_headers}
    if json_payload is not None:
        kwargs["json"] = json_payload

    response = request(path, **kwargs)

    assert response.status_code == 503
    assert response.get_json() == {
        "error": "loan_storage_unavailable",
        "message": "Loan storage is unavailable. Check local persistence setup and retry.",
    }


def test_storage_setup_failure_returns_service_error(
    make_protected_app,
    auth_headers,
    tmp_path,
):
    blocked_parent = tmp_path / "not-a-directory"
    blocked_parent.write_text("file blocks directory creation", encoding="utf-8")
    client = make_protected_app(
        LOAN_DATABASE_PATH=str(blocked_parent / "loans.sqlite3"),
    ).test_client()

    response = client.get("/loans", headers=auth_headers)

    assert response.status_code == 503
    assert response.get_json() == {
        "error": "loan_storage_unavailable",
        "message": "Loan storage is unavailable. Check local persistence setup and retry.",
    }


def test_storage_failure_does_not_delete_existing_durable_data(
    make_protected_app,
    auth_headers,
):
    healthy_client = make_protected_app().test_client()
    created = healthy_client.post(
        "/loans",
        json=valid_payload(loanId="LN-SAFE"),
        headers=auth_headers,
    )

    failing_client = make_protected_app(
        LOAN_REPOSITORY=FailingLoanRepository(),
    ).test_client()
    failed = failing_client.get("/loans", headers=auth_headers)

    restarted_healthy_client = make_protected_app().test_client()
    found = restarted_healthy_client.get("/loans/LN-SAFE", headers=auth_headers)

    assert created.status_code == 201
    assert failed.status_code == 503
    assert found.status_code == 200
    assert found.get_json()["loanId"] == "LN-SAFE"
