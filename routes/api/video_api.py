from flask import Blueprint, request, jsonify
from models.video_model import VideoModel
import math

video_api_bp = Blueprint('video_api', __name__)
video_model = VideoModel()

@video_api_bp.route('/video', methods=['GET'])
def get_all_videos():
    try:
        # 1. Parameter Pagination & Search
        page = request.args.get('page', 1, type=int)
        search_query = request.args.get('q', '')
        per_page = 6  # Sesuaikan jumlah video per halaman

        # 2. Ambil data dari MongoDB
        all_data = video_model.get_all(search_query)

        # 3. Logika Pagination
        total_items = len(all_data)
        total_pages = math.ceil(total_items / per_page)
        
        start = (page - 1) * per_page
        end = start + per_page
        data_tampil = all_data[start:end]

        # 4. Formatting data untuk JSON
        formatted_videos = []
        for v in data_tampil:
            v['_id'] = str(v['_id'])
            # Jika ada field created_at yang bertipe datetime, ubah ke string
            if 'created_at' in v and v['created_at']:
                v['created_at'] = v['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            formatted_videos.append(v)

        return jsonify({
            "status": "success",
            "message": "Data video berhasil dimuat",
            "data": formatted_videos,
            "meta": {
                "current_page": page,
                "total_pages": total_pages,
                "total_items": total_items
            }
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# @video_api_bp.route('/video/<string:video_id>', methods=['GET'])
# def get_video_detail(video_id):
#     try:
#         video = video_model.get_by_id(video_id)
#         if not video:
#             return jsonify({"status": "error", "message": "Video tidak ditemukan"}), 404
        
#         video['_id'] = str(video['_id'])
#         if 'created_at' in video and video['created_at']:
#             video['created_at'] = video['created_at'].strftime('%Y-%m-%d %H:%M:%S')

#         return jsonify({
#             "status": "success",
#             "data": video
#         }), 200
#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 500