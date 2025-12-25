from flask import Flask
from config import Config
from flask_pymongo import PyMongo
from routes.web.dashboard import web_bp
from routes.web.galeri import galeri_bp


app = Flask(__name__)


app.config.from_object(Config)
mongo = PyMongo(app)


# --- REGISTER BLUEPRINT ---
app.register_blueprint(web_bp)
app.register_blueprint(galeri_bp)


# 2. Register API (Mobile)
# url_prefix '/api' artinya semua akses harus pake /api (localhost:5000/api/list-batik)
# app.register_blueprint(api_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)