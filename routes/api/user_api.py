import os
import time
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models.user_model import get_user_by_id, update_user_profile

user_api_bp = Blueprint('user_api', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==========================================
# 1. ENDPOINT GET PROFILE USER
# ==========================================
@user_api_bp.route('/me', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        current_user_id = get_jwt_identity()
        user = get_user_by_id(current_user_id)
        
        if not user:
            return jsonify({"status": False, "msg": "User tidak ditemukan"}), 404
            
        db_profile_picture = user.get("profile_picture", "")
        full_profile_picture_url = ""

        if db_profile_picture:
            full_profile_picture_url = f"{request.host_url}{db_profile_picture}"

        return jsonify({
            "status": True,
            "msg": "Data profile berhasil diambil",
            "user": {
                "id": str(user["_id"]),
                "username": user["username"],
                "email": user["email"],
                "role": user.get("role", "users"),
                "profile_picture": full_profile_picture_url,
                "gender": user.get("gender", ""),
                "tanggal_lahir": user.get("tanggal_lahir", ""),
            }
        }), 200
    except Exception as e:
        return jsonify({"status": False, "msg": f"Server error: {str(e)}"}), 500


# ==========================================
# 2. ENDPOINT EDIT PROFILE USER (POST MULTIPART)
# ==========================================
@user_api_bp.route('/me', methods=['POST']) # Diubah ke POST agar sinkron dengan upload file Multipart
@jwt_required()
def edit_profile():
    try:
        current_user_id = get_jwt_identity()
        user = get_user_by_id(current_user_id)
        
        if not user:
            return jsonify({"status": False, "msg": "User tidak ditemukan"}), 404

        data_update = {}

        # 1. Ambil data teks menggunakan request.form (bukan request.get_json())
        if 'username' in request.form:
            data_update['username'] = request.form['username']
        if 'gender' in request.form:
            data_update['gender'] = request.form['gender']
        if 'tanggal_lahir' in request.form:
            data_update['tanggal_lahir'] = request.form['tanggal_lahir']
            
        # 2. Proses upload file fisik gambar jika ada
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            
            if file and file.filename != '':
                if allowed_file(file.filename):
                    # Ambil ekstensi aslinya
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    
                    # Buat nama unik pakai Timestamp Unix agar tidak kembar
                    timestamp = int(time.time())
                    unique_filename = f"user_{current_user_id}_{timestamp}.{ext}"
                    
                    # Tentukan folder tujuan di root project: static/img/users/
                    target_dir = os.path.join(current_app.root_path, 'static', 'img', 'users')
                    
                    # Bikin foldernya otomatis kalau belum ada
                    if not os.path.exists(target_dir):
                        os.makedirs(target_dir)
                    
                    # Simpan file secara fisik ke local storage server
                    file_path = os.path.join(target_dir, unique_filename)
                    file.save(file_path)
                    
                    # Simpan path relatif ke database MongoDB
                    data_update['profile_picture'] = f"static/img/users/{unique_filename}"
                else:
                    return jsonify({"status": False, "msg": "Ekstensi file tidak diizinkan! (Gunakan png, jpg, jpeg)"}), 400

        if not data_update:
            return jsonify({"status": False, "msg": "Tidak ada data profile yang diubah"}), 400

        # Jalankan update ke MongoDB
        update_user_profile(current_user_id, data_update)

        # Ambil data terbaru
        updated_user = get_user_by_id(current_user_id)
        
        updated_db_photo = updated_user.get("profile_picture", "")
        updated_full_photo_url = f"{request.host_url}{updated_db_photo}" if updated_db_photo else ""

        return jsonify({
            "status": True,
            "msg": "Profile berhasil diperbarui",
            "user": {
                "id": str(updated_user["_id"]),
                "username": updated_user["username"],
                "email": updated_user["email"],
                "role": updated_user.get("role", "users"),
                "profile_picture": updated_full_photo_url,
                "gender": updated_user.get("gender", ""),
                "tanggal_lahir": updated_user.get("tanggal_lahir", ""),
            }
        }), 200

    except Exception as e:
        return jsonify({"status": False, "msg": f"Server error: {str(e)}"}), 500