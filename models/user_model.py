from flask import current_app
from datetime import datetime

def create_user(data):
    bcrypt = current_app.bcrypt
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    
    user = {
        "username": data["username"],
        "email": data["email"],
        "password": hashed_password,
        "api_key": data["api_key"],
        "is_verified": data.get("is_verified", False),
        "otp": data.get("otp"), # Simpan OTP 6 digit
        "otp_expiry": data.get("otp_expiry"), # Simpan waktu kadaluarsa
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

def update_verification_status(email):
    # Set verified jadi true dan hapus data OTP agar tidak bisa dipakai lagi
    return current_app.mongo.db.users.update_one(
        {"email": email},
        {"$set": {"is_verified": True}, "$unset": {"otp": "", "otp_expiry": ""}}
    )

def update_user_otp(email, otp, otp_expiry):
    """Memperbarui OTP dan waktu expiry untuk user tertentu."""
    return current_app.mongo.db.users.update_one(
        {"email": email},
        {"$set": {"otp": otp, "otp_expiry": otp_expiry}}
    )