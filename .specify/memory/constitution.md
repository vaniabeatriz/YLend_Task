<!--
Sync Impact Report
Version change: unversioned template -> 1.0.0
Modified principles:
- Placeholder principles -> I. Simplicity and Demonstrable Scope
- Placeholder principles -> II. Python, Flask, and Bootstrap Only
- Placeholder principles -> III. Test Coverage as a Delivery Gate
- Placeholder principles -> IV. Clear and Concise Documentation
- Placeholder principles -> V. Explainable Design Decisions
Added sections:
- Technical Constraints
- Development Workflow and Quality Gates
Removed sections:
- Placeholder template guidance comments
Templates requiring updates:
- ✅ updated: .specify/templates/plan-template.md
- ✅ updated: .specify/templates/spec-template.md
- ✅ updated: .specify/templates/tasks-template.md
- ✅ reviewed, not present: .specify/templates/commands/*.md
- ✅ reviewed, no change required: AGENTS.md
Follow-up TODOs:
- None
-->
# YL Technical Test Constitution

## Core Principles

### I. Simplicity and Demonstrable Scope
Every feature MUST be small enough to explain, run, and defend within a
40-minute technical-test discussion. The implementation MUST choose the simplest
design that satisfies the stated requirements. Extra abstractions, frameworks,
services, background jobs, build steps, or data stores MUST be excluded unless
the plan records a concrete requirement that makes them necessary.

Rationale: the primary goal is to demonstrate sound engineering judgement under
time constraints, not to maximise architecture.

### II. Python, Flask, and Bootstrap Only
Application code MUST use Python and Flask for server-side behaviour and
Bootstrap for UI styling. Server-rendered Flask templates are the default UI
approach. Additional frontend frameworks, API layers, task queues, or persistent
services MUST NOT be introduced without an explicit complexity justification in
the implementation plan.

Rationale: a narrow stack keeps the project easy to review, run, test, and
explain.

### III. Test Coverage as a Delivery Gate
Automated tests MUST be included for all implemented user-facing behaviour and
important error paths. The test suite MUST run with pytest and enforce at least
80% statement coverage before delivery. Any uncovered behaviour that affects the
demo path MUST be documented as a known gap before work is considered complete.

Rationale: coverage gives a measurable quality gate while keeping the test
expectation realistic for a technical test.

### IV. Clear and Concise Documentation
Documentation MUST explain how to install, configure, run, test, and demo the
project using concise, task-focused language. The README or quickstart MUST be
kept current with the implemented behaviour. Documentation MUST avoid long
background essays and MUST prioritise commands, assumptions, and verification
steps.

Rationale: reviewers need to understand and validate the project quickly.

### V. Explainable Design Decisions
The implementation plan MUST record any non-obvious technical decision,
trade-off, or rejected simpler option. Code MUST favour explicit names and
straight-line control flow. Comments SHOULD be used only where they clarify a
decision or edge case that is not obvious from the code.

Rationale: the final solution must be easy to walk through and defend in a short
interview-style setting.

## Technical Constraints

- Runtime: Python with Flask.
- UI: Bootstrap with Flask templates unless the plan justifies otherwise.
- Testing: pytest with coverage enforcement at 80% minimum.
- Project shape: keep a single small application unless a requirement demands a
  split. Prefer `app/`, `tests/`, and concise documentation at the repository
  root or under `docs/`.
- Dependencies: every new dependency MUST be justified by a direct requirement
  or a clear reduction in code complexity.
- Data storage: prefer simple in-memory, file-based, or SQLite storage for the
  test unless persistence requirements demand more.

## Development Workflow and Quality Gates

- Specifications MUST define independently testable user stories and measurable
  success criteria.
- Plans MUST pass the Constitution Check before research or design proceeds.
- Tasks MUST include setup, implementation, tests, documentation, and final
  verification work needed to satisfy this constitution.
- Before delivery, the project MUST provide a documented command to run tests
  with coverage and MUST show coverage at or above 80%.
- Before delivery, the project MUST provide a documented command to run the
  Flask application locally and a concise demo path for the main user journey.
- Any violation of these gates MUST be recorded in Complexity Tracking with the
  simpler alternative that was rejected.

## Governance

This constitution supersedes conflicting local conventions for this technical
test. Amendments MUST be made by editing this file and synchronising affected
Spec Kit templates in the same change.

Versioning follows semantic versioning:

- MAJOR: removes or redefines a core principle or weakens a delivery gate.
- MINOR: adds a new principle, section, or materially expands required practice.
- PATCH: clarifies wording without changing obligations.

Compliance review is required during planning, task generation, and final
delivery. Reviewers MUST verify stack discipline, simplicity, documentation
quality, and the 80% coverage gate before accepting the work.

**Version**: 1.0.0 | **Ratified**: 2026-05-09 | **Last Amended**: 2026-05-09
