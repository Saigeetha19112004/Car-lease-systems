from fastapi.testclient import TestClient
from app.main import app
from app.services.payments import paypal_client
from app.db.session import engine
from app.models.models import Payment, Lease
from sqlmodel import Session, select
from unittest.mock import patch

client = TestClient(app)

def test_paypal_webhook_verification_and_processing(monkeypatch):
    # Create a payment record that the webhook should update
    with Session(engine) as session:
        lease = Lease(quote_id='00000000-0000-0000-0000-000000000000', lease_number='LS-TEST', monthly_payment=100, total_amount=3600)
        session.add(lease)
        session.commit()
        session.refresh(lease)
        payment = Payment(lease_id=lease.id, amount=100.0, currency='USD', status='pending', provider_id='PAYID-TEST')
        session.add(payment)
        session.commit()
        session.refresh(payment)

    # Mock verification to return True
    with patch.object(paypal_client, 'verify_webhook_signature', return_value=True) as mock_verify:
        payload = {
            'event_type': 'PAYMENT.CAPTURE.COMPLETED',
            'resource': {
                'id': 'PAYID-TEST'
            }
        }
        headers = {
            'paypal-transmission-id': 'TID',
            'paypal-transmission-time': 'TIME',
            'paypal-cert-url': 'https://example.com/cert',
            'paypal-auth-algo': 'SHA256',
            'paypal-transmission-sig': 'SIG'
        }
        resp = client.post('/api/v1/webhooks/paypal', json=payload, headers=headers)
        assert resp.status_code == 200
        assert resp.json().get('status') == 'processed'

    # Confirm payment updated
    with Session(engine) as session:
        p = session.exec(select(Payment).where(Payment.provider_id == 'PAYID-TEST')).first()
        assert p.status == 'succeeded'
