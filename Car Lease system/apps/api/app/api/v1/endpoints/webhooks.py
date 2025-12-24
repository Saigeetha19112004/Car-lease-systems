from fastapi import APIRouter, Request, HTTPException
from sqlmodel import Session, select
from ...db.session import engine
from ...models.models import Payment
from ...services.payments import paypal_client
import os

router = APIRouter()

@router.post("/paypal")
async def paypal_webhook(request: Request):
    # Verify webhook signature first
    headers = request.headers
    transmission_id = headers.get('paypal-transmission-id')
    transmission_time = headers.get('paypal-transmission-time')
    cert_url = headers.get('paypal-cert-url')
    auth_algo = headers.get('paypal-auth-algo')
    transmission_sig = headers.get('paypal-transmission-sig')
    webhook_id = os.getenv('PAYPAL_WEBHOOK_ID')

    body = await request.json()

    verified = paypal_client.verify_webhook_signature(
        transmission_id, transmission_time, cert_url, auth_algo, transmission_sig, webhook_id, body
    )

    if not verified:
        raise HTTPException(status_code=400, detail='Invalid webhook signature')

    event_type = body.get('event_type')

    # handle capture completed
    if event_type == 'PAYMENT.CAPTURE.COMPLETED':
        resource = body.get('resource', {})
        provider_id = resource.get('id')
        # Update payment record by provider_id
        with Session(engine) as session:
            payment = session.exec(select(Payment).where(Payment.provider_id == provider_id)).first()
            if payment:
                payment.status = 'succeeded'
                session.add(payment)
                session.commit()
        return {'status': 'processed'}

    # fallback
    return {'received': True}
