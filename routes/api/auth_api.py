import secrets
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token
from models.user_model import create_user, find_user_by_email, update_user_otp, update_verification_status
from utils.email_utils import generate_otp, send_email_otp

auth_bp = Blueprint('auth_api', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    
    if find_user_by_email(email):
        return jsonify({"msg": "Email sudah terdaftar"}), 409

    # 1. Gunakan Utils untuk OTP
    otp = generate_otp()
    otp_expiry = datetime.utcnow() + timedelta(minutes=5) # Sesuaikan dengan template (5 menit)
    
    api_key = secrets.token_hex(16)
    data.update({
        'api_key': api_key,
        'otp': otp,
        'otp_expiry': otp_expiry,
        'is_verified': False
    })
    
    try:
        # 2. Kirim Email dulu via Utils
        send_email_otp(email, otp)
        
        # 3. Simpan ke Database
        create_user(data)
        
        return jsonify({"msg": "Registrasi sukses, silakan cek OTP di email Anda"}), 201
    except Exception as e:
        return jsonify({"msg": "Gagal registrasi", "error": str(e)}), 500

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    otp_input = data.get('otp')

    user = find_user_by_email(email)
    if not user:
        return jsonify({"msg": "User tidak ditemukan"}), 404

    # Validasi OTP dan Waktu Kadaluarsa
    if user.get('otp') == otp_input:
        if datetime.utcnow() < user.get('otp_expiry'):
            update_verification_status(email)
            return jsonify({"msg": "Akun berhasil diverifikasi!"}), 200
        else:
            return jsonify({"msg": "OTP sudah kadaluarsa"}), 400
    
    return jsonify({"msg": "Kode OTP salah"}), 400

@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"msg": "Email wajib diisi"}), 400

    user = find_user_by_email(email)

    # 1. Validasi keberadaan user
    if not user:
        return jsonify({"msg": "User tidak ditemukan"}), 404

    # 2. Jika sudah verifikasi, tidak perlu kirim OTP lagi
    if user.get('is_verified'):
        return jsonify({"msg": "Akun ini sudah terverifikasi"}), 400

    # 3. Generate OTP baru & Expiry baru (5 menit)
    new_otp = generate_otp()
    new_expiry = datetime.utcnow() + timedelta(minutes=5)

    try:
        # 4. Kirim email via utils
        send_email_otp(email, new_otp)

        # 5. Update di database
        update_user_otp(email, new_otp, new_expiry)

        return jsonify({"msg": "OTP baru telah dikirim ke email Anda"}), 200
    except Exception as e:
        return jsonify({"msg": "Gagal mengirim ulang OTP", "error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = find_user_by_email(email)

    if user and current_app.bcrypt.check_password_hash(user['password'], password):
        # Cek status verifikasi sebelum login
        if not user.get('is_verified', False):
            return jsonify({"msg": "Silakan verifikasi akun kamu via email"}), 403
            
        access_token = create_access_token(identity=str(user['_id']))
        return jsonify({
            "access_token": access_token,
            "user": {"email": user['email'], "username": user['username']}
        }), 200
    
    return jsonify({"msg": "Email atau password salah"}), 401