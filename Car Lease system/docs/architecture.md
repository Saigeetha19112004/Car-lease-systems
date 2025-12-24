# Architecture Overview

- Backend: FastAPI + SQLModel (PostgreSQL)
- Frontend: Next.js (React)
- Payments: PayPal Checkout (server-side create/capture + webhook verification)
- Storage: Local file storage for images & contracts (MVP), recommended migration to S3 for production
- Testing: pytest (unit/integration), respx for HTTP mocking, Playwright for E2E
- CI: GitHub Actions (unit tests + Playwright E2E workflow)
- Monitoring: Sentry integration optional via env var (SENTRY_DSN / NEXT_PUBLIC_SENTRY_DSN)
