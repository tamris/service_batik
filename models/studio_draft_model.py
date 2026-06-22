from datetime import datetime
from extensions import mongo
from bson.objectid import ObjectId

class StudioDraftModel:
    def __init__(self):
        pass

    @property
    def collection(self):
        # Menggunakan koleksi studio_drafts di MongoDB
        return mongo.db.studio_drafts

    def save_or_update_draft(self, user_id, batik_id, canvas_json):
        """
        Menyimpan koordinat baru atau menimpa draf coretan yang sudah ada (Anti-Spam)
        """
        db_collection = self.collection
        if db_collection is None:
            print("Database tidak terkoneksi.")
            return False

        try:
            # Mengunci query berdasarkan user_id dan batik_id hasil saringan JWT
            query = {
                "user_id": ObjectId(user_id), 
                "batik_id": ObjectId(batik_id)
            }
            existing_draft = db_collection.find_one(query)

            if existing_draft:
                # Jika user klik save berkali-kali, TIMPA/UPDATE koordinat lama (Anti-Spam)
                db_collection.update_one(
                    {"_id": existing_draft["_id"]},
                    {"$set": {
                        "canvas_json": canvas_json, 
                        "updated_at": datetime.now()
                    }}
                )
                print(f"[Studio] Berhasil update draf untuk user: {user_id}")
            else:
                # Jika baru pertama kali mencoret motif ini, buat baris baru
                data = {
                    "user_id": ObjectId(user_id),
                    "batik_id": ObjectId(batik_id),
                    "canvas_json": canvas_json,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
                db_collection.insert_one(data)
                print(f"[Studio] Berhasil membuat draf baru untuk user: {user_id}")
            return True
        except Exception as e:
            print(f"[Studio Eror] Gagal menyimpan draf: {e}")
            return False

    def get_draft(self, user_id, batik_id):
        """
        Mengambil koordinat gambar terakhir milik user untuk resume membatik
        """
        db_collection = self.collection
        if db_collection is None:
            return None

        try:
            return db_collection.find_one({
                "user_id": ObjectId(user_id), 
                "batik_id": ObjectId(batik_id)
            })
        except Exception as e:
            print(f"[Studio Eror] Gagal mengambil draf: {e}")
            return None