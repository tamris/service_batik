from bson import ObjectId
from flask import current_app
from datetime import datetime

def create_user(data):
    bcrypt = current_app.bcrypt
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    
    user = {
        "username": data["username"],
        "email": data["email"],
        "password": hashed_password,
        "role": data.get("role", "users"),
        "api_key": data["api_key"],
        "is_verified": data.get("is_verified", False),
        "otp": data.get("otp"), # Simpan OTP 6 digit
        "otp_expiry": data.get("otp_expiry"), # Simpan waktu kadaluarsa
        "oauth_provider": data.get("oauth_provider", None),
        "profile_picture": data.get("profile_picture", ""),
        "gender": data.get("gender", ""),
        "tanggal_lahir": data.get("tanggal_lahir", ""),
        "created_at": datetime.now()
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

def update_user_password(email, new_password):
    """Menyimpan password baru yang sudah di-hash"""
    bcrypt = current_app.bcrypt
    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    
    # Update password dan hapus OTP agar tidak bisa dipakai lagi
    return current_app.mongo.db.users.update_one(
        {"email": email},
        {"$set": {"password": hashed_password}, "$unset": {"otp": "", "otp_expiry": ""}}
    )


def get_all_users(search_query=""):
    query = {}
    if search_query:
        query = {
            "$or": [
                {"username": {"$regex": search_query, "$options": "i"}},
                {"email": {"$regex": search_query, "$options": "i"}},
                {"role": {"$regex": search_query, "$options": "i"}}
            ]
        }
    
    # Ambil data dari MongoDB
    users = list(current_app.mongo.db.users.find(query).sort("created_at", -1))
    
    # KUNCI UTAMA: Urutkan data berdasarkan Role (Superadmin = 0, Admin = 1, User = 2)
    role_priority = {'superadmin': 0, 'admin': 1, 'users': 2}
    users.sort(key=lambda x: role_priority.get(x.get('role', 'users'), 3))
    
    return users

def get_user_by_id(user_id):
    return current_app.mongo.db.users.find_one({"_id": ObjectId(user_id)})

def update_admin(user_id, data_update):
    # Jika admin isi password baru di form edit, kita hash dulu
    if 'password' in data_update and data_update['password']:
        bcrypt = current_app.bcrypt
        data_update['password'] = bcrypt.generate_password_hash(data_update['password']).decode('utf-8')
        
    return current_app.mongo.db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": data_update}
    )

def update_user_profile(user_id, data_update):
    """Mengupdate data profile user berdasarkan ObjectId."""
    return current_app.mongo.db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": data_update}
    )

def toggle_like_batik(user_id, batik_id):
    user_ref = current_app.mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if not user_ref:
        return None
        
    saved_items = user_ref.get("saved_items", [])
    batik_obj_id = ObjectId(batik_id)
    
    if batik_obj_id in saved_items:
        # PULL: Hapus dari list jika sudah disukai (Unlike)
        current_app.mongo.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$pull": {"saved_items": batik_obj_id}}
        )
        return "unliked"
    else:
        # ADD TO SET: Tambahkan ke list secara unik jika belum disukai (Like)
        current_app.mongo.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$addToSet": {"saved_items": batik_obj_id}}
        )
        return "liked"
    
def get_user_saved_items(user_id):
    pipeline = [
        {"$match": {"_id": ObjectId(user_id)}},
        {
            "$lookup": {
                "from": "batiks", # <--- SINKRON: Menggunakan nama koleksi batiks milikmu
                "localField": "saved_items",
                "foreignField": "_id",
                "as": "liked_batiks"
            }
        },
        {"$project": {"liked_batiks": 1, "_id": 0}}
    ]
    
    result = list(current_app.mongo.db.users.aggregate(pipeline))
    if result and "liked_batiks" in result[0]:
        return result[0]["liked_batiks"]
    return []