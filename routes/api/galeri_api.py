from flask import Blueprint, jsonify
from models.batik_model import BatikModel

api_bp = Blueprint('api_galeri', __name__)
batik_model = BatikModel()

@api_bp.route('/batiks', methods=['GET'])
def get_batiks_api():
    try:
        # Ambil semua data dari MongoDB
        data = batik_model.get_all()
        # Serialize agar _id jadi string (agar Flutter tidak error)
        output = [BatikModel.serialize(b) for b in data]
        
        return jsonify({
            "status": "success",
            "total": len(output),
            "data": output
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@api_bp.route('/batiks/<string:batik_id>', methods=['GET'])
def get_detail_api(batik_id):
    try:
        data = batik_model.get_by_id(batik_id)
        if data:
            return jsonify({
                "status": "success",
                "data": BatikModel.serialize(data)
            }), 200
        return jsonify({"status": "error", "message": "Batik tidak ditemukan"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500