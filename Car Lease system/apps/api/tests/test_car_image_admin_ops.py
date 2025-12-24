from fastapi.testclient import TestClient
from app.main import app
from app.db.session import engine
from app.models.models import Car, CarImage, User
from sqlmodel import Session, select
import io
from jose import jwt
from app.core.config import settings

client = TestClient(app)


def test_set_primary_and_delete_image():
    with Session(engine) as session:
        admin = User(email='admin2@example.com', password_hash='x', role='admin')
        session.add(admin)
        session.commit()
        session.refresh(admin)

    token = jwt.encode({'sub': str(admin.id)}, settings.secret_key, algorithm='HS256')
    headers = {'Authorization': f'Bearer {token}'}

    # create car
    resp = client.post('/api/v1/cars', json={'make':'BMW','model':'X3','year':2022,'base_monthly_price':499.99}, headers=headers)
    assert resp.status_code == 200
    car = resp.json()

    # upload two images
    file_content = b"\x89PNG\r\n\x1a\n" + b"0"*100
    files = {'file': ('one.png', io.BytesIO(file_content), 'image/png')}
    r1 = client.post(f"/api/v1/cars/{car['id']}/images", files=files, headers=headers)
    assert r1.status_code == 200
    img1 = r1.json()

    files2 = {'file': ('two.png', io.BytesIO(file_content), 'image/png')}
    r2 = client.post(f"/api/v1/cars/{car['id']}/images", files=files2, headers=headers)
    assert r2.status_code == 200
    img2 = r2.json()

    # set primary to second image
    set_resp = client.post(f"/api/v1/cars/{car['id']}/images/{img2['image_id']}/set-primary", headers=headers)
    assert set_resp.status_code == 200
    assert set_resp.json()['is_primary'] is True

    # verify in DB
    with Session(engine) as session:
        imgs = session.exec(select(CarImage).where(CarImage.car_id == car['id'])).all()
        assert any(i.is_primary for i in imgs)

    # delete first image
    del_resp = client.delete(f"/api/v1/cars/{car['id']}/images/{img1['image_id']}", headers=headers)
    assert del_resp.status_code == 200
    assert del_resp.json().get('deleted') is True

    with Session(engine) as session:
        remaining = session.exec(select(CarImage).where(CarImage.car_id == car['id'])).all()
        assert len(remaining) == 1
        assert str(remaining[0].id) == img2['image_id']
