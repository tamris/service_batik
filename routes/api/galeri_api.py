from flask import Blueprint, request, jsonify
from models.batik_model import BatikModel
import math

galeri_api_bp = Blueprint('galeri_api', __name__)
batik_model = BatikModel()

@galeri_api_bp.route('/galeri', methods=['GET'])
def get_all_batik():
    try:
        # 1. Parameter Pagination & Pencarian
        page = request.args.get('page', 1, type=int)
        search_query = request.args.get('q', '')
        per_page = 20 # Kamu bisa sesuaikan jumlah item per halaman

        # 2. Ambil data dari MongoDB
        all_data = batik_model.get_all(search_query)

        # 3. Logika Pagination
        total_items = len(all_data)
        total_pages = math.ceil(total_items / per_page)
        
        start = (page - 1) * per_page
        end = start + per_page
        data_tampil = all_data[start:end]

        # 4. Formating JSON
        formatted_batik = []
        for b in data_tampil:
            b['_id'] = str(b['_id'])
            
            # Konstruksi URL Gambar Lengkap
            b['gambar_url'] = f"{request.host_url}static/img/galeri/{b.get('gambar', 'default_batik.png')}"
            
            # Format Tanggal jika ada
            if 'created_at' in b and b['created_at']:
                b['created_at'] = b['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            
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
        return jsonify({"status": "error", "message": str(e)}), 500

@galeri_api_bp.route('/galeri/<string:batik_id>', methods=['GET'])
def get_batik_detail(batik_id):
    try:
        batik = batik_model.get_by_id(batik_id)
        if not batik:
            return jsonify({"status": "error", "message": "Data batik tidak ditemukan"}), 404
        
        batik['_id'] = str(batik['_id'])
        batik['gambar_url'] = f"{request.host_url}static/img/galeri/{batik.get('gambar', 'default_batik.png')}"
        
        if 'created_at' in batik and batik['created_at']:
            batik['created_at'] = batik['created_at'].strftime('%Y-%m-%d %H:%M:%S')

        return jsonify({
            "status": "success",
            "data": batik
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500