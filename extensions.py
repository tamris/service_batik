from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt # Import library baru

# Inisialisasi tanpa 'app' dulu
mongo = PyMongo()
jwt = JWTManager()
bcrypt = Bcrypt() # Tambahkan ini