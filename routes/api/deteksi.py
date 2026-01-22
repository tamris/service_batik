import os
import numpy as np
# 1. Tambahkan ini di paling atas untuk membungkam log TensorFlow yang tidak perlu
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 

import tensorflow as tf
from flask import Blueprint, request, jsonify
from tensorflow.keras.preprocessing import image
from models.batik_model import BatikModel

deteksi_bp = Blueprint('deteksi_api', __name__)
batik_db = BatikModel()

# Path model sesuai struktur folder kamu
MODEL_PATH = 'batik_model.h5'
model = None

model = tf.keras.models.load_model(MODEL_PATH, compile=False)

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
    # Pastikan model sudah terisi
    if model is None:
        return jsonify({"msg": "Model belum siap atau gagal dimuat"}), 500

    if 'image' not in request.files:
        return jsonify({
            "msg": "Gambar tidak ditemukan", 
            "debug_info": list(request.files.keys())
        }), 400

    file = request.files['image']
    
    if not os.path.exists('static/img'):
        os.makedirs('static/img')

    temp_path = os.path.join('static/img', file.filename)
    file.save(temp_path)

    try:
        # Preprocessing: Pastikan target_size sesuai dengan input model kamu (biasanya 224 atau 128)
        img = image.load_img(temp_path, target_size=(128, 128)) 
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x /= 255.0

        # Prediksi
        preds = model.predict(x)
        class_idx = np.argmax(preds[0])
        hasil_label = CATEGORIES[class_idx]
        confidence = float(np.max(preds[0]) * 100)

        os.remove(temp_path)

        if hasil_label == "Bukan Batik Tegalan":
            return jsonify({
                "nama": hasil_label,
                "confidence": f"{confidence:.2f}%",
                "makna": "Objek ini bukan merupakan bagian dari motif Batik Tegalan.",
                "is_batik_tegalan": False
            }), 200

        # Cari Makna di DB Batik Tegalan
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