from fastapi.testclient import TestClient
from app.main import app
from app.db.session import engine
from app.models.models import Car, CarImage, User
from sqlmodel import Session, select
import io
from jose import jwt
from app.core.config import settings

client = TestClient(app)


def test_create_and_list_cars():
    with Session(engine) as session:
        car = Car(make='Toyota', model='Corolla', year=2020, base_monthly_price=199.99)
        session.add(car)
        session.commit()
        session.refresh(car)

    resp = client.get('/api/v1/cars?make=Toyota')
    assert resp.status_code == 200
    data = resp.json()
    assert any(c['make'] == 'Toyota' for c in data)


def test_admin_create_and_upload_image_to_car():
    # create admin user
    with Session(engine) as session:
        admin = User(email='admin@example.com', password_hash='x', role='admin')
        session.add(admin)
        session.commit()
        session.refresh(admin)

    token = jwt.encode({'sub': str(admin.id)}, settings.secret_key, algorithm='HS256')
    headers = {'Authorization': f'Bearer {token}'}

    # admin creates car
    resp = client.post('/api/v1/cars', json={'make':'Honda','model':'Accord','year':2022,'base_monthly_price':299.99}, headers=headers)
    assert resp.status_code == 200
    car = resp.json()

    # upload image as admin
    file_content = b"\x89PNG\r\n\x1a\n" + b"0"*100
    files = {'file': ('test.png', io.BytesIO(file_content), 'image/png')}
    resp2 = client.post(f"/api/v1/cars/{car['id']}/images", files=files, headers=headers)
    assert resp2.status_code == 200
    data = resp2.json()
    assert 'image_id' in data
    assert data['url'].startswith('/api/v1/media/images/')

    with Session(engine) as session:
        img = session.exec(select(CarImage).where(CarImage.car_id == car['id'])).first()
        assert img is not None

    # media endpoint should serve the image
    media_resp = client.get(data['url'])
    assert media_resp.status_code == 200
    assert media_resp.headers.get('content-type', '').startswith('image/')


def test_non_admin_cannot_create_car():
    # regular user
    with Session(engine) as session:
        user = User(email='user@example.com', password_hash='x', role='customer')
        session.add(user)
        session.commit()
        session.refresh(user)
    token = jwt.encode({'sub': str(user.id)}, settings.secret_key, algorithm='HS256')
    headers = {'Authorization': f'Bearer {token}'}

    resp = client.post('/api/v1/cars', json={'make':'Ford','model':'Focus','year':2019,'base_monthly_price':149.99}, headers=headers)
    assert resp.status_code == 403
