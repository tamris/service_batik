from extensions import mongo
from bson.objectid import ObjectId

class InformasiModel:
    @property
    def collection(self):
        return mongo.db.informasi

    # Tambahkan parameter search_query=None agar tidak error
    def get_all(self, search_query=None):
        query = {}
        if search_query:
            # Cari berdasarkan judul atau deskripsi (case-insensitive)
            query = {
                "$or": [
                    {"judul": {"$regex": search_query, "$options": "i"}},
                    {"deskripsi": {"$regex": search_query, "$options": "i"}}
                ]
            }
        return list(self.collection.find(query))

    def get_by_id(self, info_id):
        return self.collection.find_one({"_id": ObjectId(info_id)})

    def create(self, data):
        return self.collection.insert_one(data)

    def update(self, info_id, data):
        return self.collection.update_one({"_id": ObjectId(info_id)}, {"$set": data})

    def delete(self, info_id):
        return self.collection.delete_one({"_id": ObjectId(info_id)})

    @staticmethod
    def serialize(info):
        if not info: return None
        info["_id"] = str(info["_id"])
        return info