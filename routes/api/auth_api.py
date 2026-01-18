from flask import Blueprint, request, jsonify
from extensions import mongo, bcrypt # Ambil bcrypt dari extensions
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth_api', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"msg": "Email dan password wajib diisi"}), 400

    # Cari user berdasarkan email
    user = mongo.db.users.find_one({"email": email})

    # Verifikasi password menggunakan bcrypt
    if user and bcrypt.check_password_hash(user['password'], password):
        # Buat token JWT menggunakan SECRET_KEY yang ada di config
        access_token = create_access_token(identity=str(user['_id']))
        
        return jsonify({
            "msg": "Login berhasil",
            "access_token": access_token,
            "user": {
                "email": user['email'],
                "username": user.get('username')
            }
        }), 200
    
    return jsonify({"msg": "Email atau password salah"}), 401
