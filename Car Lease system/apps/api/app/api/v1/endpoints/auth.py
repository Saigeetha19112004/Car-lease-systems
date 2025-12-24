from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from passlib.context import CryptContext
from jose import jwt
import os
from ...db.session import engine
from ...models.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv('SECRET_KEY', 'supersecret')

router = APIRouter()

@router.post('/register')
def register(payload: dict):
    email = payload.get('email')
    password = payload.get('password')
    full_name = payload.get('full_name')
    if not email or not password:
        raise HTTPException(status_code=400, detail='email and password required')

    with Session(engine) as session:
        existing = session.exec(select(User).where(User.email == email)).first()
        if existing:
            raise HTTPException(status_code=400, detail='User exists')
        user = User(email=email, password_hash=pwd_context.hash(password), full_name=full_name)
        session.add(user)
        session.commit()
        session.refresh(user)
        token = jwt.encode({'sub': str(user.id)}, SECRET_KEY, algorithm='HS256')
        return {'user': {'id': user.id, 'email': user.email, 'full_name': user.full_name}, 'access_token': token}

@router.post('/login')
def login(payload: dict):
    email = payload.get('email')
    password = payload.get('password')
    if not email or not password:
        raise HTTPException(status_code=400, detail='email and password required')
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        if not user or not pwd_context.verify(password, user.password_hash):
            raise HTTPException(status_code=401, detail='Invalid credentials')
        token = jwt.encode({'sub': str(user.id)}, SECRET_KEY, algorithm='HS256')
        return {'access_token': token}
