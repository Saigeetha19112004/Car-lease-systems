import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str = os.getenv('DATABASE_URL')
    redis_url: str = os.getenv('REDIS_URL')
    secret_key: str = os.getenv('SECRET_KEY', 'supersecret')

settings = Settings()
