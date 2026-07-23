from extensions import mongo
from bson.objectid import ObjectId
from datetime import datetime

class BatikModel:
    @property
    def collection(self):
        return mongo.db.batiks

    def get_all(self, search_query=None, category=None, include_deleted=False):
        # Array untuk menampung semua kondisi query
        conditions = []
        
        # 1. Logika soft delete lama (tetap dipertahankan)
        if not include_deleted:
            conditions.append({"is_deleted": {"$ne": True}})
            
        # 2. Tambahkan filter kategori jika ada yang dipilih
        if category:
            conditions.append({"category": {"$regex": f"^{category}$", "$options": "i"}})
            
        # 3. Logika pencarian text/makna lama (tetap dipertahankan)[cite: 4]
        if search_query:
            conditions.append({
                "$or": [
                    {"name": {"$regex": search_query, "$options": "i"}},
                    {"makna": {"$regex": search_query, "$options": "i"}}
                ]
            })
            
        # Bentuk query akhir dari kondisi-kondisi di atas
        if conditions:
            # Jika include_deleted=True dan ada search_query, kita pastikan struktur query-nya valid
            if len(conditions) == 1:
                query = conditions[0]
            else:
                query = {"$and": conditions}
        else:
            query = {}
            
        return list(self.collection.find(query))

    def get_active(self, search_query=None):
        # 💡 FILTER UTAMA: Hanya ambil data yang belum di-soft delete untuk aplikasi mobile
        query = {"is_deleted": {"$ne": True}}
        
        if search_query:
            query = {
                "$and": [
                    {"is_deleted": {"$ne": True}},
                    {
                        "$or": [
                            {"name": {"$regex": search_query, "$options": "i"}},
                            {"makna": {"$regex": search_query, "$options": "i"}}
                        ]
                    }
                ]
            }
        return list(self.collection.find(query))

    def get_by_id(self, batik_id):
        pipeline = [
            {"$match": {"_id": ObjectId(batik_id)}},
            {"$lookup": {
                "from": "users",
                "localField": "user_id",
                "foreignField": "_id",
                "as": "admin_data"
            }},
            {"$unwind": {
                "path": "$admin_data", 
                "preserveNullAndEmptyArrays": True
            }},
            {
                "$lookup": {
                    "from": "users",
                    "localField": "updated_by",
                    "foreignField": "_id",
                    "as": "editor_data"
                }
            },
            {"$unwind": {"path": "$editor_data", "preserveNullAndEmptyArrays": True}}
        ]
        hasil = list(self.collection.aggregate(pipeline))
        return hasil[0] if hasil else None

    def create(self, data):
        # Memastikan field status is_deleted terinisialisasi secara eksplisit saat dokumen dibuat
        if "is_deleted" not in data:
            data["is_deleted"] = False
        return self.collection.insert_one(data)

    def update(self, batik_id, data):
        return self.collection.update_one({"_id": ObjectId(batik_id)}, {"$set": data})

    def delete(self, batik_id):
        # Soft delete: Ubah flag status menjadi True dan catat waktu penonaktifannya
        return self.collection.update_one(
            {"_id": ObjectId(batik_id)}, 
            {
                "$set": {
                    "is_deleted": True,
                    "deleted_at": datetime.now()
                }
            }
        )

    def restore(self, batik_id):
        # Mengaktifkan kembali: Kembalikan flag ke False dan hapus field deleted_at dari dokumen
        return self.collection.update_one(
            {"_id": ObjectId(batik_id)},
            {
                "$set": {"is_deleted": False},
                "$unset": {"deleted_at": ""}
            }
        )
    
    def get_by_nama(self, nama):
        # Sisi admin/validasi tetap mengecek nama dari data yang sedang aktif
        return self.collection.find_one({"name": nama, "is_deleted": {"$ne": True}})
    
    def get_by_category(self, category):
        # Digunakan jika API publik/mobile apps butuh filter kategori data yang aktif saja
        return list(self.collection.find({"category": category, "is_deleted": {"$ne": True}}))

    @staticmethod
    def serialize(batik):
        if not batik: 
            return None
        batik["_id"] = str(batik["_id"])
        return batik