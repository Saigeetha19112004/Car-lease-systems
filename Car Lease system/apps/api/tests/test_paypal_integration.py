import respx
import httpx
from fastapi.testclient import TestClient
from app.main import app
from app.services.payments import paypal_client
from app.db.session import engine
from app.models.models import Lease, Payment
from sqlmodel import Session, select
from unittest.mock import patch

client = TestClient(app)


def test_create_order_creates_payment():
    with Session(engine) as session:
        lease = Lease(quote_id='00000000-0000-0000-0000-000000000001', lease_number='LS-INT-1', monthly_payment=100, total_amount=100)
        session.add(lease)
        session.commit()
        session.refresh(lease)

    DummyOrder = type('Order', (), {'id': 'ORDER-1', 'links': []})
    with patch.object(paypal_client, 'create_order', return_value=DummyOrder()):
        resp = client.post('/api/v1/payments/create-order', json={'lease_id': str(lease.id), 'amount': 100.0, 'currency': 'USD'})
        assert resp.status_code == 200
        data = resp.json()
        assert data['order_id'] == 'ORDER-1'

    with Session(engine) as session:
        p = session.exec(select(Payment).where(Payment.provider_id == 'ORDER-1')).first()
        assert p is not None and p.status == 'pending'


def test_capture_updates_payment():
    with Session(engine) as session:
        lease = Lease(quote_id='00000000-0000-0000-0000-000000000002', lease_number='LS-INT-2', monthly_payment=50, total_amount=1800)
        session.add(lease)
        session.commit()
        session.refresh(lease)
        payment = Payment(lease_id=lease.id, amount=50.0, currency='USD', status='pending', provider_id='ORDER-2')
        session.add(payment)
        session.commit()
        session.refresh(payment)

    with patch.object(paypal_client, 'capture_order', return_value={'id': 'ORDER-2'}):
        resp = client.post('/api/v1/payments/capture', json={'order_id': 'ORDER-2'})
        assert resp.status_code == 200

    with Session(engine) as session:
        p = session.exec(select(Payment).where(Payment.provider_id == 'ORDER-2')).first()
        assert p.status == 'succeeded'


@respx.mock
def test_verify_webhook_signature_respx():
    # Mock PayPal token and verification endpoints
    base = 'https://api.sandbox.paypal.com'
    respx.post(f'{base}/v1/oauth2/token').respond(200, json={'access_token': 'TEST_TOKEN'})
    respx.post(f'{base}/v1/notifications/verify-webhook-signature').respond(200, json={'verification_status': 'SUCCESS'})

    with Session(engine) as session:
        lease = Lease(quote_id='00000000-0000-0000-0000-000000000003', lease_number='LS-INT-3', monthly_payment=200, total_amount=7200)
        session.add(lease)
        session.commit()
        session.refresh(lease)
        payment = Payment(lease_id=lease.id, amount=200.0, currency='USD', status='pending', provider_id='PAYID-WEB')
        session.add(payment)
        session.commit()
        session.refresh(payment)

    headers = {
        'paypal-transmission-id': 'TID',
        'paypal-transmission-time': 'TIME',
        'paypal-cert-url': 'https://example.com/cert',
        'paypal-auth-algo': 'SHA256',
        'paypal-transmission-sig': 'SIG'
    }

    payload = {
        'event_type': 'PAYMENT.CAPTURE.COMPLETED',
        'resource': {
            'id': 'PAYID-WEB'
        }
    }

    resp = client.post('/api/v1/webhooks/paypal', json=payload, headers=headers)
    assert resp.status_code == 200
    assert resp.json().get('status') == 'processed'

    with Session(engine) as session:
        p = session.exec(select(Payment).where(Payment.provider_id == 'PAYID-WEB')).first()
        assert p.status == 'succeeded'
