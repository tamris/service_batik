from flask import Blueprint, request, jsonify
from models.informasi_model import InformasiModel
from bson.objectid import ObjectId  # Diperlukan untuk query user_id ke database
import math

informasi_api_bp = Blueprint('informasi_api', __name__)
info_model = InformasiModel()

@informasi_api_bp.route('/informasi', methods=['GET'])
def get_all_informasi():
    try:
        page = request.args.get('page', 1, type=int)
        search_query = request.args.get('q', '') 
        per_page = 50

        all_data = info_model.get_all(search_query)

        total_items = len(all_data)
        total_pages = math.ceil(total_items / per_page)
        
        start = (page - 1) * per_page
        end = start + per_page
        data_tampil = all_data[start:end]

        formatted_data = []
        for item in data_tampil:
            item['_id'] = str(item['_id'])

            if 'created_at' in item and item['created_at']:
                item['created_at'] = item['created_at'].isoformat()
            
            # --- EKSTRAK NAMA ADMIN DARI HASIL $LOOKUP ---
            admin_obj = item.get('admin_data')
            if admin_obj and 'username' in admin_obj:
                item['author_name'] = admin_obj['username']
            else:
                item['author_name'] = "Admin Batik Tegal"
            
            # Hapus data mentah admin_data agar JSON response API lebih bersih
            if 'admin_data' in item:
                del item['admin_data']

            if 'user_id' in item and item['user_id']:
                item['user_id'] = str(item['user_id'])

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
        return jsonify({"status": "error", "message": str(e)}), 500
    
@informasi_api_bp.route('/informasi/categories', methods=['GET'])
def get_categories_api():
    try:
        categories = info_model.get_distinct_categories()
        # Bersihkan data jika ada string kosong atau null
        cleaned_categories = [cat for cat in categories if cat]
        
        return jsonify({
            "status": "success",
            "data": cleaned_categories
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@informasi_api_bp.route('/informasi/<string:info_id>', methods=['GET'])
def get_detail_informasi(info_id):
    try:
        info = info_model.get_by_id(info_id)
        if not info:
            return jsonify({"status": "error", "message": "Data tidak ditemukan"}), 404
        
        info['_id'] = str(info['_id'])
        
        if 'created_at' in info and info['created_at']:
            info['created_at'] = info['created_at'].isoformat()
            
        # --- EKSTRAK NAMA ADMIN DI DETAIL ---
        admin_obj = info.get('admin_data')
        if admin_obj and 'username' in admin_obj:
            info['author_name'] = admin_obj['username']
        else:
            info['author_name'] = "Admin Batik Tegal"
            
        if 'admin_data' in info:
            del info['admin_data']
        
        if 'user_id' in info and info['user_id']:
            info['user_id'] = str(info['user_id'])
            
        info['image_url'] = f"{request.host_url}static/img/informasi/{info.get('image_url', 'default_info.png')}"
        
        return jsonify({
            "status": "success",
            "data": info
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
