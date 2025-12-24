from app.services.payments import PayPalClient

class DummyClient:
    def __init__(self):
        pass

def test_paypal_client_init():
    # Ensure client initializes without raising when env missing (MVP tests simple)
    client = PayPalClient()
    assert hasattr(client, 'client')
