# API Notes

- The FastAPI app exposes OpenAPI at `/openapi.json` and the interactive docs at `/docs` (Swagger UI).
- An export script `scripts/export_openapi.py` writes the OpenAPI schema to `docs/openapi.json` for offline reference.
- Admin reporting endpoints: `GET /api/v1/admin/reports/summary` (admin-only) for counts of cars, leases, payments, users.
