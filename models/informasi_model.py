from extensions import mongo
from bson.objectid import ObjectId

class InformasiModel:
    @property
    def collection(self):
        return mongo.db.informasi

    # 1. PERBAIKAN DI GET_ALL: Tambahkan Aggregation Pipeline supaya List Card juga dapat nama Admin
    def get_all(self, search_query=None):
        query = {}
        if search_query:
            query = {
                "$or": [
                    {"title": {"$regex": search_query, "$options": "i"}},
                    {"description": {"$regex": search_query, "$options": "i"}}
                ]
            }
            
        pipeline = [
            {"$match": query},
            {"$sort": {"created_at": -1}},
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
            }}
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