import os
from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import get_jwt_identity, jwt_required
from models.batik_model import BatikModel
from models.studio_draft_model import StudioDraftModel
from extensions import mongo # 💡 Pastikan extensions mongo ini sudah sesuai dengan konfigurasi PyMongo lo

studio_api_bp = Blueprint('studio_api', __name__)
batik_model = BatikModel()
draft_model = StudioDraftModel()


@studio_api_bp.route('/studio/canvas-list', methods=['GET'])
def get_canvas_sketches():
    try:
        all_batik = batik_model.get_all("", include_deleted=False)
        canvas_ready_batik = []
        for b in all_batik:
            if b.get('is_sketsa_available') == True and b.get('sketch_image_url'):
                b['_id'] = str(b['_id'])
                b['image_url'] = f"{request.host_url}static/img/galeri/{b.get('image_url', 'default_batik.png')}"
                
                # Arahkan URL sketsa ke endpoint API baru berbasis ID, bukan ke file statis lagi
                b['sketch_image_url'] = f"{request.host_url}api/studio/sketch/{b['_id']}"
                
                if 'created_at' in b and b['created_at']:
                    b['created_at'] = b['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                canvas_ready_batik.append(b)

        return jsonify({
            "status": "success",
            "message": "Data sketsa studio canvas berhasil dimuat",
            "total_canvas": len(canvas_ready_batik),
            "data": canvas_ready_batik
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ENDPOINT API BARU: Mengirimkan File Gambar Sketsa Langsung Berdasarkan ID Batik
@studio_api_bp.route('/studio/sketch/<string:batik_id>', methods=['GET'])
def get_sketch_image_by_id(batik_id):
    try:
        # 1. Cari data batik di MongoDB berdasarkan ID
        batik = batik_model.get_by_id(batik_id)
        if not batik or not batik.get('sketch_image_url'):
            return jsonify({"status": "error", "message": "File sketsa tidak ditemukan di database"}), 404
        
        # 2. Ambil nama file sketsa dari dokumen database
        sketch_filename = batik['sketch_image_url']
        
        # Pastikan ekstensinya aman tersemat (.png)
        if not sketch_filename.endswith('.png'):
            sketch_filename = f"{sketch_filename}.png"
            
        SKETCH_DIRECTORY = os.path.join('static', 'img', 'sketch')
        
        # 3. Validasi fisik: Jika file beneran tidak ada di folder laptop, kirim gambar default transparan biar Flutter gak crash
        if not os.path.exists(os.path.join(SKETCH_DIRECTORY, sketch_filename)):
            # Jika file fisik hilang, kita lempar balik informasi eror yang jelas
            return jsonify({"status": "error", "message": f"File fisik {sketch_filename} tidak ada di direktori server"}), 404

        # 4. Ambil dan kirim file gambar aslinya secara langsung
        return send_from_directory(SKETCH_DIRECTORY, sketch_filename)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    

@studio_api_bp.route('/studio/save-draft', methods=['POST'])
@jwt_required() # 🔒 WAJIB JWT: Menolak request jika token tidak valid/tidak ada
def save_draft():
    try:
        # 1. Ekstrak otomatis user_id dari payload dekripsi token JWT
        current_user_id = get_jwt_identity() 
        
        data = request.get_json()
        batik_id = data.get('batik_id')
        canvas_json = data.get('canvas_json') # Data koordinat mentah atau string Base64 dari Flutter

        if not batik_id or not canvas_json:
            return jsonify({"status": "error", "message": "Parameter batik_id atau canvas_json tidak boleh kosong"}), 400

        # 2. Oper ke model untuk proses save/update pintar
        success = draft_model.save_or_update_draft(current_user_id, batik_id, canvas_json)
        if success:
            return jsonify({"status": "success", "message": "Progres membatik aman tersimpan"}), 200
        
        return jsonify({"status": "error", "message": "Gagal mengamankan draf ke database"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@studio_api_bp.route('/studio/get-draft', methods=['GET'])
@jwt_required() # 🔒 WAJIB JWT
def get_draft():
    try:
        # Ekstrak otomatis user_id dari token JWT
        current_user_id = get_jwt_identity()
        batik_id = request.args.get('batik_id')

        if not batik_id:
            return jsonify({"status": "error", "message": "Parameter batik_id wajib disertakan"}), 400

        draft = draft_model.get_draft(current_user_id, batik_id)
        
        # Jika belum pernah menggambar motif ini, kembalikan string kosong agar kanvas Flutter bersih
        if not draft:
            return jsonify({"status": "success", "canvas_json": ""}), 200

        return jsonify({
            "status": "success",
            "canvas_json": draft['canvas_json']
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# 💡 ENDPOINT SAKTI BARU: Mengambil list draf khusus yang sudah pernah disimpan oleh user aktif (JWT)
@studio_api_bp.route('/studio/my-drafts', methods=['GET'])
@jwt_required() # 🔒 WAJIB JWT: Saring ketat per user akun login
def get_my_drafts():
    try:
        from bson.objectid import ObjectId
        current_user_id = get_jwt_identity()
        
        # 1. Tarik semua data draf dari koleksi 'studio_drafts' yang miliknya user_id ini
        my_raw_drafts = list(mongo.db.studio_drafts.find({"user_id": ObjectId(current_user_id)}))
        
        filtered_draft_list = []
        for draft in my_raw_drafts:
            # 2. Jemput informasi detail motif batik aslinya (Nama & Gambar Utama) dari tabel batik
            batik_info = batik_model.get_by_id(str(draft["batik_id"]))
            
            if batik_info:
                filtered_draft_list.append({
                    "id": str(batik_info["_id"]),
                    "name": batik_info.get("name", ""),
                    "image_url": f"{request.host_url}static/img/galeri/{batik_info.get('image_url', 'default_batik.png')}",
                    "updated_at": draft["updated_at"].strftime('%Y-%m-%d %H:%M:%S') if "updated_at" in draft else "Baru saja"
                })
                
        return jsonify({
            "status": "success",
            "message": "Daftar draf membatik user berhasil dimuat",
            "data": filtered_draft_list
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500