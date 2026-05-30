import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    MONGO_URI = os.getenv('MONGO_URI')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

    # JWT Expired Time
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

    # Validasi
    if not SECRET_KEY or not JWT_SECRET_KEY:
        raise ValueError(
            "SECRET_KEY dan JWT_SECRET_KEY harus di-set di file .env!"
        )

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME')
    MAIL_FROM_NAME = os.getenv('MAIL_NAME')