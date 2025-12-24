import os
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment, LiveEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest, OrdersCaptureRequest

PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET')
PAYPAL_ENV = os.getenv('PAYPAL_ENVIRONMENT', 'sandbox')

class PayPalClient:
    def __init__(self):
        if PAYPAL_ENV == 'live':
            environment = LiveEnvironment(client_id=PAYPAL_CLIENT_ID, client_secret=PAYPAL_CLIENT_SECRET)
        else:
            environment = SandboxEnvironment(client_id=PAYPAL_CLIENT_ID, client_secret=PAYPAL_CLIENT_SECRET)
        self.client = PayPalHttpClient(environment)

    def create_order(self, amount: str, currency: str = 'USD'):
        request = OrdersCreateRequest()
        request.prefer('return=representation')
        request.request_body({
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": currency,
                        "value": amount
                    }
                }
            ]
        })
        response = self.client.execute(request)
        return response.result

    def capture_order(self, order_id: str):
        request = OrdersCaptureRequest(order_id)
        request.prefer('return=representation')
        response = self.client.execute(request)
        return response.result

    def verify_webhook_signature(self, transmission_id: str, transmission_time: str, cert_url: str, auth_algo: str, transmission_sig: str, webhook_id: str, webhook_event: dict) -> bool:
        """Verify PayPal webhook signature using the PayPal /v1/notifications/verify-webhook-signature endpoint.
        Returns True if verification_status == 'SUCCESS'."""
        import httpx
        base = 'https://api.paypal.com' if PAYPAL_ENV == 'live' else 'https://api.sandbox.paypal.com'
        # Obtain access token
        token_res = httpx.post(f'{base}/v1/oauth2/token', auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET), data={'grant_type': 'client_credentials'})
        if token_res.status_code != 200:
            return False
        token = token_res.json().get('access_token')
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        payload = {
            'transmission_id': transmission_id,
            'transmission_time': transmission_time,
            'cert_url': cert_url,
            'auth_algo': auth_algo,
            'transmission_sig': transmission_sig,
            'webhook_id': webhook_id,
            'webhook_event': webhook_event
        }
        res = httpx.post(f'{base}/v1/notifications/verify-webhook-signature', json=payload, headers=headers)
        if res.status_code != 200:
            return False
        return res.json().get('verification_status') == 'SUCCESS'

paypal_client = PayPalClient()
