from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
from models.user_model import toggle_like_batik, get_user_saved_items
from extensions import mongo

interaction_bp = Blueprint('interaction_api', __name__)

# =========================================================
# 1. ENDPOINT: TOGGLE LIKE / UNLIKE BATIK
# =========================================================
@interaction_bp.route('/galeri/<string:batik_id>/like', methods=['POST'])
@jwt_required()
def like_batik_action(batik_id):
    try:
        current_user_id = get_jwt_identity()
        
        if not ObjectId.is_valid(batik_id):
            return jsonify({"status": "error", "message": "Format ID Batik tidak valid"}), 400
            
        # Memastikan data batik yang mau di-like statusnya aktif / ada
        batik_exists = mongo.db.batiks.find_one({"_id": ObjectId(batik_id), "is_deleted": {"$ne": True}})
        if not batik_exists:
            return jsonify({"status": "error", "message": "Data batik tidak ditemukan atau telah dihapus"}), 404

        # Eksekusi toggle
        result = toggle_like_batik(current_user_id, batik_id)
        
        if result == "liked":
            return jsonify({"status": "success", "message": "Batik berhasil ditambahkan ke favorit", "is_liked": True}), 200
        elif result == "unliked":
            return jsonify({"status": "success", "message": "Batik dihapus dari favorit", "is_liked": False}), 200
            
        return jsonify({"status": "error", "message": "User tidak ditemukan"}), 404

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# =========================================================
# 2. ENDPOINT: GET DAFTAR ITEM TERSEMPAN USER
# =========================================================
@interaction_bp.route('/user/saved', methods=['GET'])
@jwt_required()
def get_saved_items():
    try:
        current_user_id = get_jwt_identity()
        
        # Ambil daftar batik hasil lookup
        saved_batiks = get_user_saved_items(current_user_id)
        
        formatted_list = []
        for b in saved_batiks:
            # Lewati jika ternyata kain batik tersebut sudah di-soft delete oleh admin
            if b.get("is_deleted") == True:
                continue
                
            b['_id'] = str(b['_id'])
            
            # SINKRON: Mengikuti konstruksi URL gambar dari galeri_api_bp milikmu
            b['image_url'] = f"{request.host_url}static/img/galeri/{b.get('image_url', 'default_batik.png')}"
            
            if 'created_at' in b and b['created_at']:
                b['created_at'] = b['created_at'].strftime('%Y-%m-%d %H:%M:%S')

            b['is_liked'] = True
                
            formatted_list.append(b)

        return jsonify({
            "status": "success",
            "message": "Data item tersimpan berhasil dimuat",
            "data": formatted_list
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500