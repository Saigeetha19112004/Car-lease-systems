# Car Lease System (MVP)

This repository contains a minimal MVP for a Car Lease system:
- Backend: FastAPI + SQLModel
- Frontend: Next.js (React)
- DB: PostgreSQL
- Local dev: Docker Compose
- CI: GitHub Actions (basic lint & tests)

Quick start (local):
- Copy `.env.example` to `.env` and update values
- Run: `docker-compose up --build`
- API accessible at `http://localhost:8000`
- Frontend accessible at `http://localhost:3000`

Notes:
- This is a starting point: auth, PayPal payment integration (MVP), and more features are included as stubs to be completed next.

Payments
- PayPal credentials are read from environment variables: `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET`, `PAYPAL_ENVIRONMENT` (sandbox or live). Follow PayPal docs to create sandbox/test credentials.
- Frontend (client) needs `NEXT_PUBLIC_PAYPAL_CLIENT_ID` set (sandbox or live) to render the PayPal JS SDK buttons. See `apps/web/.env.example`.

Quick test flow (local)
1. Start services: `docker-compose up --build`
2. Create a car via API (POST `/api/v1/cars`) or use DB directly
3. In browser visit `http://localhost:3000/cars` → choose a car → click "Get Quote"
4. Fill quote form (term/down payment) → click **Get Quote & Create Lease**
5. You will be redirected to `/checkout/{lease_id}` where PayPal buttons are rendered. Use Sandbox client-id to test Checkout flow.

E2E tests (Playwright)
- To run E2E tests locally:
  1. Start services with test endpoints enabled: `ENABLE_TEST_ENDPOINTS=1 docker-compose up --build`
  2. Install web deps: `cd apps/web && npm install`
  3. Run: `npm run test:e2e` from `apps/web` (this runs Playwright tests that seed an admin user and exercise admin flows + checkout).

Contracts
- Generate a contract for a lease: POST `/api/v1/contracts/{lease_id}/generate` → returns `contract_id` and local path (MVP stores PDF under `storage/contracts/`).
- Sign a contract: POST `/api/v1/contracts/{lease_id}/sign` with `{ signer_name, signer_email }` → updates contract status to signed and stores `signed_at` and signer metadata.
