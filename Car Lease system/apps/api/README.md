# API (FastAPI) - Car Lease System

Dev:
- Copy `.env.example` to `.env`
- Run `docker-compose up --build`
- API docs: `http://localhost:8000/docs`

Notes:
- This scaffold uses SQLModel; in production, use migrations (Alembic) and secure secrets.

Payments (PayPal)
- Set `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET`, and `PAYPAL_ENVIRONMENT` in `.env` to allow creating / capturing orders and handling webhooks.
- Webhook endpoint: POST `/api/v1/webhooks/paypal` (basic handler included; validate signatures in production).
