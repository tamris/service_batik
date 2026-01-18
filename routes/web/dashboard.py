from flask import Blueprint, render_template

# Bikin Blueprint nama 'web_dashboard'
web_bp = Blueprint('web_dashboard', __name__)

@web_bp.route('/')
def index():
    # Dummy counts (gampang diganti nanti dari database)
    counts = {
        'users_count': 120,
        'batik_count': 64,
        'artikel_count': 85,
        'event_count': 12,
        'video_count': 38,
        'mapping_count': 5,
    }
    return render_template('dashboard.html', **counts)

