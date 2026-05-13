# Research: Loan Website

## Decision: Implement the website as one Flask-rendered page with static browser assets

**Rationale**: The feature asks for a single-page website, while the project
constitution requires Python, Flask, and Bootstrap and excludes extra frontend
frameworks unless justified. A Flask-rendered page with small static JavaScript
can provide the one-page browser experience, call the existing JSON endpoints,
and avoid a separate build system.

**Alternatives considered**:

- Angular single-page application. Rejected for this slice because Angular was
  optional in the source task and would introduce Node tooling, a second project,
  and build complexity that the constitution asks us to avoid unless necessary.
- Server-only multipage forms. Rejected because the requested experience is a
  single page that consumes the loan API and updates visible state without
  navigating between pages.

## Decision: Reuse existing same-origin loan API endpoints

**Rationale**: The current API already supports create, list, borrower-name
search, loan ID lookup, and deletion. The website can call those endpoints from
the same origin, preserving existing validation, duplicate, not-found,
runtime reset, and case-sensitive matching semantics.

**Alternatives considered**:

- Add website-specific form endpoints. Rejected because it duplicates API logic
  and risks divergent behaviour.
- Access the service directly from page routes. Rejected because the feature is
  specifically a website consuming the existing API.

## Decision: Use Bootstrap layout with compact operational workflows

**Rationale**: This is an operational loan-management tool, not a marketing
site. A compact responsive layout with forms, action buttons, status messages,
and scannable result sections matches the reviewer workflow and project
constitution.

**Alternatives considered**:

- Large landing-page hero. Rejected because users need immediate access to loan
  workflows.
- Decorative dashboard cards only. Rejected because repeated loan data and form
  actions need dense, predictable controls.

## Decision: Normalize user feedback into visible page states

**Rationale**: The API returns structured success and error payloads. The
website should map those into user-visible states: success, validation,
duplicate, not-found, empty result, and service unavailable. Form values should
remain available after failures so users can correct or retry.

**Alternatives considered**:

- Display raw JSON responses. Rejected because the website must provide a
  user-friendly workflow.
- Clear forms after every failed action. Rejected because it makes validation
  and retry paths slower and less usable.

## Decision: Keep testing within pytest and document browser validation

**Rationale**: The existing project quality gate uses pytest and statement
coverage. Tests can cover page rendering, expected controls, static assets,
existing API regressions, and documentation smoke checks. The quickstart will
also document desktop/mobile browser validation for responsive and visual states.

**Alternatives considered**:

- Add a browser automation dependency now. Rejected for this planning slice
  because it adds dependency and setup weight; if later implementation finds
  pure pytest insufficient for a critical behaviour, that must be justified in
  tasks or implementation notes.
- Manual validation only. Rejected because the constitution requires automated
  coverage for implemented behaviour and important error paths.
