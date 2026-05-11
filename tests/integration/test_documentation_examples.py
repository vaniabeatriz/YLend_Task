from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_readme_documents_core_commands_and_demo_flow():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "pip install -r requirements.txt" in readme
    assert "flask --app app run --debug" in readme
    assert "pytest --cov=app --cov-report=term-missing --cov-fail-under=80" in readme
    assert "curl http://127.0.0.1:5000/health" in readme
    assert "POST http://127.0.0.1:5000/loans" in readme
    assert "GET http://127.0.0.1:5000/loans" in readme
    assert "GET http://127.0.0.1:5000/loans?borrowerName=<borrowerName>" in readme
    assert "GET http://127.0.0.1:5000/loans/<loanId>" in readme
    assert "curl -i http://127.0.0.1:5000/loans" in readme
    assert 'curl -i "http://127.0.0.1:5000/loans?borrowerName=Jane%20Smith"' in readme
    assert 'curl -i "http://127.0.0.1:5000/loans?borrowerName=No%20Match"' in readme
    assert "curl -i http://127.0.0.1:5000/loans/LN-001" in readme
    assert '"loans": []' in readme
    assert "borrowerName is required." in readme
    assert "404 Not Found" in readme
    assert "409 Conflict" in readme
    assert "400 Bad Request" in readme
    assert "Restart Behavior" in readme
    assert "201 Created" in readme


def test_borrower_name_lookup_quickstart_documents_core_commands_and_demo_flow():
    quickstart = (
        ROOT / "specs" / "004-borrower-name-lookup" / "quickstart.md"
    ).read_text(encoding="utf-8")

    assert "pip install -r requirements.txt" in quickstart
    assert "flask --app app run --debug" in quickstart
    assert "pytest --cov=app --cov-report=term-missing --cov-fail-under=80" in quickstart
    assert "POST http://127.0.0.1:5000/loans" in quickstart
    assert "curl -i http://127.0.0.1:5000/loans" in quickstart
    assert 'curl -i "http://127.0.0.1:5000/loans?borrowerName=Jane%20Smith"' in quickstart
    assert 'curl -i "http://127.0.0.1:5000/loans?borrowerName=No%20Match"' in quickstart
    assert 'curl -i "http://127.0.0.1:5000/loans?borrowerName="' in quickstart
    assert '"loans": []' in quickstart
    assert "borrowerName is required" in quickstart
    assert "Restart Behavior" in quickstart
    assert "201 Created" in quickstart
