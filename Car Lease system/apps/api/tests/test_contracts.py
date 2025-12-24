from fastapi.testclient import TestClient
from app.main import app
from app.db.session import engine
from app.models.models import Lease, ContractDocument
from sqlmodel import Session, select

client = TestClient(app)


def test_generate_and_sign_contract():
    with Session(engine) as session:
        lease = Lease(quote_id='00000000-0000-0000-0000-000000000010', lease_number='LS-CON-1', monthly_payment=150, total_amount=5400)
        session.add(lease)
        session.commit()
        session.refresh(lease)

    resp = client.post(f'/api/v1/contracts/{lease.id}/generate')
    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] == 'generated'

    # sign
    sign_resp = client.post(f'/api/v1/contracts/{lease.id}/sign', json={'signer_name': 'Test User', 'signer_email': 'test@example.com'})
    assert sign_resp.status_code == 200
    sign_data = sign_resp.json()
    assert sign_data['status'] == 'signed'

    with Session(engine) as session:
        doc = session.exec(select(ContractDocument).where(ContractDocument.lease_id == lease.id)).first()
        assert doc is not None
        assert doc.status == 'signed'
        assert doc.signer['name'] == 'Test User'
