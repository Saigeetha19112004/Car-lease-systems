from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from ...db.session import engine
from ...models.models import Car, Lease, Payment, User
from ...dependencies import admin_required

router = APIRouter()

@router.get('/reports/summary')
def reports_summary(user=Depends(admin_required)):
    with Session(engine) as session:
        cars_count = session.exec(select(Car)).count()
        leases_count = session.exec(select(Lease)).count()
        payments_count = session.exec(select(Payment)).count()
        users_count = session.exec(select(User)).count()
        return {'cars': cars_count, 'leases': leases_count, 'payments': payments_count, 'users': users_count}
