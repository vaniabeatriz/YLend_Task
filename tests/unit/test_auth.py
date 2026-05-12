import time

import pytest

from app import create_app
from app.auth import (
    AuthConfig,
    AuthError,
    AUTH_ACCESS_TOKEN_SESSION_KEY,
    AUTH_EXPIRES_AT_SESSION_KEY,
    AUTH_USER_SESSION_KEY,
    current_auth_status,
    get_token_auth_header,
    has_authenticated_session,
    verify_access_token,
)


def test_auth_config_normalizes_domain_and_reports_missing_values(app):
    app.config.update(
        {
            "AUTH0_DOMAIN": "https://example.auth0.com/",
            "AUTH0_CLIENT_ID": "",
            "AUTH0_CLIENT_SECRET": "",
            "AUTH0_AUDIENCE": "",
            "AUTH0_CALLBACK_URL": "",
        }
    )

    config = AuthConfig.from_app(app)

    assert config.domain == "example.auth0.com"
    assert config.missing_for_web() == [
        "AUTH0_CLIENT_ID",
        "AUTH0_CLIENT_SECRET",
        "AUTH0_AUDIENCE",
        "AUTH0_CALLBACK_URL",
    ]
    assert config.missing_for_api() == ["AUTH0_AUDIENCE"]


def test_auth_status_reports_signed_out_and_setup_error(app):
    with app.test_request_context("/"):
        status = current_auth_status()

    assert status["authenticated"] is False
    assert status["accessToken"] is None
    assert status["setupError"] == "Please sign in or register to continue."


def test_authenticated_session_expires_and_clears_session(app):
    with app.test_request_context("/"):
        session = __import__("flask").session
        session[AUTH_USER_SESSION_KEY] = {"name": "Expired User"}
        session[AUTH_ACCESS_TOKEN_SESSION_KEY] = "token"
        session[AUTH_EXPIRES_AT_SESSION_KEY] = int(time.time()) - 1

        assert has_authenticated_session() is False
        assert AUTH_USER_SESSION_KEY not in session
        assert AUTH_ACCESS_TOKEN_SESSION_KEY not in session


def test_get_token_auth_header_requires_bearer_token(protected_app):
    with protected_app.test_request_context("/loans"):
        with pytest.raises(AuthError) as exc:
            get_token_auth_header()
    assert exc.value.error == "authentication_required"

    with protected_app.test_request_context(
        "/loans", headers={"Authorization": "Basic token"}
    ):
        with pytest.raises(AuthError) as exc:
            get_token_auth_header()
    assert exc.value.error == "invalid_token"

    with protected_app.test_request_context(
        "/loans", headers={"Authorization": "Bearer one two"}
    ):
        with pytest.raises(AuthError) as exc:
            get_token_auth_header()
    assert exc.value.error == "invalid_token"

    with protected_app.test_request_context(
        "/loans", headers={"Authorization": "Bearer"}
    ):
        with pytest.raises(AuthError) as exc:
            get_token_auth_header()
    assert exc.value.error == "invalid_token"

    with protected_app.test_request_context(
        "/loans", headers={"Authorization": "Bearer expected-token"}
    ):
        assert get_token_auth_header() == "expected-token"


def test_verify_access_token_uses_injected_verifier(protected_app):
    with protected_app.app_context():
        claims = verify_access_token("valid-test-token")

    assert claims["sub"] == "auth0|test-user"


@pytest.mark.parametrize(
    "token",
    ["expired-token", "wrong-audience-token", "wrong-issuer-token", "malformed-token"],
)
def test_verify_access_token_surfaces_invalid_token_failures(protected_app, token):
    with protected_app.app_context():
        with pytest.raises(AuthError) as exc:
            verify_access_token(token)

    assert exc.value.error == "invalid_token"
    assert exc.value.status_code == 401


def test_verify_access_token_reports_missing_api_configuration():
    app = create_app({"TESTING": True, "AUTH_DISABLE_FOR_TESTS": False})

    with app.app_context():
        with pytest.raises(AuthError) as exc:
            verify_access_token("any-token")

    assert exc.value.error == "auth_configuration_error"
    assert exc.value.status_code == 503
    assert exc.value.message == "Please sign in or register to continue."


def test_verify_access_token_surfaces_jwks_lookup_failures():
    class FailingJwksClient:
        def get_signing_key_from_jwt(self, token):
            raise RuntimeError("JWKS unavailable")

    app = create_app(
        {
            "TESTING": True,
            "AUTH_DISABLE_FOR_TESTS": False,
            "AUTH0_DOMAIN": "test-tenant.auth0.com",
            "AUTH0_AUDIENCE": "https://loan-api.test",
            "AUTH_JWKS_CLIENT": FailingJwksClient(),
        }
    )

    with app.app_context():
        with pytest.raises(AuthError) as exc:
            verify_access_token("token")

    assert exc.value.error == "invalid_token"
    assert exc.value.status_code == 401


def test_session_cookie_security_defaults_and_https_secure_override():
    app = create_app({"TESTING": True})
    secure_app = create_app(
        {
            "TESTING": True,
            "PREFERRED_URL_SCHEME": "https",
        }
    )

    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"
    assert app.config["SESSION_COOKIE_SECURE"] is False
    assert secure_app.config["SESSION_COOKIE_SECURE"] is True
