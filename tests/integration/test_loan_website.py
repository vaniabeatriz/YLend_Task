from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STATIC_DIR = ROOT / "app" / "static"


def read_static_asset(filename):
    return (STATIC_DIR / filename).read_text(encoding="utf-8")


def test_website_home_renders_create_and_current_list_shell(client):
    response = client.get("/")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert response.content_type.startswith("text/html")
    assert "Loan Management" in body
    assert 'id="home-section"' in body
    assert 'id="home-heading"' in body
    assert "Create, find, review, and delete loan." in body
    assert 'id="auth-status"' in body
    assert 'id="login-link"' in body
    assert 'href="/login"' in body
    assert 'id="logout-link"' in body
    assert 'href="/logout"' in body
    assert "bootstrap" in body.lower()
    assert 'href="/static/loan_website.css"' in body
    assert 'src="/static/loan_website.js"' in body
    assert 'id="global-feedback"' in body
    assert 'id="create-loan-form"' in body
    assert 'name="loanId"' in body
    assert 'name="borrowerName"' in body
    assert 'name="fundingAmount"' in body
    assert 'name="repaymentAmount"' in body
    assert 'id="current-loans"' in body
    assert 'id="current-loans-status"' in body
    assert "Open this panel to load current loans." in body


def test_website_home_renders_endpoint_menu(client):
    response = client.get("/")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'class="endpoint-menu"' in body
    assert 'aria-label="Loan workflow actions"' in body
    assert "data-auth-required" in body
    assert 'data-section-target="create-section"' in body
    assert 'data-section-target="current-loans-section"' in body
    assert 'data-section-target="borrower-search-section"' in body
    assert 'data-section-target="lookup-section"' in body
    assert 'data-section-target="delete-section"' in body
    assert 'aria-expanded="false"' in body
    assert 'href="/health"' in body
    assert "Create loan" in body
    assert "List loans" in body
    assert "Search borrower" in body
    assert "Look up loan" in body
    assert "Delete loan" in body
    assert "Health check" in body
    assert "endpoint-method" not in body
    assert "data-workflow-section" in body
    assert body.count("data-workflow-section") == 5
    assert body.count("hidden") >= 5


def test_loan_website_static_assets_are_served(client):
    css = client.get("/static/loan_website.css")
    js = client.get("/static/loan_website.js")

    assert css.status_code == 200
    assert js.status_code == 200
    assert css.content_type.startswith("text/css")
    assert "javascript" in js.content_type


def test_loan_website_js_contains_create_list_and_failure_preservation_hooks():
    script = read_static_asset("loan_website.js")

    assert "create-loan-form" in script
    assert "current-loans" in script
    assert "global-feedback" in script
    assert "POST" in script
    assert "GET" in script
    assert "/loans" in script
    assert "loadCurrentLoans" in script
    assert "renderLoanCollection" in script
    assert "validation_error" in script
    assert "duplicate_loan_id" in script
    assert "preserveCreateFormValues" in script
    assert "loanId" in script
    assert "borrowerName" in script
    assert "fundingAmount" in script
    assert "repaymentAmount" in script
    assert "showWorkflowSection" in script
    assert "data-section-target" in script
    assert "data-workflow-section" in script
    assert "loadAuthStatus" in script
    assert "applyAuthState" in script
    assert "Authorization" in script
    assert "Bearer" in script
    assert 'sectionId === "current-loans-section"' in script
    assert 'document.addEventListener("DOMContentLoaded", () => {' in script
    assert "bindWebsiteEvents();" in script
    assert "loadAuthStatus();" in script


def test_website_home_can_render_initial_auth_setup_error(client):
    response = client.get("/login")
    body = response.get_data(as_text=True)

    assert response.status_code == 503
    assert "Please sign in or create an account to continue." in body


def test_website_home_renders_search_and_lookup_regions(client):
    response = client.get("/")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'id="borrower-search-form"' in body
    assert 'name="borrowerName"' in body
    assert 'id="borrower-results"' in body
    assert "No loans match this borrower name." in body
    assert 'id="loan-lookup-form"' in body
    assert 'name="loanId"' in body
    assert 'id="lookup-result"' in body
    assert "No loan exists for this loan ID." in body


def test_loan_website_js_contains_borrower_search_lookup_and_empty_state_hooks():
    script = read_static_asset("loan_website.js")

    assert "borrower-search-form" in script
    assert "borrower-results" in script
    assert "loan-lookup-form" in script
    assert "lookup-result" in script
    assert "URLSearchParams" in script
    assert "borrowerName" in script
    assert "loan_not_found" in script
    assert "No loans match this borrower name." in script
    assert "No loan exists for this loan ID." in script
    assert "handleBorrowerSearch" in script
    assert "handleLoanLookup" in script


def test_website_home_renders_delete_region_and_confirmation_copy(client):
    response = client.get("/")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'id="delete-loan-form"' in body
    assert 'id="delete-loan-id"' in body
    assert 'name="loanId"' in body
    assert 'id="deleted-loan-result"' in body
    assert "Deleted loan details will appear here." in body
    assert "No loan exists for this loan ID." in body


def test_loan_website_js_contains_delete_confirmation_and_refresh_hooks():
    script = read_static_asset("loan_website.js")

    assert "delete-loan-form" in script
    assert "deleted-loan-result" in script
    assert "DELETE" in script
    assert "handleLoanDelete" in script
    assert "Deleted loan" in script
    assert "loan_not_found" in script
    assert "No loan exists for this loan ID." in script
    assert "loadCurrentLoans" in script


def test_website_home_renders_loading_and_accessible_status_regions(client):
    response = client.get("/")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'role="status"' in body
    assert body.count('aria-live="polite"') >= 6
    assert 'data-action-control' in body
    assert 'data-feedback-target-ms="2000"' in body


def test_loan_website_js_contains_service_unavailable_loading_and_retry_hooks():
    script = read_static_asset("loan_website.js")

    assert "service-unavailable" in script
    assert "The loan service is unavailable" in script
    assert "startAction" in script
    assert "finishAction" in script
    assert "activeAction" in script
    assert "setActionControlsDisabled" in script
    assert "An action is already in progress." in script
    assert "localFeedbackTargetMs" in script
    assert "2000" in script
    assert "restoreCreateFormValues" in script
    assert "authentication_required" in script
    assert "invalid_token" in script
    assert "auth_configuration_error" in script
    assert "Sign in to use loan workflows." in script


def test_loan_website_css_contains_responsive_and_no_overflow_safeguards():
    styles = read_static_asset("loan_website.css")

    assert ".endpoint-menu" in styles
    assert ".endpoint-menu-item" in styles
    assert "overflow-x: hidden" in styles
    assert "min-width: 0" in styles
    assert "overflow-wrap: anywhere" in styles
    assert "white-space: normal" in styles
    assert "@media (max-width: 820px)" in styles
    assert "@media (max-width: 520px)" in styles
    assert "grid-template-columns: 1fr" in styles
