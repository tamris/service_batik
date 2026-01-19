from flask import Blueprint, request, jsonify, current_app
from models.chatbot_model import ChatbotModel

chatbot_bp = Blueprint('chatbot_api', __name__)

@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({"error": "Pesan tidak boleh kosong"}), 400

    try:
        # Ambil vector_db yang sudah diinisialisasi di app.py
        vector_db = getattr(current_app, 'vector_db', None)
        bot = ChatbotModel(vector_db=vector_db)
        
        reply = bot.ask_ai(user_message)
        return jsonify({"reply": reply}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500