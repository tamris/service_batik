from flask import Blueprint, render_template

# Bikin Blueprint nama 'web_dashboard'
web_bp = Blueprint('web_dashboard', __name__)

@web_bp.route('/')
def index():
    # Ini return HTML buat dilihat di Browser Laptop
    return render_template('dashboard.html')

