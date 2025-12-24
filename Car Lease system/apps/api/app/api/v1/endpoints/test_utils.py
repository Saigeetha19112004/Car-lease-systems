import os
from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from ...db.session import engine
from ...models.models import User
from passlib.context import CryptContext
from jose import jwt
from ...core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

ENABLE = os.getenv('ENABLE_TEST_ENDPOINTS', '0') == '1'

@router.post('/seed-admin')
def seed_admin(payload: dict):
    if not ENABLE:
        raise HTTPException(status_code=404, detail='Not found')
    email = payload.get('email', 'admin@example.com')
    password = payload.get('password', 'password')
    with Session(engine) as session:
        existing = session.exec(select(User).where(User.email == email)).first()
        if existing:
            existing.role = 'admin'
            session.add(existing)
            session.commit()
            token = jwt.encode({'sub': str(existing.id)}, settings.secret_key, algorithm='HS256')
            return {'id': str(existing.id), 'access_token': token}
        user = User(email=email, password_hash=pwd_context.hash(password), full_name='Admin', role='admin')
        session.add(user)
        session.commit()
        session.refresh(user)
        token = jwt.encode({'sub': str(user.id)}, settings.secret_key, algorithm='HS256')
        return {'id': str(user.id), 'access_token': token}
