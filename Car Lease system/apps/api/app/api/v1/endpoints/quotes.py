from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from typing import Optional
from ...db.session import engine
from ...models.models import Quote, Car
from ...services.quote import calculate_quote

router = APIRouter()

class QuoteCreate:
    car_id: str
    term_months: int
    mileage_allowance: int
    down_payment: Optional[float] = 0.0

@router.post("/", response_model=Quote)
def create_quote(payload: dict):
    car_id = payload.get('car_id')
    term = int(payload.get('term_months'))
    down = float(payload.get('down_payment',0))
    mileage = int(payload.get('mileage_allowance',10000))

    with Session(engine) as session:
        car = session.get(Car, car_id)
        if not car:
            raise HTTPException(status_code=404, detail='Car not found')
        monthly, breakdown, expires_at = calculate_quote(car.base_monthly_price, term, down)
        quote = Quote(user_id=payload.get('user_id'), car_id=car_id, term_months=term, mileage_allowance=mileage, monthly_payment=monthly, upfront=down, taxes=breakdown['taxes'], fees=breakdown['fees'], residual_value=breakdown['residual'], status='issued', expires_at=expires_at)
        session.add(quote)
        session.commit()
        session.refresh(quote)
        return quote

@router.get("/{quote_id}", response_model=Quote)
def get_quote(quote_id: str):
    with Session(engine) as session:
        quote = session.get(Quote, quote_id)
        if not quote:
            raise HTTPException(status_code=404, detail='Quote not found')
        return quote

@router.post("/{quote_id}/accept")
def accept_quote(quote_id: str):
    from ...models.models import Lease
    import uuid
    from datetime import datetime, timedelta

    with Session(engine) as session:
        quote = session.get(Quote, quote_id)
        if not quote:
            raise HTTPException(status_code=404, detail='Quote not found')
        if quote.status != 'issued':
            raise HTTPException(status_code=400, detail='Quote not available for acceptance')
        # create lease
        lease_number = f'LS-{str(uuid.uuid4())[:8]}'
        start = datetime.utcnow().date()
        end = start + timedelta(days=30*quote.term_months)
        total = quote.monthly_payment * quote.term_months + quote.upfront + quote.taxes + quote.fees
        lease = Lease(quote_id=quote.id, lease_number=lease_number, start_date=start, end_date=end, status='active', monthly_payment=quote.monthly_payment, total_amount=total)
        session.add(lease)
        quote.status = 'accepted'
        session.add(quote)
        session.commit()
        session.refresh(lease)
        return {'lease_id': lease.id, 'lease_number': lease.lease_number}
