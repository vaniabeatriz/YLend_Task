import os
import time
from dataclasses import dataclass
from functools import wraps
from urllib.parse import urlencode

from flask import current_app, g, jsonify, redirect, request, session, url_for

try:
    from authlib.integrations.flask_client import OAuth
except ImportError:  # pragma: no cover - exercised only without optional dep
    OAuth = None

try:
    import jwt
except ImportError:  # pragma: no cover - exercised only without optional dep
    jwt = None

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - exercised only without optional dep
    load_dotenv = None


AUTH_USER_SESSION_KEY = "auth_user"
AUTH_ACCESS_TOKEN_SESSION_KEY = "auth_access_token"
AUTH_EXPIRES_AT_SESSION_KEY = "auth_expires_at"


class AuthError(Exception):
    def __init__(self, error, message, status_code=401, details=None):
        super().__init__(message)
        self.error = error
        self.message = message
        self.status_code = status_code
        self.details = details or []


class AuthSetupError(AuthError):
    def __init__(self, message, details=None):
        super().__init__(
            "auth_configuration_error",
            message,
            503,
            details,
        )


@dataclass(frozen=True)
class AuthConfig:
    domain: str
    client_id: str
    client_secret: str
    audience: str
    callback_url: str
    logout_return_url: str

    @classmethod
    def from_app(cls, app):
        domain = _normalize_domain(app.config.get("AUTH0_DOMAIN", ""))
        return cls(
            domain=domain,
            client_id=(app.config.get("AUTH0_CLIENT_ID") or "").strip(),
            client_secret=(app.config.get("AUTH0_CLIENT_SECRET") or "").strip(),
            audience=(app.config.get("AUTH0_AUDIENCE") or "").strip(),
            callback_url=(app.config.get("AUTH0_CALLBACK_URL") or "").strip(),
            logout_return_url=(app.config.get("AUTH0_LOGOUT_RETURN_URL") or "").strip(),
        )

    @property
    def issuer(self):
        return f"https://{self.domain}/"

    @property
    def jwks_url(self):
        return f"https://{self.domain}/.well-known/jwks.json"

    @property
    def server_metadata_url(self):
        return f"https://{self.domain}/.well-known/openid-configuration"

    def missing_for_web(self):
        missing = []
        if not self.domain:
            missing.append("AUTH0_DOMAIN")
        if not self.client_id:
            missing.append("AUTH0_CLIENT_ID")
        if not self.client_secret:
            missing.append("AUTH0_CLIENT_SECRET")
        if not self.audience:
            missing.append("AUTH0_AUDIENCE")
        if not self.callback_url:
            missing.append("AUTH0_CALLBACK_URL")
        return missing

    def missing_for_api(self):
        missing = []
        if not self.domain:
            missing.append("AUTH0_DOMAIN")
        if not self.audience:
            missing.append("AUTH0_AUDIENCE")
        return missing


def _normalize_domain(value):
    return str(value or "").strip().removeprefix("https://").removeprefix("http://").rstrip("/")


def _truthy(value):
    return str(value or "").lower() in {"1", "true", "yes", "on"}


def _setup_message(missing):
    if missing:
        return "please, sign in to register"
    return "Auth0 authentication is not configured."


def load_auth_environment():
    if load_dotenv:
        load_dotenv()


def init_auth(app):
    app.config.setdefault("AUTH0_DOMAIN", os.environ.get("AUTH0_DOMAIN", ""))
    app.config.setdefault("AUTH0_CLIENT_ID", os.environ.get("AUTH0_CLIENT_ID", ""))
    app.config.setdefault("AUTH0_CLIENT_SECRET", os.environ.get("AUTH0_CLIENT_SECRET", ""))
    app.config.setdefault("AUTH0_AUDIENCE", os.environ.get("AUTH0_AUDIENCE", ""))
    app.config.setdefault(
        "AUTH0_CALLBACK_URL",
        os.environ.get("AUTH0_CALLBACK_URL", "http://127.0.0.1:5000/callback"),
    )
    app.config.setdefault(
        "AUTH0_LOGOUT_RETURN_URL",
        os.environ.get("AUTH0_LOGOUT_RETURN_URL", "http://127.0.0.1:5000/"),
    )
    if not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = os.environ.get("APP_SECRET_KEY", "dev-secret-key")
    if app.config.get("SESSION_COOKIE_HTTPONLY") is None:
        app.config["SESSION_COOKIE_HTTPONLY"] = True
    if not app.config.get("SESSION_COOKIE_SAMESITE"):
        app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    secure_cookie_setting = os.environ.get("SESSION_COOKIE_SECURE")
    if secure_cookie_setting is not None:
        app.config["SESSION_COOKIE_SECURE"] = _truthy(secure_cookie_setting)
    elif app.config.get("PREFERRED_URL_SCHEME") == "https":
        app.config["SESSION_COOKIE_SECURE"] = True

    if app.testing and "AUTH_DISABLE_FOR_TESTS" not in app.config:
        app.config["AUTH_DISABLE_FOR_TESTS"] = True

    app.extensions["auth0_oauth"] = None
    config = AuthConfig.from_app(app)
    if OAuth and not config.missing_for_web():
        oauth = OAuth(app)
        oauth.register(
            "auth0",
            client_id=config.client_id,
            client_secret=config.client_secret,
            server_metadata_url=config.server_metadata_url,
            client_kwargs={"scope": "openid profile email"},
        )
        app.extensions["auth0_oauth"] = oauth


def error_response(error, message, status_code, details=None):
    payload = {"error": error, "message": message}
    if details:
        payload["details"] = details
    response = jsonify(payload)
    response.status_code = status_code
    return response


def auth_error_response(error):
    return error_response(error.error, error.message, error.status_code, error.details)


def setup_error_for_missing(missing):
    return AuthSetupError(
        _setup_message(missing),
        [{"field": name, "message": f"{name} is required."} for name in missing],
    )


def has_authenticated_session():
    if not session.get(AUTH_USER_SESSION_KEY) or not session.get(
        AUTH_ACCESS_TOKEN_SESSION_KEY
    ):
        return False

    expires_at = session.get(AUTH_EXPIRES_AT_SESSION_KEY)
    if expires_at and expires_at <= int(time.time()):
        clear_auth_session()
        return False

    return True


def current_auth_status():
    config = AuthConfig.from_app(current_app)
    setup_error = None
    missing = config.missing_for_web()
    if missing:
        setup_error = _setup_message(missing)

    if has_authenticated_session():
        return {
            "authenticated": True,
            "user": session.get(AUTH_USER_SESSION_KEY),
            "accessToken": session.get(AUTH_ACCESS_TOKEN_SESSION_KEY),
            "setupError": None,
        }

    return {
        "authenticated": False,
        "user": None,
        "accessToken": None,
        "setupError": setup_error,
    }


def store_auth_session(user, access_token, expires_at=None):
    session[AUTH_USER_SESSION_KEY] = user or {}
    session[AUTH_ACCESS_TOKEN_SESSION_KEY] = access_token
    if expires_at:
        session[AUTH_EXPIRES_AT_SESSION_KEY] = int(expires_at)
    else:
        session.pop(AUTH_EXPIRES_AT_SESSION_KEY, None)


def clear_auth_session():
    session.pop(AUTH_USER_SESSION_KEY, None)
    session.pop(AUTH_ACCESS_TOKEN_SESSION_KEY, None)
    session.pop(AUTH_EXPIRES_AT_SESSION_KEY, None)


def start_login():
    test_redirect_url = current_app.config.get("AUTH_TEST_LOGIN_REDIRECT_URL")
    if test_redirect_url:
        return redirect(test_redirect_url)

    config = AuthConfig.from_app(current_app)
    missing = config.missing_for_web()
    if missing:
        raise setup_error_for_missing(missing)
    oauth = current_app.extensions.get("auth0_oauth")
    if oauth is None:
        raise AuthSetupError("Authlib is required to start Auth0 sign-in.")

    return oauth.auth0.authorize_redirect(
        redirect_uri=config.callback_url,
        audience=config.audience,
    )


def handle_callback():
    test_user = current_app.config.get("AUTH_TEST_CALLBACK_USER")
    test_token = current_app.config.get("AUTH_TEST_CALLBACK_ACCESS_TOKEN")
    if test_user and test_token:
        store_auth_session(
            test_user,
            test_token,
            current_app.config.get("AUTH_TEST_CALLBACK_EXPIRES_AT"),
        )
        return redirect(url_for("api.index"))

    config = AuthConfig.from_app(current_app)
    missing = config.missing_for_web()
    if missing:
        raise setup_error_for_missing(missing)
    oauth = current_app.extensions.get("auth0_oauth")
    if oauth is None:
        raise AuthSetupError("Authlib is required to complete Auth0 sign-in.")

    try:
        token = oauth.auth0.authorize_access_token()
    except Exception as exc:  # pragma: no cover - depends on provider response
        clear_auth_session()
        raise AuthError(
            "authentication_failed",
            "Auth0 sign-in could not be completed. Please try again.",
            401,
        ) from exc

    user = token.get("userinfo") or {}
    if not user:
        user = {"sub": token.get("sub"), "name": token.get("name"), "email": token.get("email")}
    access_token = token.get("access_token")
    if not access_token:
        clear_auth_session()
        raise AuthError(
            "authentication_failed",
            "Auth0 did not return an access token for the loan API.",
            401,
        )

    store_auth_session(user, access_token, token.get("expires_at"))
    return redirect(url_for("api.index"))


def handle_logout():
    clear_auth_session()
    config = AuthConfig.from_app(current_app)
    if config.domain and config.client_id:
        params = urlencode(
            {
                "returnTo": config.logout_return_url or url_for("api.index", _external=True),
                "client_id": config.client_id,
            }
        )
        return redirect(f"https://{config.domain}/v2/logout?{params}")
    return redirect(url_for("api.index"))


def get_token_auth_header():
    auth = request.headers.get("Authorization")
    if not auth:
        raise AuthError(
            "authentication_required",
            "A valid Auth0 access token is required.",
        )

    parts = auth.split()
    if parts[0].lower() != "bearer":
        raise AuthError(
            "invalid_token",
            "Authorization header must start with Bearer.",
        )
    if len(parts) == 1:
        raise AuthError("invalid_token", "Bearer token is missing.")
    if len(parts) > 2:
        raise AuthError("invalid_token", "Authorization header must be Bearer token.")
    return parts[1]


def verify_access_token(token):
    verifier = current_app.config.get("AUTH_TOKEN_VERIFIER")
    if verifier:
        return verifier(token)

    config = AuthConfig.from_app(current_app)
    missing = config.missing_for_api()
    if missing:
        raise setup_error_for_missing(missing)
    if jwt is None:
        raise AuthSetupError("PyJWT is required to validate Auth0 access tokens.")

    try:
        jwks_client = current_app.config.get("AUTH_JWKS_CLIENT") or jwt.PyJWKClient(
            config.jwks_url
        )
        signing_key = jwks_client.get_signing_key_from_jwt(token).key
        return jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience=config.audience,
            issuer=config.issuer,
        )
    except getattr(jwt, "ExpiredSignatureError", Exception) as exc:
        raise AuthError(
            "invalid_token",
            "The Auth0 access token is invalid or expired.",
        ) from exc
    except getattr(jwt, "InvalidTokenError", Exception) as exc:
        raise AuthError(
            "invalid_token",
            "The Auth0 access token is invalid or expired.",
        ) from exc
    except Exception as exc:
        raise AuthError(
            "invalid_token",
            "The Auth0 access token is invalid or expired.",
        ) from exc


def require_auth(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_app.testing and current_app.config.get("AUTH_DISABLE_FOR_TESTS"):
            return view(*args, **kwargs)

        try:
            token = get_token_auth_header()
            g.auth_claims = verify_access_token(token)
        except AuthError as exc:
            return auth_error_response(exc)

        return view(*args, **kwargs)

    return wrapped
