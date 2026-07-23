from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
from models.batik_model import BatikModel
from extensions import mongo
import math

galeri_api_bp = Blueprint('galeri_api', __name__)
batik_model = BatikModel()

@galeri_api_bp.route('/galeri', methods=['GET'])
@jwt_required(optional=True)
def get_all_batik():
    try:
        # Ambil identitas token di paling atas agar bisa di-print dengan aman
        current_user_id = get_jwt_identity()

        # print("\n=== DEBUG ENDPOINT GALERI ===")
        # print(f"Token Terdeteksi (User ID): {current_user_id}")

        # 1. Parameter Pagination & Pencarian
        page = request.args.get('page', 1, type=int)
        search_query = request.args.get('q', '')
        per_page = 20

        # 2. Ambil data dari MongoDB
        all_data = batik_model.get_all(search_query)

        # 3. Logika Pagination
        total_items = len(all_data)
        total_pages = math.ceil(total_items / per_page)
        
        start = (page - 1) * per_page
        end = start + per_page
        data_tampil = all_data[start:end]

        # 4. Ambil daftar saved items dari user yang login
        saved_items = []
        if current_user_id:
            user_ref = mongo.db.users.find_one({"_id": ObjectId(current_user_id)})
            if user_ref:
                saved_items = user_ref.get("saved_items", [])
                print(f"Daftar Saved Items di DB: {[str(item) for item in saved_items]}")

        # 5. Formatting JSON
        formatted_batik = []
        for b in data_tampil:
            b['_id'] = str(b['_id'])
            b['image_url'] = f"{request.host_url}static/img/galeri/{b.get('image_url', 'default_batik.png')}"
            
            if 'created_at' in b and b['created_at']:
                b['created_at'] = b['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            # Bandingkan data
            b['is_liked'] = ObjectId(b['_id']) in saved_items
            formatted_batik.append(b)

        return jsonify({
            "status": "success",
            "message": "Data galeri batik berhasil dimuat",
            "data": formatted_batik,
            "meta": {
                "current_page": page,
                "total_pages": total_pages,
                "total_items": total_items
            }
        }), 200

    except Exception as e:
        print(f"EROR BACKEND JALUR GALERI: {str(e)}") # Biar kelihatan di terminal flask kalau ada eror lain
        return jsonify({"status": "error", "message": str(e)}), 500

@galeri_api_bp.route('/galeri/<string:batik_id>', methods=['GET'])
@jwt_required(optional=True) # <--- Lakukan hal yang sama untuk Detail Batik
def get_batik_detail(batik_id):
    try:

        current_user_id = get_jwt_identity()

        print("\n=== DEBUG ENDPOINT GALERI ===")
        print(f"Token Terdeteksi (User ID): {current_user_id}")
        batik = batik_model.get_by_id(batik_id)
        if not batik:
            return jsonify({"status": "error", "message": "Data batik tidak ditemukan"}), 404
        
        batik['_id'] = str(batik['_id'])
        batik['image_url'] = f"{request.host_url}static/img/galeri/{batik.get('image_url', 'default_batik.png')}"
        
        if 'created_at' in batik and batik['created_at']:
            batik['created_at'] = batik['created_at'].strftime('%Y-%m-%d %H:%M:%S')

        # Cek status liked untuk detail batik
        current_user_id = get_jwt_identity()
        is_liked = False
        if current_user_id:
            user_ref = mongo.db.users.find_one({"_id": ObjectId(current_user_id)})
            if user_ref:
                saved_items = user_ref.get("saved_items", [])
                is_liked = ObjectId(batik['_id']) in saved_items
        
        batik['is_liked'] = is_liked

        return jsonify({
            "status": "success",
            "data": batik
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500