from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from flask import current_app
from models.user_model import create_user, find_user_by_email

auth_bp = Blueprint('auth_api', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if find_user_by_email(data.get('email')):
        return jsonify({"msg": "Email sudah terdaftar"}), 409
    
    try:
        # Menambahkan field default yang dibutuhkan model jika belum ada
        data.setdefault('api_key', 'some-random-api-key') 
        create_user(data)
        return jsonify({"msg": "User berhasil dibuat"}), 201
    except Exception as e:
        return jsonify({"msg": "Gagal registrasi", "error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = find_user_by_email(email)

    if user and current_app.bcrypt.check_password_hash(user['password'], password):
        access_token = create_access_token(identity=str(user['_id']))
        return jsonify({
            "access_token": access_token,
            "user": {
                "email": user['email'],
                "username": user['username'],
            }
        }), 200
    
    return jsonify({"msg": "Email atau password salah"}), 401