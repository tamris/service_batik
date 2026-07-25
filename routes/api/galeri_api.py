import os
import cv2
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
import numpy as np
from io import BytesIO
from models.batik_model import BatikModel
from extensions import mongo
import math

galeri_api_bp = Blueprint('galeri_api', __name__)
batik_model = BatikModel()

@galeri_api_bp.route('/galeri', methods=['GET'])
@jwt_required(optional=True)
def get_all_batik():
    try:
        current_user_id = get_jwt_identity()

        page = request.args.get('page', 1, type=int)
        search_query = request.args.get('q', '')
        per_page = 20

        all_data = batik_model.get_all(search_query)

        total_items = len(all_data)
        total_pages = math.ceil(total_items / per_page)
        
        start = (page - 1) * per_page
        end = start + per_page
        data_tampil = all_data[start:end]

        saved_items = []
        if current_user_id:
            user_ref = mongo.db.users.find_one({"_id": ObjectId(current_user_id)})
            if user_ref:
                saved_items = user_ref.get("saved_items", [])

        formatted_batik = []
        for b in data_tampil:
            b['_id'] = str(b['_id'])
            b['image_url'] = f"{request.host_url}static/img/galeri/{b.get('image_url', 'default_batik.png')}"
            
            if 'created_at' in b and b['created_at']:
                b['created_at'] = b['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            
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
        print(f"EROR BACKEND JALUR GALERI: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


@galeri_api_bp.route('/galeri/<string:batik_id>', methods=['GET'])
@jwt_required(optional=True)
def get_batik_detail(batik_id):
    try:
        current_user_id = get_jwt_identity()

        batik = batik_model.get_by_id(batik_id)
        if not batik:
            return jsonify({"status": "error", "message": "Data batik tidak ditemukan"}), 404
        
        batik['_id'] = str(batik['_id'])
        batik['image_url'] = f"{request.host_url}static/img/galeri/{batik.get('image_url', 'default_batik.png')}"
        
        if 'created_at' in batik and batik['created_at']:
            batik['created_at'] = batik['created_at'].strftime('%Y-%m-%d %H:%M:%S')

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
    

def get_dominant_hsv_color(image, k=3):
    """
    Fungsi untuk mendeteksi warna dominan secara otomatis menggunakan K-Means Clustering
    """
    small_img = cv2.resize(image, (100, 100))
    hsv_small = cv2.cvtColor(small_img, cv2.COLOR_BGR2HSV)
    
    pixels = hsv_small.reshape((-1, 3)).astype(np.float32)
    
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    
    counts = np.bincount(labels.flatten())
    dominant_cluster_idx = np.argmax(counts)
    
    return centers[dominant_cluster_idx]
    

@galeri_api_bp.route('/galeri/<string:batik_id>/modifikasi-warna', methods=['POST'])
@jwt_required(optional=True)
def modifikasi_warna_batik(batik_id):
    try:
        # 1. Ambil data batik dari MongoDB
        batik = batik_model.get_by_id(batik_id)
        if not batik:
            return jsonify({"status": "error", "message": "Data batik tidak ditemukan"}), 404

        # 2. Ambil target hue dari JSON Body
        data = request.get_json() or request.form or {}
        target_hue = int(data.get('hue', 120)) 

        # 3. Baca gambar dari folder static
        raw_image_url = batik.get('image_url', 'default_batik.png')
        filename = os.path.basename(raw_image_url)
        image_path = os.path.join("static", "img", "galeri", filename)

        image = cv2.imread(image_path)
        if image is None:
            return jsonify({"status": "error", "message": f"File gambar '{filename}' tidak ditemukan di server"}), 404

        # 4. Konversi ke HSV
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # 5. DETEKSI WARNA DOMINAN (WAJIB DIPANGGIL DI SINI!)
        dom_h, dom_s, dom_v = get_dominant_hsv_color(image)

        # 6. MASKING DINAMIS BERDASARKAN WARNA DOMINAN
        # A. Warna Putih / Terang
        if dom_s < 40:
            lower_bound = np.array([0, 0, int(max(0, dom_v - 50))])
            upper_bound = np.array([180, 50, 255])
            mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
            
            h, s, v = cv2.split(hsv_image)
            h[mask > 0] = target_hue
            s[mask > 0] = 180 

        # B. Warna Merah (Hue di ujung skala 0-15 atau 165-180)
        elif dom_h < 15 or dom_h > 165:
            m1 = cv2.inRange(hsv_image, np.array([0, 30, 30]), np.array([15, 255, 255]))
            m2 = cv2.inRange(hsv_image, np.array([165, 30, 30]), np.array([180, 255, 255]))
            mask = cv2.bitwise_or(m1, m2)
            
            h, s, v = cv2.split(hsv_image)
            h[mask > 0] = target_hue

        # C. Warna Lain (Cokelat, Hijau, Biru, Kuning, Ungu, dll)
        else:
            hue_low = max(0, int(dom_h - 18))
            hue_high = min(179, int(dom_h + 18))
            
            lower_bound = np.array([hue_low, 30, 30])
            upper_bound = np.array([hue_high, 255, 255])
            mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
            
            h, s, v = cv2.split(hsv_image)
            h[mask > 0] = target_hue

        # 7. Merge & Convert kembali ke BGR
        new_hsv = cv2.merge([h, s, v])
        result_image = cv2.cvtColor(new_hsv, cv2.COLOR_HSV2BGR)

        # 8. Encode ke RAM
        success, buffer = cv2.imencode('.jpg', result_image)
        if not success:
            return jsonify({"status": "error", "message": "Gagal memproses gambar"}), 500

        io_buf = BytesIO(buffer)

        return send_file(
            io_buf,
            mimetype='image/jpeg',
            as_attachment=False,
            download_name=f"modifikasi_{filename}"
        )

    except Exception as e:
        print(f"EROR MODIFIKASI WARNA: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500