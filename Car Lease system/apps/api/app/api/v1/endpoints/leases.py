from fastapi import APIRouter, HTTPException
from sqlmodel import Session
from ...db.session import engine
from ...models.models import Lease

router = APIRouter()

@router.get("/{lease_id}")
def get_lease(lease_id: str):
    with Session(engine) as session:
        lease = session.get(Lease, lease_id)
        if not lease:
            raise HTTPException(status_code=404, detail='Lease not found')
        return lease
