import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret')
    MONGO_URI = os.getenv(
    'MONGO_URI',
    'mongodb+srv://sibatikgal_db_user:P8Szd2dydFmcKK8w@cluster0.0ootvqq.mongodb.net/sibatikgal?retryWrites=true&w=majority&appName=Cluster0')