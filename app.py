from flask import Flask
from config import Config
from extensions import mongo , jwt, bcrypt, mail
from routes.web.dashboard import web_bp
from routes.web.galeri import galeri_bp
from routes.api.galeri_api import api_bp
from routes.api.auth_api import auth_bp
from routes.api.chatbot_api import chatbot_bp
from utils.rag_utils import initialize_rag

app = Flask(__name__)
app.config.from_object(Config)
app.vector_db = initialize_rag("dataset")

# 1. Inisialisasi Database
mongo.init_app(app)
jwt.init_app(app)
bcrypt.init_app(app)
mail.init_app(app)

app.mongo = mongo
app.bcrypt = bcrypt
app.mail = mail

# 2. Register Blueprint
app.register_blueprint(web_bp)
app.register_blueprint(galeri_bp)

# 3. Register API Blueprint
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(chatbot_bp, url_prefix='/api/chatbot')


if __name__ == '__main__':
    app.run(debug=True)