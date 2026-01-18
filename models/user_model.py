from flask import current_app
from datetime import datetime

def create_user(data):
    bcrypt = current_app.bcrypt
    # Hashing password sebelum disimpan
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    
    user = {
        "username": data.get("username"),
        "email": data.get("email"),
        "password": hashed_password,
        "api_key": data.get("api_key", ""),
        "is_verified": data.get("is_verified", False),
        "oauth_provider": data.get("oauth_provider", None),
        "profile_picture": data.get("profile_picture", ""),
        "gender": data.get("gender", ""),
        "tanggal_lahir": data.get("tanggal_lahir", ""),
        "created_at": datetime.utcnow()
    }
    
    current_app.mongo.db.users.insert_one(user)
    return user

def find_user_by_email(email):
    return current_app.mongo.db.users.find_one({"email": email})

def update_user_password(email, new_password):
    bcrypt = current_app.bcrypt
    new_password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    
    current_app.mongo.db.users.update_one(
        {"email": email},
        {"$set": {"password": new_password_hash}}
    )