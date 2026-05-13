import pytest

from app import create_app
from app.auth import AuthError


TEST_ACCESS_TOKEN = "valid-test-token"


def valid_test_token_verifier(token):
    if token == TEST_ACCESS_TOKEN:
        return {
            "sub": "auth0|test-user",
            "aud": "https://loan-api.test",
            "iss": "https://test-tenant.auth0.com/",
        }
    raise AuthError("invalid_token", "The Auth0 access token is invalid or expired.")


@pytest.fixture
def database_path(tmp_path):
    return tmp_path / "loans.sqlite3"


def protected_app_config(database_path, **overrides):
    config = {
        "TESTING": True,
        "LOAN_DATABASE_PATH": str(database_path),
        "AUTH_DISABLE_FOR_TESTS": False,
        "AUTH0_DOMAIN": "test-tenant.auth0.com",
        "AUTH0_CLIENT_ID": "test-client-id",
        "AUTH0_CLIENT_SECRET": "test-client-secret",
        "AUTH0_AUDIENCE": "https://loan-api.test",
        "AUTH0_CALLBACK_URL": "http://127.0.0.1:5000/callback",
        "AUTH_TOKEN_VERIFIER": valid_test_token_verifier,
    }
    config.update(overrides)
    return config


@pytest.fixture
def app(database_path):
    return create_app({"TESTING": True, "LOAN_DATABASE_PATH": str(database_path)})


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers():
    return {"Authorization": f"Bearer {TEST_ACCESS_TOKEN}"}


@pytest.fixture
def make_protected_app(database_path):
    def _make(**overrides):
        return create_app(protected_app_config(database_path, **overrides))

    return _make


@pytest.fixture
def protected_app(make_protected_app):
    return make_protected_app()


@pytest.fixture
def protected_client(protected_app):
    return protected_app.test_client()
