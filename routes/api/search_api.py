from flask import Blueprint, request, jsonify
from models.batik_model import BatikModel
from models.event_model import EventModel
from models.informasi_model import InformasiModel
from models.video_model import VideoModel

search_api = Blueprint('search_api', __name__)

@search_api.route('/search', methods=['GET'])
def global_search():
    try:
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({
                "status": "success",
                "data": {"batik": [], "artikel": [], "video": [], "event": []}
            }), 200

        batik_model = BatikModel()
        event_model = EventModel()
        informasi_model = InformasiModel()
        video_model = VideoModel()

        # A. Cari Batik
        batik_cursor = batik_model.get_active(search_query=query)
        batik_results = []
        for doc in batik_cursor:
            doc['_id'] = str(doc['_id'])
            if 'user_id' in doc: doc['user_id'] = str(doc['user_id'])
            batik_results.append(doc)

        # B. Cari Artikel / Informasi (FIX CONVERSION SAFE)
        artikel_cursor = informasi_model.get_all(search_query=query)
        artikel_results = []
        for doc in artikel_cursor:
            doc['_id'] = str(doc['_id'])
            if 'user_id' in doc: doc['user_id'] = str(doc['user_id'])
            # Amankan admin_data agar tidak memicu error crash 500
            if 'admin_data' in doc and isinstance(doc['admin_data'], dict):
                if '_id' in doc['admin_data']:
                    doc['admin_data']['_id'] = str(doc['admin_data']['_id'])
            artikel_results.append(doc)

        # C. Cari Video (FIX CONVERSION SAFE)
        video_cursor = video_model.get_all(search_query=query)
        video_results = []
        for doc in video_cursor:
            doc['_id'] = str(doc['_id'])
            if 'user_id' in doc: doc['user_id'] = str(doc['user_id'])
            video_results.append(doc) # Tetap kumpulkan di list video

        # D. Cari Event (FIX CONVERSION SAFE)
        event_cursor = event_model.get_all(search_query=query)
        event_results = []
        for doc in event_cursor:
            doc['_id'] = str(doc['_id'])
            if 'user_id' in doc: doc['user_id'] = str(doc['user_id'])
            event_results.append(doc)

        return jsonify({
            "status": "success",
            "data": {
                "batik": batik_results,
                "artikel": artikel_results,
                "video": video_results,
                "event": event_results
            }
        }), 200

    except Exception as e:
        # Tampilkan error asli di terminal Flask biar kamu bisa pantau
        print(f"CRASH PADA GLOBAL SEARCH: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Terjadi kesalahan pada server backend: {str(e)}"
        }), 500