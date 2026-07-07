import os
import numpy as np
import tensorflow as tf
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from tensorflow.keras.preprocessing import image
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from models.batik_model import BatikModel
from models.history_model import HistoryModel 

deteksi_bp = Blueprint('deteksi_api', __name__)
batik_db = BatikModel()
history_db = HistoryModel()

DATASET_DIR = 'dataset_augmented_2' 
WEIGHTS_PATH = 'batik_model_weights.weights.h5'

# =====================================================================
# BEST PRACTICE 1: GLOBAL MODEL INITIALIZATION (LOAD HANYA 1 KALI)
# =====================================================================
model = None

def init_model():
    global model
    if model is not None:
        return
        
    try:
        print("Mulai membangun arsitektur Xception di server...")
        base_model = tf.keras.applications.Xception(weights=None, include_top=False, input_shape=(224, 224, 3))
        x = base_model.output
        x = tf.keras.layers.GlobalAveragePooling2D()(x)
        x = tf.keras.layers.Dense(1024, activation='relu')(x)
        predictions = tf.keras.layers.Dense(26, activation='softmax')(x)
        
        model = tf.keras.models.Model(inputs=base_model.input, outputs=predictions)
        
        if os.path.exists(WEIGHTS_PATH):
            model.load_weights(WEIGHTS_PATH)
            # Kunci model agar thread-safe saat melayani banyak request bersamaan
            model.make_predict_function() 
            print("SANGAT MANTAP: Model AI Berhasil dimuat sempurna pada startup server!")
        else:
            print(f"Peringatan Kritis: File bobot '{WEIGHTS_PATH}' tidak ditemukan!")
            model = None
    except Exception as e:
        print(f"Error fatal saat inisialisasi model pada startup: {str(e)}")
        model = None

# Jalankan fungsi load model saat file deteksi.py dibaca oleh Flask
init_model()

# Mengatur Kategori Motif Batik
if os.path.exists(DATASET_DIR):
    CATEGORIES = sorted([f for f in os.listdir(DATASET_DIR) if os.path.isdir(os.path.join(DATASET_DIR, f))])
else:
    CATEGORIES = [
        'Ambringan', 'Beras Mawur', 'Bukan Batik', 'Bukan Batik Tegalan', 'Cempaka Putih', 
        'Ciprat', 'Galaran', 'Glondahan', 'Grandilan', 'Gribigan', 
        'Jago Mogok', 'Kacangan', 'Kangkung', 'Kapal Sender', 'Kawung', 
        'Kembang Pacar', 'Mahkota', 'Parang', 'Pasiran', 'Poci', 'Remekan', 
        'Sekar Jagad', 'Sida Mukti', 'Sisik Melik', 'Watu Pecah', 'Wayang'
    ]

@deteksi_bp.route('/predict', methods=['POST'])
@jwt_required()
def predict():
    # Gunakan model global yang sudah stand-by di RAM server
    global model
    
    if model is None:
        return jsonify({"msg": "Model AI belum siap atau gagal dimuat di server"}), 500

    if 'image' not in request.files:
        return jsonify({"msg": "Gambar tidak ditemukan dalam request"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"msg": "Nama file gambar tidak valid atau kosong"}), 400

    user_id = get_jwt_identity() 
    
    # BEST PRACTICE 2: Amankan nama file dari serangan path traversal
    safe_filename = secure_filename(file.filename)
    
    HISTORY_DIR = 'static/img/history'
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR)

    # Pembuatan nama unik permanen untuk mencegah penimpaan file gambar user lain
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = os.path.splitext(safe_filename)[1]
    new_filename = f"history_{user_id}_{timestamp}{file_extension}"
    permanent_path = os.path.join(HISTORY_DIR, new_filename)
    
    try:
        # Simpan langsung ke folder permanen (menghemat operasi I/O disk)
        file.save(permanent_path)

        # Preprocessing Gambar dari file lokal secara efisien
        try:
            img = image.load_img(permanent_path, target_size=(224, 224)) 
            x = image.img_to_array(img)
            x = np.expand_dims(x, axis=0)
            x /= 255.0
        except Exception as img_err:
            if os.path.exists(permanent_path): os.remove(permanent_path)
            return jsonify({"msg": "Gagal memproses file gambar.", "error": str(img_err)}), 400

        # Jalankan Prediksi secara instan (Sangat cepat karena model sudah nangkring di memori)
        preds = model.predict(x)
        class_idx = np.argmax(preds[0])
        hasil_label = CATEGORIES[class_idx]
        confidence = float(preds[0][class_idx] * 100) 

        banner_image_url = f"/{HISTORY_DIR}/{new_filename}"

        # --- EVALUASI HASIL PREDIKSI ---
        if hasil_label == "Bukan Batik Tegalan":
            makna_output = "Objek ini bukan merupakan bagian dari motif Batik Tegalan."
            is_batik = False
        elif hasil_label == "Bukan Batik":
            makna_output = "Objek ini bukan merupakan bagian dari motif Batik."
            is_batik = False
        else:
            makna_output = "Makna tidak ditemukan di database."
            detail_data = batik_db.get_by_nama(hasil_label)
            
            if detail_data:
                detail = detail_data[0] if isinstance(detail_data, list) and len(detail_data) > 0 else detail_data
                if isinstance(detail, dict):
                    makna_output = detail.get('makna', makna_output)
            is_batik = True

        # Simpan Riwayat ke Database MongoDB secara aman
        try:
            history_db.create_history(
                user_id=user_id,
                nama_motif=hasil_label,
                confidence=f"{confidence:.2f}%",
                makna=makna_output,
                is_batik_tegalan=is_batik,
                banner_image_url=banner_image_url
            )
        except Exception as db_err:
            print(f"Gagal menyimpan riwayat ke database: {db_err}")

        # Kembalikan Respons JSON ke Flutter
        return jsonify({
            "nama": hasil_label,
            "confidence": f"{confidence:.2f}%",
            "makna": makna_output,
            "is_batik_tegalan": is_batik,
            "banner_image_url": banner_image_url
        }), 200

    except Exception as e:
        if os.path.exists(permanent_path): 
            os.remove(permanent_path)
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
        return jsonify({"msg": "Terjadi kesalahan pada sistem saat mengambil history", "error": str(e)}), 500

@deteksi_bp.route('/history/<string:history_id>', methods=['DELETE'])
@jwt_required()
def delete_history(history_id):
    try:
        user_id = get_jwt_identity()
        history_data = history_db.get_by_id(history_id)

        if not history_data:
            return jsonify({"msg": "Riwayat tidak ditemukan"}), 404

        # Validasi kepemilikan data secara aman
        if str(history_data.get("user_id")) != str(user_id):
            return jsonify({"msg": "Anda tidak memiliki akses untuk menghapus riwayat ini"}), 403

        # Eksekusi hapus data di MongoDB
        deleted = history_db.delete_history(history_id, user_id=user_id)
        if not deleted:
            return jsonify({"msg": "Gagal menghapus riwayat"}), 500

        # --- PERBAIKAN: Pembersihan File Gambar dari Disk Server ---
        banner_image_url = history_data.get("banner_image_url", "")
        if banner_image_url:
            # Menggunakan normpath untuk menyelaraskan backslash/slash sesuai OS (Windows/Linux)
            relative_image_path = banner_image_url.lstrip('/')
            image_path = os.path.normpath(os.path.join(current_app.root_path, relative_image_path))
            
            if os.path.exists(image_path):
                os.remove(image_path)
                print(f"DEBUG: File gambar {image_path} berhasil dibersihkan dari server.")

        return jsonify({
            "msg": "Riwayat berhasil dihapus",
            "status": "success",
            "deleted_id": history_id
        }), 200
        
    except Exception as e:
        return jsonify({"msg": "Terjadi kesalahan pada sistem saat menghapus history", "error": str(e)}), 500