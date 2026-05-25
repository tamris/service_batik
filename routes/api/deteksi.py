import os
import numpy as np
import tensorflow as tf
from datetime import datetime
from flask import Blueprint, request, jsonify
from tensorflow.keras.preprocessing import image
from flask_jwt_extended import jwt_required, get_jwt_identity

from models.batik_model import BatikModel
from models.history_model import HistoryModel 

deteksi_bp = Blueprint('deteksi_api', __name__)
batik_db = BatikModel()
history_db = HistoryModel()

MODEL_PATH = 'batik_model.h5'
model = None

if os.path.exists(MODEL_PATH):
    try:
        model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    except Exception as e:
        print(f"Error fatal saat memuat model: {str(e)}")
else:
    print(f"Peringatan: File model '{MODEL_PATH}' tidak ditemukan!")

CATEGORIES = [
    'Beras Mawur', 'Bukan Batik Tegalan', 'Cempaka Mulya', 'Cempaka Putih', 
    'Ciprat', 'Cungkilan', 'Galaran', 'Grandil', 'Gribigan', 'Irengan', 
    'Jago Mogok', 'Kacangan', 'Kangkung', 'Kawung', 'Kembang Pacar', 
    'Kuku Macan', 'Lompongan', 'Megamendung', 'Parang', 'Pasiran', 
    'Poci Tahu Aci', 'Putri Mahkota', 'Remekan', 'Salem', 'Sawatan', 
    'Sekar Jagad', 'Sidomukti', 'Sidomulyo', 'Sisik Melik', 'Teripang', 'Watu Pecah'
]

@deteksi_bp.route('/predict', methods=['POST'])
@jwt_required()
def predict():
    if model is None:
        return jsonify({"msg": "Model AI belum siap atau gagal dimuat di server"}), 500

    if 'image' not in request.files:
        return jsonify({
            "msg": "Gambar tidak ditemukan dalam request", 
            "debug_info": list(request.files.keys())
        }), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"msg": "Nama file gambar tidak valid atau kosong"}), 400

    user_id = get_jwt_identity() 
    
    # Folder temporary untuk pemrosesan awal Keras
    UPLOAD_DIR = 'static/img'
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    temp_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        file.save(temp_path)

        # Preprocessing Gambar
        try:
            img = image.load_img(temp_path, target_size=(128, 128)) 
            x = image.img_to_array(img)
            x = np.expand_dims(x, axis=0)
            x /= 255.0
        except Exception as img_err:
            if os.path.exists(temp_path): os.remove(temp_path)
            return jsonify({"msg": "Gagal memproses file gambar.", "error": str(img_err)}), 400

        # Jalankan Prediksi
        preds = model.predict(x)
        class_idx = np.argmax(preds[0])
        hasil_label = CATEGORIES[class_idx]
        confidence = float(np.max(preds[0]) * 100)

        # --- SEKARANG MASUK KE static/img/history (SESUAI REQUEST) ---
        HISTORY_DIR = 'static/img/history'
        if not os.path.exists(HISTORY_DIR):
            os.makedirs(HISTORY_DIR)

        # Generate nama file unik biar gak crash kalau nama filenya sama
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(file.filename)[1]
        new_filename = f"history_{user_id}_{timestamp}{file_extension}"
        permanent_path = os.path.join(HISTORY_DIR, new_filename)

        # Pindahkan file ke folder permanen static/img/history
        os.rename(temp_path, permanent_path)

        # URL yang akan disimpan ke database MongoDB dan dilempar ke Flutter
        banner_image_url = f"/{HISTORY_DIR}/{new_filename}"

        # --- KONDISI 1: JIKA BUKAN BATIK TEGALAN ---
        if hasil_label == "Bukan Batik Tegalan":
            makna_bukan = "Objek ini bukan merupakan bagian dari motif Batik Tegalan."
            
            try:
                history_db.create_history(
                    user_id=user_id,
                    nama_motif=hasil_label,
                    confidence=f"{confidence:.2f}%",
                    makna=makna_bukan,
                    is_batik_tegalan=False,
                    banner_image_url=banner_image_url
                )
            except Exception as db_err:
                print(f"Gagal menyimpan history: {db_err}")

            return jsonify({
                "nama": hasil_label,
                "confidence": f"{confidence:.2f}%",
                "makna": makna_bukan,
                "is_batik_tegalan": False,
                "banner_image_url": banner_image_url
            }), 200

        # --- KONDISI 2: BERHASIL DETEKSI BATIK TEGALAN ---
        text_makna = "Makna tidak ditemukan di database."
        detail_data = batik_db.get_by_nama(hasil_label)
        
        if detail_data:
            if isinstance(detail_data, list) and len(detail_data) > 0:
                detail = detail_data[0]
            elif isinstance(detail_data, dict):
                detail = detail_data
            else:
                detail = None

            if detail and isinstance(detail, dict):
                text_makna = detail.get('makna', text_makna)

        # Simpan ke riwayat database
        try:
            history_db.create_history(
                user_id=user_id,
                nama_motif=hasil_label,
                confidence=f"{confidence:.2f}%",
                makna=text_makna,
                is_batik_tegalan=True,
                banner_image_url=banner_image_url
            )
        except Exception as db_err:
            print(f"Gagal menyimpan history: {db_err}")

        return jsonify({
            "nama": hasil_label,
            "confidence": f"{confidence:.2f}%",
            "makna": text_makna,
            "is_batik_tegalan": True,
            "banner_image_url": banner_image_url
        }), 200

    except Exception as e:
        if os.path.exists(temp_path): 
            os.remove(temp_path)
        return jsonify({"msg": "Terjadi kesalahan internal pada sistem", "error": str(e)}), 500
    
@deteksi_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    try:
        user_id = get_jwt_identity()
        user_history = history_db.get_by_user(user_id)
        return jsonify({
            "msg": "Berhasil mengambil riwayat deteksi",
            "status": "success",
            "data": user_history
        }), 200
    except Exception as e:
        return jsonify({
            "msg": "Terjadi kesalahan pada sistem saat mengambil history",
            "error": str(e)
        }), 500