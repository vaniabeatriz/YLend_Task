# Quickstart: Loan Website

This quickstart validates the single-page website locally. The website uses the
same running Flask application as the loan API, and loans remain temporary for
the current application session.

## Prerequisites

- Python 3.11+
- A shell with `python3` and `pip`
- A modern browser

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run Locally

```bash
flask --app app run --debug
```

Open `http://127.0.0.1:5000/` in a browser.

Primary success and error feedback should become visible within 2 seconds during
local test usage.

## Website Demo Flow

1. Confirm the page shows a current-loans section. A fresh session should show
   an empty current-list message.
2. Create a loan with:

   ```text
   Loan ID: LN-001
   Borrower name: Jane Smith
   Funding amount: 1000.0
   Repayment amount: 1200.0
   ```

   Expected result: success message for `LN-001` and `LN-001` appears in the
   current loans list.

3. Try creating the same loan ID again.

   Expected result: duplicate-loan feedback, and the entered values remain
   visible for correction.

4. Search by borrower name `Jane Smith`.

   Expected result: borrower-name results include `LN-001`.

5. Search by borrower name `No Match`.

   Expected result: empty-result message, not an error.

6. Look up loan ID `LN-001`.

   Expected result: the page shows the loan details.

7. Look up loan ID `LN-MISSING`.

   Expected result: clear not-found feedback.

8. Delete loan ID `LN-001`.

   Expected result: success message identifies the deleted loan, and `LN-001`
   is removed from the current loan list.

9. Delete loan ID `LN-001` again.

   Expected result: clear not-found feedback and any remaining current loans are
   unchanged.

## Responsive Check

Resize the browser to a mobile-sized width or use browser responsive tools.

Expected result:

- Create, search, lookup, delete, and list controls remain readable.
- No primary workflow requires horizontal scrolling.
- Success and error messages remain visible and do not overlap controls.
- Primary action feedback remains visible within 2 seconds.

## Restart Behavior

Stop the Flask server with `Ctrl-C`, start it again, and refresh the website.

Expected result: current loans are gone because storage is in memory for the
running application session only. Lookup or deletion for old loan IDs returns
not-found feedback.

## Run Tests

```bash
pytest --cov=app --cov-report=term-missing --cov-fail-under=80
```

Expected result: tests pass and statement coverage is at least 80%.

## Scope Notes

- The website is a local single-page browser surface for the existing loan API.
- It covers create, list, borrower-name search, loan ID lookup, and loan
  deletion workflows.
- Auth0, durable persistence, public exposure, container registry work,
  Kubernetes, Helm, and cloud infrastructure are out of scope for this slice.
