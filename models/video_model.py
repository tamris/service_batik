from extensions import mongo
from bson.objectid import ObjectId

class VideoModel:
    @property
    def collection(self):
        return mongo.db.videos

    def get_all(self, search_query=None, category=None):
        conditions = []
        
        # 1. Tambahkan filter kategori jika dipilih oleh user
        if category:
            conditions.append({"category": {"$regex": f"^{category}$", "$options": "i"}})
            
        # 2. Pertahankan logika pencarian bawaan (berdasarkan judul atau deskripsi)[cite: 12]
        if search_query:
            conditions.append({
                "$or": [
                    {"title": {"$regex": search_query, "$options": "i"}},
                    {"description": {"$regex": search_query, "$options": "i"}}
                ]
            })
            
        # Tentukan objek query akhir berdasarkan kondisi array
        if conditions:
            query = {"$and": conditions}
        else:
            query = {}
            
        # Urutkan berdasarkan created_at terbaru (logika lama tetap aman)[cite: 12]
        return list(self.collection.find(query).sort("created_at", -1))

    def get_by_id(self, video_id):
        # --- UBAH MENGGUNAKAN AGGREGATION UNTUK JOIN USER ---
        pipeline = [
            {"$match": {"_id": ObjectId(video_id)}},
            
            # 1. Lookup untuk Creator (Pembuat Video) menggunakan field user_id
            {
                "$lookup": {
                    "from": "users",
                    "localField": "user_id",     # Field di koleksi videos saat create
                    "foreignField": "_id",
                    "as": "creator_data"
                }
            },
            {"$unwind": {"path": "$creator_data", "preserveNullAndEmptyArrays": True}},
            
            # 2. Lookup untuk Editor (Pengedit Terakhir) menggunakan field updated_by
            {
                "$lookup": {
                    "from": "users",
                    "localField": "updated_by",   # Field di koleksi videos saat update
                    "foreignField": "_id",
                    "as": "editor_data"
                }
            },
            {"$unwind": {"path": "$editor_data", "preserveNullAndEmptyArrays": True}}
        ]
        
        result = list(self.collection.aggregate(pipeline))
        return result[0] if result else None

    def create(self, data):
        return self.collection.insert_one(data)

    def update(self, video_id, data):
        return self.collection.update_one({"_id": ObjectId(video_id)}, {"$set": data})

    def delete(self, video_id):
        return self.collection.delete_one({"_id": ObjectId(video_id)})

    @staticmethod
    def serialize(video):
        if not video: return None
        video["_id"] = str(video["_id"])
        return video