import os
import numpy as np
import tensorflow as tf
from flask import Blueprint, request, jsonify
from tensorflow.keras.preprocessing import image
from models.batik_model import BatikModel

deteksi_bp = Blueprint('deteksi_api', __name__)
batik_db = BatikModel()

# Load model (Pastikan batik_model.h5 ada di root folder)
MODEL_PATH = 'batik_model.h5'
model = tf.keras.models.load_model(MODEL_PATH)

# Urutan Label Sesuai Screenshot Colab Kamu (image_23f480.png)
CATEGORIES = [
    'Beras Mawur', 'Bukan Batik Tegalan', 'Cempaka Mulya', 'Cempaka Putih', 
    'Ciprat', 'Cungkilan', 'Galaran', 'Grandil', 'Gribigan', 'Irengan', 
    'Jago Mogok', 'Kacangan', 'Kangkung', 'Kawung', 'Kembang Pacar', 
    'Kuku Macan', 'Lompongan', 'Megamendung', 'Parang', 'Pasiran', 
    'Poci Tahu Aci', 'Putri Mahkota', 'Remekan', 'Salem', 'Sawatan', 
    'Sekar Jagad', 'Sidomukti', 'Sidomulyo', 'Sisik Melik', 'Teripang', 'Watu Pecah'
]

@deteksi_bp.route('/predict', methods=['POST'])
def predict():
    # Perbaikan pengecekan file agar lebih akurat
    if 'image' not in request.files:
        return jsonify({
            "msg": "Gambar tidak ditemukan", 
            "debug_info": list(request.files.keys()) # Membantu cek key apa yang masuk
        }), 400

    file = request.files['image']
    
    # Pastikan folder static/img sudah ada
    if not os.path.exists('static/img'):
        os.makedirs('static/img')

    temp_path = os.path.join('static/img', file.filename)
    file.save(temp_path)

    try:
        # Preprocessing (Sesuaikan target_size dengan model kamu)
        img = image.load_img(temp_path, target_size=(128, 128)) 
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x /= 255.0

        # Prediksi
        preds = model.predict(x)
        class_idx = np.argmax(preds[0])
        hasil_label = CATEGORIES[class_idx]
        confidence = float(np.max(preds[0]) * 100)

        os.remove(temp_path) # Hapus temp file

        # 1. Kasus Bukan Batik Tegalan
        if hasil_label == "Bukan Batik Tegalan":
            return jsonify({
                "nama": hasil_label,
                "confidence": f"{confidence:.2f}%",
                "makna": "Objek ini bukan merupakan bagian dari motif Batik Tegalan.",
                "is_batik_tegalan": False
            }), 200

        # 2. Kasus Motif Valid (Cari Makna di DB)
        detail = batik_db.get_by_nama(hasil_label)
        
        return jsonify({
            "nama": hasil_label,
            "confidence": f"{confidence:.2f}%",
            "makna": detail['makna'] if detail else "Makna tidak ditemukan di database.",
            "is_batik_tegalan": True
        }), 200

    except Exception as e:
        if os.path.exists(temp_path): os.remove(temp_path)
        return jsonify({"msg": "Error sistem", "error": str(e)}), 500