from extensions import mongo
from bson.objectid import ObjectId

class EventModel:
    @property
    def collection(self):
        return mongo.db.events

    def get_all(self, search_query=None, category=None):
        conditions = []
        
        # 1. Tambahkan kondisi filter kategori jika ada yang dipilih
        if category:
            conditions.append({"category": {"$regex": f"^{category}$", "$options": "i"}})
            
        # 2. Pertahankan logika pencarian multi-field text bawaan kamu (title, description, address.full)[cite: 9]
        if search_query:
            conditions.append({
                "$or": [
                    {"title": {"$regex": search_query, "$options": "i"}},
                    {"description": {"$regex": search_query, "$options": "i"}},
                    {"address.full": {"$regex": search_query, "$options": "i"}}
                ]
            })
            
        # Tentukan skema query MongoDB akhir
        if conditions:
            query = {"$and": conditions}
        else:
            query = {}
            
        return list(self.collection.find(query).sort("created_at", -1))

    def get_by_id(self, event_id):
        pipeline = [
            {"$match": {"_id": ObjectId(event_id)}},
            
            # 1. Lookup untuk Creator (Pembuat)
            {
                "$lookup": {
                    "from": "users",
                    "localField": "user_id",
                    "foreignField": "_id",
                    "as": "creator_data"
                }
            },
            {"$unwind": {"path": "$creator_data", "preserveNullAndEmptyArrays": True}},
            
            # 2. Lookup untuk Editor (Pengedit Terakhir)
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
        
        result = list(self.collection.aggregate(pipeline))
        return result[0] if result else None

    def create(self, data):
        return self.collection.insert_one(data)

    def update(self, event_id, data):
        return self.collection.update_one({"_id": ObjectId(event_id)}, {"$set": data})

    def delete(self, event_id):
        return self.collection.delete_one({"_id": ObjectId(event_id)})