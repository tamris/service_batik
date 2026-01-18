import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables dari .env


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    MONGO_URI = os.getenv('MONGO_URI')
    
    # Validasi: pastikan keys tidak kosong
    if not SECRET_KEY or not JWT_SECRET_KEY:
        raise ValueError("SECRET_KEY dan JWT_SECRET_KEY harus di-set di file .env!")