from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail # Tambahkan ini

mongo = PyMongo()
jwt = JWTManager()
bcrypt = Bcrypt()
mail = Mail() # Tambahkan ini