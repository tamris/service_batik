from flask import Blueprint, request, jsonify
from models.mapping_model import MappingModel
from bson.objectid import ObjectId
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity 

mapping_api_bp = Blueprint('mapping_api', __name__)
mapping_model = MappingModel()

def serialize_doc(doc):
    """Helper untuk mengubah ObjectId dan datetime menjadi string agar bisa di-JSON-kan"""
    if not doc:
        return None
    doc['_id'] = str(doc['_id'])
    if 'user_id' in doc:
        doc['user_id'] = str(doc['user_id'])
    if 'created_at' in doc and isinstance(doc['created_at'], datetime):
        doc['created_at'] = doc['created_at'].isoformat()
    if 'update_at' in doc and isinstance(doc['update_at'], datetime):
        doc['update_at'] = doc['update_at'].isoformat()
    
    # Bersihkan data di dalam array reviews jika ada
    if 'reviews' in doc and isinstance(doc['reviews'], list):
        for r in doc['reviews']:
            if 'review_id' in r:
                r['review_id'] = str(r['review_id'])
            if 'user_id' in r:
                r['user_id'] = str(r['user_id'])
            if 'created_at' in r and isinstance(r['created_at'], datetime):
                r['created_at'] = r['created_at'].isoformat()
                
    # Bersihkan field join admin_data dari aggregation jika ada
    if 'admin_data' in doc and isinstance(doc['admin_data'], dict):
        if '_id' in doc['admin_data']:
            doc['admin_data']['_id'] = str(doc['admin_data']['_id'])
        # Hilangkan password demi keamanan agar tidak terkirim ke API
        doc['admin_data'].pop('password', None) 
        
    return doc


# ==========================================
# 1. API GET ALL LOKASI (Untuk Map / List di Flutter)
# ==========================================
@mapping_api_bp.route('/mappings', methods=['GET'])
def get_all_locations():
    try:
        search_query = request.args.get('q', '')
        all_data = mapping_model.get_all(search_query)
        
        # Konversi object id ke string
        serialized_data = [serialize_doc(doc) for doc in all_data]
        
        return jsonify({
            "status": "success",
            "message": "Berhasil mengambil data lokasi batik",
            "data": serialized_data
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ==========================================
# 2. API GET DETAIL LOKASI BY ID
# ==========================================
@mapping_api_bp.route('/mappings/<string:mapping_id>', methods=['GET'])
def get_detail_location(mapping_id):
    try:
        if not ObjectId.is_valid(mapping_id):
            return jsonify({"status": "error", "message": "ID Lokasi tidak valid"}), 400
            
        mapping = mapping_model.get_by_id(mapping_id)
        if not mapping:
            return jsonify({"status": "error", "message": "Data lokasi tidak ditemukan"}), 404
            
        return jsonify({
            "status": "success",
            "message": "Berhasil mengambil detail lokasi batik",
            "data": serialize_doc(mapping)
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ==========================================
# 3. API POST REVIEW (DENGAN PROTEKSI ANTI-SPAM)
# ==========================================
@mapping_api_bp.route('/mappings/<string:mapping_id>/reviews', methods=['POST'])
@jwt_required()
def post_review(mapping_id):
    try:
        if not ObjectId.is_valid(mapping_id):
            return jsonify({"status": "error", "message": "ID Lokasi tidak valid"}), 400
            
        data = request.get_json()
        rating = data.get('rating')
        comment = data.get('comment', '')

        if not rating or not (1 <= int(rating) <= 5):
            return jsonify({"status": "error", "message": "Rating wajib diisi angka 1-5"}), 400

        current_user_id = get_jwt_identity()

        # VALIDASI BARU: Cek apakah user ini udah pernah ngasih review di toko batik ini
        if mapping_model.check_existing_review(mapping_id, current_user_id):
            return jsonify({
                "status": "error", 
                "message": "Kamu sudah memberikan ulasan di lokasi ini. Gunakan fitur edit untuk mengubah."
            }), 400

        username = mapping_model.get_username_by_id(current_user_id)

        review_baru = {
            "review_id": ObjectId(),
            "user_id": ObjectId(current_user_id),
            "username": username,
            "rating": int(rating),
            "comment": comment,
            "created_at": datetime.now()
        }

        mapping_model.add_review(mapping_id, review_baru)
        return jsonify({"status": "success", "message": "Ulasan berhasil ditambahkan!"}), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ==========================================
# 4. API UPDATE/EDIT REVIEW (BARU)
# ==========================================
@mapping_api_bp.route('/mappings/<string:mapping_id>/reviews', methods=['PUT'])
@jwt_required()
def update_review(mapping_id):
    try:
        if not ObjectId.is_valid(mapping_id):
            return jsonify({"status": "error", "message": "ID Lokasi tidak valid"}), 400
            
        data = request.get_json()
        rating = data.get('rating')
        comment = data.get('comment', '')

        if not rating or not (1 <= int(rating) <= 5):
            return jsonify({"status": "error", "message": "Rating wajib diisi angka 1-5"}), 400

        current_user_id = get_jwt_identity()

        # Jalankan update ke sub-dokumen array MongoDB
        success = mapping_model.update_user_review(mapping_id, current_user_id, rating, comment)
        
        if not success:
            return jsonify({
                "status": "error", 
                "message": "Gagal memperbarui ulasan. Kamu belum pernah mengulas tempat ini atau lokasi tidak ditemukan."
            }), 400

        return jsonify({"status": "success", "message": "Ulasan berhasil diperbarui!"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500