from flask import Blueprint, request, jsonify
from models.informasi_model import InformasiModel
import math

informasi_api_bp = Blueprint('informasi_api', __name__)
info_model = InformasiModel()

@informasi_api_bp.route('/informasi', methods=['GET'])
def get_all_informasi():
    try:
        # 1. Ambil Parameter
        page = request.args.get('page', 1, type=int)
        search_query = request.args.get('q', '') 
        per_page = 10 # Kamu bisa sesuaikan jumlah data per-load-nya

        # 2. Ambil data dari MongoDB
        all_data = info_model.get_all(search_query)

        # 3. Hitung Pagination
        total_items = len(all_data)
        total_pages = math.ceil(total_items / per_page)
        
        start = (page - 1) * per_page
        end = start + per_page
        data_tampil = all_data[start:end]

        # 4. Bersihkan data (Ubah ObjectId ke string agar bisa jadi JSON)
        formatted_data = []
        for item in data_tampil:
            item['_id'] = str(item['_id'])

            if 'created_at' in item and item['created_at']:
                item['created_at'] = item['created_at'].isoformat()
            # Tambahkan base URL untuk gambar agar Flutter gampang nampilinnya
            # Ganti localhost:5000 dengan IP Server/Digital Ocean kamu nanti
            item['image_url'] = f"{request.host_url}static/img/informasi/{item.get('image_url', 'default_info.png')}"
            formatted_data.append(item)

        return jsonify({
            "status": "success",
            "message": "Data berhasil diambil",
            "data": formatted_data,
            "meta": {
                "current_page": page,
                "total_pages": total_pages,
                "total_items": total_items,
                "per_page": per_page
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    

@informasi_api_bp.route('/api/informasi/<string:info_id>', methods=['GET'])
def get_detail_informasi(info_id):
    try:
        info = info_model.get_by_id(info_id)
        if not info:
            return jsonify({"status": "error", "message": "Data tidak ditemukan"}), 404
        
        info['_id'] = str(info['_id'])
        info['image_url'] = f"{request.host_url}static/img/informasi/{info.get('image_url', 'default_info.png')}"
        
        return jsonify({
            "status": "success",
            "data": info
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500