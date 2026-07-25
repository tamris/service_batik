from bson.objectid import ObjectId
from datetime import datetime
from extensions import mongo

class MasterDataModel:
    @property
    def collection(self):
        # Single collection untuk semua data master
        return mongo.db.master_data

    # --- FUNGSI GENERIK ---
    def get_by_type(self, master_type):
        """Mengambil data master berdasarkan type-nya"""
        return list(self.collection.find({
            "type": master_type
        }))

    def create_master(self, master_type, name, description=""):
        """Menambah data master baru"""
        data = {
            "type": master_type,  # e.g. 'kategori_batik', 'teknik_batik', 'kategori_artikel'
            "name": name,
            "description": description,
            "created_at": datetime.now()
        }
        return self.collection.insert_one(data)

    def delete_master(self, master_id):
        """Hard delete data master (hapus permanen dari database)"""
        return self.collection.delete_one(
            {"_id": ObjectId(master_id)}
        )