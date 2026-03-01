from flask import Blueprint, request, jsonify
from models.event_model import EventModel
import math

event_api_bp = Blueprint('event_api', __name__)
event_model = EventModel()

@event_api_bp.route('/events', methods=['GET'])
def get_all_events():
    try:
        # 1. Parameter Pagination & Search
        page = request.args.get('page', 1, type=int)
        search_query = request.args.get('q', '')
        per_page = 5  # Event biasanya tampil lebih besar, jadi per page lebih sedikit

        # 2. Ambil data dari MongoDB
        all_data = event_model.get_all(search_query)

        # 3. Logika Pagination
        total_items = len(all_data)
        total_pages = math.ceil(total_items / per_page)
        
        start = (page - 1) * per_page
        end = start + per_page
        data_tampil = all_data[start:end]

        # 4. Formatting data untuk JSON
        formatted_events = []
        for e in data_tampil:
            e['_id'] = str(e['_id'])
            
            # Ubah URL Banner
            e['banner_image_url'] = f"{request.host_url}static/img/events/{e.get('banner_image_url', 'default_event.png')}"
            
            # FIX 1: Ubah event_date ke String (Ini yang bikin Error 500)
            if 'event_date' in e and e['event_date']:
                # Gunakan isoformat agar Flutter gampang membacanya
                if hasattr(e['event_date'], 'isoformat'):
                    e['event_date'] = e['event_date'].isoformat()
                else:
                    e['event_date'] = str(e['event_date'])

            # FIX 2: Pastikan created_at juga aman
            if 'created_at' in e and e['created_at']:
                if hasattr(e['created_at'], 'strftime'):
                    e['created_at'] = e['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                else:
                    e['created_at'] = str(e['created_at'])
                
            formatted_events.append(e)

        return jsonify({
            "status": "success",
            "message": "Data event berhasil dimuat",
            "data": formatted_events,
            "meta": {
                "current_page": page,
                "total_pages": total_pages,
                "total_items": total_items
            }
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@event_api_bp.route('/events/<string:event_id>', methods=['GET'])
def get_event_detail(event_id):
    try:
        event = event_model.get_by_id(event_id)
        if not event:
            return jsonify({"status": "error", "message": "Event tidak ditemukan"}), 404
        
        event['_id'] = str(event['_id'])
        event['banner_image_url'] = f"{request.host_url}static/img/events/{event.get('banner_image_url', 'default_event.png')}"
        
        if 'created_at' in event and event['created_at']:
            event['created_at'] = event['created_at'].strftime('%Y-%m-%d %H:%M:%S')

        return jsonify({
            "status": "success",
            "data": event
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500