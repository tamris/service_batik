from datetime import datetime
from flask import current_app
from bson.objectid import ObjectId

class MappingModel:
    # HAPUS FUNGSI __init__ YANG LAMA
    
    # Gunakan @property agar dipanggil secara dinamis saat route diakses
    @property
    def collection(self):
        return current_app.mongo.db.mappings

    def get_all(self, search_query="", category=""):
        conditions = []
        
        # 1. Tambahkan filter kategori jika dipilih oleh user
        if category:
            conditions.append({"category": {"$regex": f"^{category}$", "$options": "i"}})
            
        # 2. Pertahankan logika pencarian multi-field text bawaan kamu (name, category, address.full)
        if search_query:
            conditions.append({
                "$or": [
                    {"name": {"$regex": search_query, "$options": "i"}},
                    {"category": {"$regex": search_query, "$options": "i"}},
                    {"address.full": {"$regex": search_query, "$options": "i"}}
                ]
            })
            
        # Tentukan objek query berdasarkan kondisi array
        if conditions:
            query = {"$and": conditions}
        else:
            query = {}
            
        # Menggunakan Aggregation ($lookup) untuk nge-JOIN dengan tabel 'users'[cite: 14]
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
    
    def get_username_by_id(self, user_id):
        """Mencari nama user berdasarkan user_id di koleksi users"""
        # Akses koleksi 'users' secara dinamis
        user_data = current_app.mongo.db.users.find_one({"_id": ObjectId(user_id)}, {"username": 1})
        if user_data:
            return user_data.get("username", "Anonymous")
        return "Anonymous"
    
    def add_review(self, mapping_id, review_data):
        """
        Menambahkan ulasan baru ke dalam array 'reviews' dan mengupdate 
        nilai 'average_rating' serta 'total_reviews' secara atomik.
        """
        # 1. Masukkan review baru ke dalam array 'reviews'
        self.collection.update_one(
            {"_id": ObjectId(mapping_id)},
            {"$push": {"reviews": review_data}}
        )

        # 2. Ambil data dokumen terbaru untuk menghitung ulang rata-rata rating
        mapping = self.collection.find_one({"_id": ObjectId(mapping_id)})
        if not mapping:
            return False

        reviews = mapping.get("reviews", [])
        total_reviews = len(reviews)
        
        if total_reviews > 0:
            # Hitung total bintang lalu bagi dengan total review
            total_stars = sum([r.get("rating", 0) for r in reviews])
            average_rating = round(float(total_stars / total_reviews), 1)
        else:
            average_rating = 0.0

        # 3. Update field denormalisasi ke dalam dokumen utama
        self.collection.update_one(
            {"_id": ObjectId(mapping_id)},
            {
                "$set": {
                    "average_rating": average_rating,
                    "total_reviews": total_reviews,
                    "update_at": datetime.now() # Pastikan datetime di-import di model jika belum
                }
            }
        )
        return True
    
    def check_existing_review(self, mapping_id, user_id):
        """Mengecek apakah user ini sudah pernah me-review lokasi ini"""
        return self.collection.find_one({
            "_id": ObjectId(mapping_id),
            "reviews.user_id": ObjectId(user_id)
        }) is not None

    def recalculate_rating(self, mapping_id):
        """Fungsi helper internal untuk menghitung ulang rata-rata rating"""
        mapping = self.collection.find_one({"_id": ObjectId(mapping_id)})
        if not mapping:
            return

        reviews = mapping.get("reviews", [])
        total_reviews = len(reviews)
        
        if total_reviews > 0:
            total_stars = sum([r.get("rating", 0) for r in reviews])
            average_rating = round(float(total_stars / total_reviews), 1)
        else:
            average_rating = 0.0

        self.collection.update_one(
            {"_id": ObjectId(mapping_id)},
            {
                "$set": {
                    "average_rating": average_rating,
                    "total_reviews": total_reviews,
                    "update_at": datetime.now()
                }
            }
        )

    def add_review(self, mapping_id, review_data):
        """Menambahkan ulasan baru"""
        self.collection.update_one(
            {"_id": ObjectId(mapping_id)},
            {"$push": {"reviews": review_data}}
        )
        self.recalculate_rating(mapping_id)
        return True

    def update_user_review(self, mapping_id, user_id, rating, comment):
        """Mengupdate ulasan milik user tertentu di dalam array reviews"""
        result = self.collection.update_one(
            {
                "_id": ObjectId(mapping_id),
                "reviews.user_id": ObjectId(user_id)
            },
            {
                "$set": {
                    "reviews.$.rating": int(rating),
                    "reviews.$.comment": comment,
                    "reviews.$.created_at": datetime.now() # Tanggal diperbarui
                }
            }
        )
        
        if result.modified_count > 0:
            # Jika berhasil diubah, hitung ulang rata-ratanya
            self.recalculate_rating(mapping_id)
            return True
        return False