from flask import Flask
from config import Config
from extensions import mongo , jwt, bcrypt, mail
from routes.web.dashboard import web_bp
from routes.web.auth import auth_web
from routes.web.galeri import galeri_bp
from routes.web.infromasi import informasi_bp
from routes.web.video import video_bp
from routes.web.user_manager import user_bp
from routes.web.mapping import mapping_bp
from routes.web.event import event_bp
from routes.api.galeri_api import galeri_api_bp
from routes.api.informasi_api import informasi_api_bp
from routes.api.auth_api import auth_bp
from routes.api.google_oauth import google_oauth_bp
from routes.api.deteksi import deteksi_bp
from routes.api.chatbot_api import chatbot_bp
from routes.api.video_api import video_api_bp
from routes.api.event_api import event_api_bp
from routes.api.maping_api import mapping_api_bp
from routes.api.studio_api import studio_api_bp
from routes.api.user_api import user_api_bp
from routes.api.batik_interaction import interaction_bp
from utils.rag_utils import initialize_rag

app = Flask(__name__)
app.config.from_object(Config)
app.vector_db = initialize_rag("dataset")

# 1. Inisialisasi Database
mongo.init_app(app)
with app.app_context():
    mongo.db.events.create_index([("location", "2dsphere")])
    mongo.db.events.create_index("schedule.start_datetime")
jwt.init_app(app)
bcrypt.init_app(app)
mail.init_app(app)

app.mongo = mongo
app.bcrypt = bcrypt
app.mail = mail

# 2. Register Blueprint
app.register_blueprint(web_bp)
app.register_blueprint(auth_web)
app.register_blueprint(galeri_bp)
app.register_blueprint(informasi_bp)
app.register_blueprint(video_bp)
app.register_blueprint(event_bp)    
app.register_blueprint(mapping_bp) 
app.register_blueprint(user_bp)

# 3. Register API Blueprint
app.register_blueprint(galeri_api_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_api_bp, url_prefix='/api/user')
app.register_blueprint(chatbot_bp, url_prefix='/api/chatbot')
app.register_blueprint(deteksi_bp, url_prefix='/api/deteksi')
app.register_blueprint(google_oauth_bp, url_prefix='/api/oauth')
app.register_blueprint(informasi_api_bp, url_prefix='/api')
app.register_blueprint(video_api_bp, url_prefix='/api')
app.register_blueprint(event_api_bp, url_prefix='/api')
app.register_blueprint(mapping_api_bp, url_prefix='/api')
app.register_blueprint(studio_api_bp, url_prefix='/api')
app.register_blueprint(interaction_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)