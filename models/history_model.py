from datetime import datetime
from extensions import mongo

class HistoryModel:
    def __init__(self):
        # Kita tidak meng-import 'app' di sini untuk menghindari Circular Import Error.
        # Kita buat properti collection secara dinamis menggunakan property dekorator di bawah.
        pass

    @property
    def collection(self):
        return mongo.db.history_deteksi

    def create_history(self, user_id, nama_motif, confidence, makna, is_batik_tegalan, banner_image_url):
        """
        Menyimpan riwayat deteksi ke database MongoDB
        """
        db_collection = self.collection
        if db_collection is None:
            print("Gagal menyimpan history: Koneksi database tidak tersedia.")
            return False

        data = {
            "user_id": user_id, 
            "nama_motif": nama_motif,
            "confidence": confidence,
            "makna": makna,
            "is_batik_tegalan": is_batik_tegalan,
            "banner_image_url": banner_image_url,  # Pastikan variabel ini sudah didefinisikan sebelumnya
            "created_at": datetime.now()
        }
        
        try:
            db_collection.insert_one(data)
            print(f"Berhasil menyimpan riwayat untuk user: {user_id}")
            return True
        except Exception as e:
            print(f"Gagal saat eksekusi insert_one: {e}")
            return False

    def get_by_user(self, user_id):
        """
        Mengambil semua riwayat milik user tertentu, diurutkan dari yang terbaru
        """
        db_collection = self.collection
        if db_collection is None:
            print("Gagal mengambil history: Koneksi database tidak tersedia.")
            return []

        try:
            cursor = db_collection.find({"user_id": user_id}).sort("created_at", -1)
            
            history_list = []
            for doc in cursor:
                doc['_id'] = str(doc['_id'])
                if 'created_at' in doc and doc['created_at']:
                    doc['created_at'] = doc['created_at'].isoformat()
                
                history_list.append(doc)
                
            return history_list
        except Exception as e:
            print(f"Gagal mengambil data dari MongoDB: {e}")
            return []