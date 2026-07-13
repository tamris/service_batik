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
        return self.collection.find_one({"_id": ObjectId(event_id)})

    def create(self, data):
        return self.collection.insert_one(data)

    def update(self, event_id, data):
        return self.collection.update_one({"_id": ObjectId(event_id)}, {"$set": data})

    def delete(self, event_id):
        return self.collection.delete_one({"_id": ObjectId(event_id)})