from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ...services.payments import paypal_client
from ...db.session import engine
from ...models.models import Payment, Lease
from sqlmodel import Session, select

router = APIRouter()

class CreateOrderRequest(BaseModel):
    lease_id: str
    amount: float
    currency: str = 'USD'

@router.post('/create-order')
def create_order(req: CreateOrderRequest):
    # Create a PayPal order for the lease amount
    with Session(engine) as session:
        lease = session.get(Lease, req.lease_id)
        if not lease:
            raise HTTPException(status_code=404, detail='Lease not found')
        order = paypal_client.create_order(str(req.amount), req.currency)
        # create a Payment record with provider id = order.id and status pending
        payment = Payment(lease_id=req.lease_id, amount=req.amount, currency=req.currency, status='pending', provider_id=order.id)
        session.add(payment)
        session.commit()
        session.refresh(payment)
        return {'order_id': order.id, 'status': 'created', 'links': [l.__dict__ for l in order.links]}

class CaptureRequest(BaseModel):
    order_id: str

@router.post('/capture')
def capture_order(req: CaptureRequest):
    capture = paypal_client.capture_order(req.order_id)
    provider_id = req.order_id
    with Session(engine) as session:
        payment = session.exec(select(Payment).where(Payment.provider_id == provider_id)).first()
        if payment:
            payment.status = 'succeeded'
            session.add(payment)
            session.commit()
    return {'status': 'captured', 'capture': str(capture)}
