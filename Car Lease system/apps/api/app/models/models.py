from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
import uuid

class User(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    email: str
    password_hash: str
    full_name: Optional[str]
    role: str = 'customer'
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Car(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    vin: Optional[str]
    make: str
    model: str
    year: Optional[int]
    base_monthly_price: float
    status: str = 'available'
    mileage: Optional[int]
    available_from: Optional[datetime]
    available_to: Optional[datetime]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CarImage(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    car_id: uuid.UUID
    url: str
    is_primary: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Quote(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    user_id: uuid.UUID
    car_id: uuid.UUID
    term_months: int
    mileage_allowance: int
    monthly_payment: float
    upfront: float = 0
    taxes: float = 0
    fees: float = 0
    residual_value: Optional[float]
    status: str = 'draft'
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime]

class Lease(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    quote_id: uuid.UUID
    lease_number: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    status: str = 'pending'
    contract_url: Optional[str]
    monthly_payment: float
    total_amount: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Payment(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    lease_id: uuid.UUID
    amount: float
    currency: str = 'USD'
    status: str = 'pending'
    provider_id: Optional[str]
    payment_method: Optional[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ContractDocument(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    lease_id: uuid.UUID
    s3_url: str
    signed_at: Optional[datetime]
    signer: Optional[dict]
    status: str = 'generated'
    created_at: datetime = Field(default_factory=datetime.utcnow)
