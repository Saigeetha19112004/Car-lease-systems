import os
from sqlmodel import create_engine, SQLModel

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgres:postgres@localhost:5432/car_lease')

# For SQLModel sync engine (simple dev); replace with async as needed
engine = create_engine(DATABASE_URL, echo=True)
