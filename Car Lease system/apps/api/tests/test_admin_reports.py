import os
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import engine
from sqlmodel import SQLModel, Session
from app.models.models import Car, Lease, Payment

client = TestClient(app)


def seed_admin_get_token():
    # uses test seed endpoint (enabled via env var in test env)
    r = client.post('/api/v1/test/seed_admin')
    assert r.status_code == 201
    data = r.json()
    return data['token']


def test_admin_reports_summary():
    token = seed_admin_get_token()
    # create a car
    headers = {'Authorization': f'Bearer {token}'}
    car_body = {
        'make': 'Test',
        'model': 'Reporter',
        'year': 2024,
        'base_price_per_month': 350.0,
    }
    r = client.post('/api/v1/cars', json=car_body, headers=headers)
    assert r.status_code == 201
    car = r.json()

    # create a lease for that car
    quote_body = {'car_id': car['id'], 'term_months': 36, 'annual_mileage': 12000}
    r = client.post('/api/v1/quotes', json=quote_body, headers=headers)
    assert r.status_code == 201
    quote = r.json()

    r = client.post('/api/v1/quotes/accept', json={'quote_id': quote['id']}, headers=headers)
    assert r.status_code == 201
    lease = r.json()

    # create a fake payment record
    payment_body = {'lease_id': lease['id'], 'amount': 1000.0, 'currency': 'USD', 'status': 'COMPLETED', 'provider': 'test'}
    r = client.post('/api/v1/payments', json=payment_body, headers=headers)
    assert r.status_code == 201

    # now fetch report
    r = client.get('/api/v1/admin/reports/summary', headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data['cars'] >= 1
    assert data['leases'] >= 1
    assert data['payments'] >= 1
    assert data['users'] >= 1
