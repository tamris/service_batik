from extensions import mongo
from bson.objectid import ObjectId

class VideoModel:
    @property
    def collection(self):
        return mongo.db.videos

    def get_all(self, search_query=None):
        query = {}
        if search_query:
            # Cari berdasarkan judul atau deskripsi
            query = {
                "$or": [
                    {"judul": {"$regex": search_query, "$options": "i"}},
                    {"deskripsi": {"$regex": search_query, "$options": "i"}}
                ]
            }
        # Urutkan berdasarkan created_at terbaru
        return list(self.collection.find(query).sort("created_at", -1))

    def get_by_id(self, video_id):
        return self.collection.find_one({"_id": ObjectId(video_id)})

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