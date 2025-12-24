# Changelog

## [Unreleased]
- Add admin reporting endpoint and admin dashboard page (`/admin/reports`).
- Add OpenAPI export script: `scripts/export_openapi.py` → `docs/openapi.json`.
- Add optional Sentry integration for backend and frontend (via env vars).
- Add Playwright E2E CI workflow (`.github/workflows/e2e.yml`).
- Add deployment template workflow (`.github/workflows/deploy.yml`).
- Add docs for architecture and deployment (`docs/*.md`).
- Update test suite with `tests/test_admin_reports.py` and E2E test coverage for reports.
