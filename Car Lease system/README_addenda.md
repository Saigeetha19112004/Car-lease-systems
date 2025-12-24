New additions (completed)

- Admin reporting: `GET /api/v1/admin/reports/summary` (admin-only) and admin UI at `/admin/reports` showing counts for cars, leases, payments, and users.
- OpenAPI export: `scripts/export_openapi.py` writes `docs/openapi.json` for offline use.
- Sentry (optional): Backend reads `SENTRY_DSN`, frontend reads `NEXT_PUBLIC_SENTRY_DSN`.
- CI: Playwright E2E job: `.github/workflows/e2e.yml` runs Playwright tests in CI using docker-compose.
- Deployment template: `.github/workflows/deploy.yml` provides a build-and-push template for GHCR.
- Docs: `docs/architecture.md`, `docs/deployment.md`, `docs/api.md` added.

If you want, I can also wire up production-ready deployment (Terraform/Helm) and migrate storage to S3 next. Let me know your preferred cloud provider.
