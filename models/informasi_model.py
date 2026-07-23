from extensions import mongo
from bson.objectid import ObjectId

class InformasiModel:
    @property
    def collection(self):
        return mongo.db.informasi

    # 1. PERBAIKAN DI GET_ALL: Tambahkan Aggregation Pipeline supaya List Card juga dapat nama Admin
    def get_all(self, search_query=None, category=None):
        conditions = []
        
        # 1. Tambahkan filter kategori jika dipilih
        if category:
            conditions.append({"category": {"$regex": f"^{category}$", "$options": "i"}})
            
        # 2. Pertahankan logika pencarian bawaan (title & description)[cite: 7]
        if search_query:
            conditions.append({
                "$or": [
                    {"title": {"$regex": search_query, "$options": "i"}},
                    {"description": {"$regex": search_query, "$options": "i"}}
                ]
            })
            
        # Tentukan objek query berdasarkan kondisi array yang terisi
        if conditions:
            query = {"$and": conditions}
        else:
            query = {}
            
        pipeline = [
            {"$match": query}, # Menggunakan kombinasi filter baru kita
            {"$sort": {"created_at": -1}}, # Sorting bawaan tetap dipertahankan[cite: 7]
            {"$lookup": {
                "from": "users",
                "localField": "user_id",
                "foreignField": "_id",
                "as": "admin_data"
            }},
            {"$unwind": {
                "path": "$admin_data",
                "preserveNullAndEmptyArrays": True
            }}
        ]
        return list(self.collection.aggregate(pipeline))

    # 2. DI SINI SUDAH BAGUS: Kita pertahankan pipeline aggregate kamu
    def get_by_id(self, info_id):
        # Validasi Object ID agar Flask tidak crash kalau format string id salah
        try:
            obj_id = ObjectId(info_id)
        except Exception:
            return None

        pipeline = [
            {"$match": {"_id": obj_id}},
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
        if hasil:
            return hasil[0]
        return None

    def create(self, data):
        return self.collection.insert_one(data)

    def update(self, info_id, data):
        return self.collection.update_one({"_id": ObjectId(info_id)}, {"$set": data})

    def delete(self, info_id):
        return self.collection.delete_one({"_id": ObjectId(info_id)})
    
    def get_distinct_categories(self):
        # Mengambil semua kategori unik langsung dari database informasi
        # .distinct() otomatis mengelompokkan dan membuang duplikasi di MongoDB
        return self.collection.distinct("category")

    @staticmethod
    def serialize(info):
        if not info: return None
        info["_id"] = str(info["_id"])
        return info