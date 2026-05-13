from flask import current_app
from bson.objectid import ObjectId

class MappingModel:
    # HAPUS FUNGSI __init__ YANG LAMA
    
    # Gunakan @property agar dipanggil secara dinamis saat route diakses
    @property
    def collection(self):
        return current_app.mongo.db.mappings

    def get_all(self, search_query=""):
        query = {}
        if search_query:
            query = {
                "$or": [
                    {"name": {"$regex": search_query, "$options": "i"}},
                    {"category": {"$regex": search_query, "$options": "i"}},
                    {"address.full": {"$regex": search_query, "$options": "i"}}
                ]
            }
            
        # Menggunakan Aggregation ($lookup) untuk nge-JOIN dengan tabel 'users'
        pipeline = [
            {"$match": query},
            {"$sort": {"created_at": -1}},
            {"$lookup": {
                "from": "users",          # Pastikan ini adalah nama collection user kamu di MongoDB
                "localField": "user_id",  # ID yang ada di tabel mapping
                "foreignField": "_id",    # ID utama di tabel users
                "as": "admin_data"        # Hasil gabungannya disimpan di variabel ini
            }},
            {"$unwind": {
                "path": "$admin_data", 
                "preserveNullAndEmptyArrays": True # Kalau adminnya udah dihapus, data mapping gak ikut hilang
            }}
        ]
        
        return list(self.collection.aggregate(pipeline))

    def get_by_id(self, mapping_id):
        # Gunakan aggregation (JOIN) untuk menarik data admin berdasarkan user_id
        pipeline = [
            {"$match": {"_id": ObjectId(mapping_id)}},
            {"$lookup": {
                "from": "users",          # Nama tabel users
                "localField": "user_id",  # Field di tabel mapping
                "foreignField": "_id",    # Field di tabel users
                "as": "admin_data"
            }},
            {"$unwind": {
                "path": "$admin_data", 
                "preserveNullAndEmptyArrays": True
            }}
        ]
        
        # Ambil hasil query
        hasil = list(self.collection.aggregate(pipeline))
        
        # Kembalikan data index ke-0 jika ada, jika tidak kembalikan None
        if hasil:
            return hasil[0]
        return None

    def create(self, data):
        return self.collection.insert_one(data)

    def update(self, mapping_id, data):
        return self.collection.update_one({"_id": ObjectId(mapping_id)}, {"$set": data})

    def delete(self, mapping_id):
        return self.collection.delete_one({"_id": ObjectId(mapping_id)})