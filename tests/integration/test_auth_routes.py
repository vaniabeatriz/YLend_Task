from app import create_app


def test_auth_status_reports_signed_out_state(client):
    response = client.get("/auth/status")

    assert response.status_code == 200
    assert response.get_json()["authenticated"] is False
    assert response.get_json()["accessToken"] is None


def test_login_redirects_to_mocked_auth0_url():
    app = create_app(
        {
            "TESTING": True,
            "AUTH_DISABLE_FOR_TESTS": False,
            "AUTH_TEST_LOGIN_REDIRECT_URL": "https://test-tenant.auth0.com/login",
        }
    )
    client = app.test_client()

    response = client.get("/login")

    assert response.status_code == 302
    assert response.headers["Location"] == "https://test-tenant.auth0.com/login"


def test_callback_stores_session_and_logout_clears_it():
    app = create_app(
        {
            "TESTING": True,
            "AUTH_TEST_CALLBACK_USER": {
                "name": "Jane Reviewer",
                "email": "jane@example.com",
            },
            "AUTH_TEST_CALLBACK_ACCESS_TOKEN": "valid-test-token",
        }
    )
    client = app.test_client()

    callback = client.get("/callback")
    signed_in = client.get("/auth/status")
    logout = client.get("/logout")
    signed_out = client.get("/auth/status")

    assert callback.status_code == 302
    assert callback.headers["Location"] == "/"
    assert signed_in.get_json() == {
        "authenticated": True,
        "user": {
            "name": "Jane Reviewer",
            "email": "jane@example.com",
        },
        "accessToken": "valid-test-token",
        "setupError": None,
    }
    assert logout.status_code == 302
    assert logout.headers["Location"] == "/"
    assert signed_out.get_json()["authenticated"] is False


def test_callback_provider_failure_returns_recoverable_auth_error():
    class FailingAuth0Client:
        def authorize_access_token(self):
            raise RuntimeError("provider unavailable")

    class FailingOAuth:
        auth0 = FailingAuth0Client()

    app = create_app(
        {
            "TESTING": True,
            "AUTH_DISABLE_FOR_TESTS": False,
            "AUTH0_DOMAIN": "test-tenant.auth0.com",
            "AUTH0_CLIENT_ID": "test-client-id",
            "AUTH0_CLIENT_SECRET": "test-client-secret",
            "AUTH0_AUDIENCE": "https://loan-api.test",
            "AUTH0_CALLBACK_URL": "http://127.0.0.1:5000/callback",
        }
    )
    app.extensions["auth0_oauth"] = FailingOAuth()
    client = app.test_client()

    response = client.get("/callback")

    assert response.status_code == 401
    assert "Auth0 sign-in could not be completed" in response.get_data(as_text=True)


def test_missing_auth0_config_does_not_block_health_or_home():
    app = create_app({"TESTING": True, "AUTH_DISABLE_FOR_TESTS": False})
    client = app.test_client()

    home = client.get("/")
    health = client.get("/health")
    login = client.get("/login")
    status = client.get("/auth/status")

    assert home.status_code == 200
    assert health.status_code == 200
    assert health.get_json() == {"status": "ok"}
    assert login.status_code == 503
    assert "Missing Auth0 configuration" in login.get_data(as_text=True)
    assert "Missing Auth0 configuration" in status.get_json()["setupError"]
