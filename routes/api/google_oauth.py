import os
import secrets
from flask import Blueprint, request, jsonify
from google.oauth2 import id_token
from google.auth.transport import requests
from flask_jwt_extended import create_access_token

from models.user_model import create_user, find_user_by_email

# Import fungsi database kamu (asumsi nama file/lokasi)
# dari database_helper import find_user_by_email, create_user 

google_oauth_bp = Blueprint('google_oauth', __name__)

# Mengambil Client ID dari environment variable
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')

@google_oauth_bp.route('/google', methods=['POST'])
def google_login():
    data = request.get_json()
    
    # Validasi body request
    if not data or 'id_token' not in data:
        return jsonify({"error": "Missing id_token"}), 400
        
    token = data.get('id_token')

    try:
        # 1. Verifikasi token ke server Google
        id_info = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            GOOGLE_CLIENT_ID
        )

        # 2. Ambil data user dari Google
        email = id_info.get('email')
        name = id_info.get('name')
        picture = id_info.get('picture')

        # 3. Logika Database (Check or Create User)
        user = find_user_by_email(email)

        if not user:
            # Buat user baru jika belum terdaftar
            user_data = {
                "username": name,
                "email": email,
                "password": secrets.token_hex(16), # Password random untuk OAuth
                "api_key": secrets.token_hex(16),
                "oauth_provider": "google",
                "is_verified": True,
                "profile_picture": picture
            }
            create_user(user_data)
            # Ambil data user yang baru dibuat untuk mendapatkan ID-nya
            user = find_user_by_email(email)

        # 4. Generate JWT Access Token
        # Pastikan user["_id"] dikonversi ke string untuk payload JWT
        access_token = create_access_token(identity=str(user["_id"]))

        return jsonify({
            "status": "success",
            "message": "Login successful",
            "access_token": access_token,
            "user": {
                "name": user.get("username"),
                "email": email,
                "api_key": user.get("api_key"),
                "photo": picture
            }
        }), 200

    except ValueError:
        # Token tidak valid atau expired
        return jsonify({"error": "Invalid Google token"}), 401
    except Exception as e:
        # Error lainnya (koneksi database, dll)
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500