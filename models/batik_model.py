from extensions import mongo
from bson.objectid import ObjectId

class BatikModel:
    @property
    def collection(self):
        return mongo.db.batiks

    def get_all(self, search_query=None):
        query = {}
        if search_query:
            # Cari berdasarkan nama atau makna (case-insensitive)
            query = {
                "$or": [
                    {"nama": {"$regex": search_query, "$options": "i"}},
                    {"makna": {"$regex": search_query, "$options": "i"}}
                ]
            }
        return list(self.collection.find(query))

    def get_by_id(self, batik_id):
        return self.collection.find_one({"_id": ObjectId(batik_id)})

    def create(self, data):
        return self.collection.insert_one(data)

    def update(self, batik_id, data):
        return self.collection.update_one({"_id": ObjectId(batik_id)}, {"$set": data})

    def delete(self, batik_id):
        return self.collection.delete_one({"_id": ObjectId(batik_id)})

    @staticmethod
    def serialize(batik):
        if not batik: return None
        batik["_id"] = str(batik["_id"])
        return batik