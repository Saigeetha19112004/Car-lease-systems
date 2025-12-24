import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from .db.session import engine

# Optional: initialize Sentry if configured
sentry_dsn = os.getenv('SENTRY_DSN')
if sentry_dsn:
    try:
        import sentry_sdk
        sentry_sdk.init(dsn=sentry_dsn)
    except Exception:
        # don't fail startup if sentry lib missing
        pass

from .api.v1.endpoints import auth, cars, quotes, leases, webhooks

app = FastAPI(title="Car Lease System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    # Create tables if they don't exist (for dev/demo)
    SQLModel.metadata.create_all(engine)

# include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"]) 
app.include_router(cars.router, prefix="/api/v1/cars", tags=["cars"]) 
# Media endpoints
from .api.v1.endpoints import media
app.include_router(media.router, prefix="/api/v1/media", tags=['media'])

# Test-only endpoints (enabled by env var ENABLE_TEST_ENDPOINTS=1)
import os
if os.getenv('ENABLE_TEST_ENDPOINTS','0') == '1':
    from .api.v1.endpoints import test_utils
    app.include_router(test_utils.router, prefix="/api/v1/test", tags=['test-utils'])
app.include_router(quotes.router, prefix="/api/v1/quotes", tags=["quotes"])
app.include_router(leases.router, prefix="/api/v1/leases", tags=["leases"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["webhooks"]) 
from .api.v1.endpoints import payments
app.include_router(payments.router, prefix="/api/v1/payments", tags=['payments'])
from .api.v1.endpoints import contracts
app.include_router(contracts.router, prefix="/api/v1/contracts", tags=['contracts'])
# Admin reporting endpoints
from .api.v1.endpoints import admin
app.include_router(admin.router, prefix="/api/v1/admin", tags=['admin'])
