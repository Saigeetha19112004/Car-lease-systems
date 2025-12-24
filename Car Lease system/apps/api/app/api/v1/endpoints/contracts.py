from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from ...db.session import engine
from ...models.models import Lease, ContractDocument
from ...services.contracts import generate_contract_pdf, sign_contract
from pydantic import BaseModel

router = APIRouter()

@router.post("/{lease_id}/generate")
def generate(lease_id: str):
    with Session(engine) as session:
        lease = session.get(Lease, lease_id)
        if not lease:
            raise HTTPException(status_code=404, detail='Lease not found')
        path, doc = generate_contract_pdf(lease)
        return {'contract_id': doc.id, 'path': path, 'status': doc.status}

class SignRequest(BaseModel):
    signer_name: str
    signer_email: str

@router.post("/{lease_id}/sign")
def sign(lease_id: str, payload: SignRequest):
    signer = {'name': payload.signer_name, 'email': payload.signer_email}
    doc = sign_contract(lease_id, signer)
    if not doc:
        raise HTTPException(status_code=404, detail='Contract not found')
    return {'contract_id': doc.id, 'status': doc.status, 'signed_at': doc.signed_at}

@router.get("/{lease_id}")
def get_contract(lease_id: str):
    with Session(engine) as session:
        doc = session.exec(select(ContractDocument).where(ContractDocument.lease_id == lease_id)).first()
        if not doc:
            raise HTTPException(status_code=404, detail='Contract not found')
        return {'contract_id': doc.id, 'path': doc.s3_url, 'status': doc.status, 'signed_at': doc.signed_at}
