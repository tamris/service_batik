import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from routes.web.auth import login_required
from bson.objectid import ObjectId
from datetime import datetime
from werkzeug.utils import secure_filename

# Bikin Blueprint nama 'web_dashboard'
web_bp = Blueprint('web_dashboard', __name__)

UPLOAD_AVATAR_FOLDER = 'static/img/avatars'

# ==========================================
# 1. GLOBAL CONTEXT PROCESSOR & JINJA FILTER
# ==========================================

@web_bp.app_context_processor
def inject_user_profile():
    """
    Menyuntikkan data user yang sedang login secara global ke SEMUA file HTML.
    Bisa langsung dipanggil di navbar lewat variabel: current_user_profile
    """
    user_id = session.get('user_id')
    if user_id:
        user_data = current_app.mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return dict(current_user_profile=user_data)
    return dict(current_user_profile=None)


def format_tgl_indo(date_str):
    """Fungsi helper kustom untuk memformat tanggal ISO menjadi teks Indonesia asli."""
    if not date_str:
        return "Segera Hadir"
    try:
        if 'T' in date_str:
            date_str = date_str.split('T')[0]
            
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        bulan_indo = [
            "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ]
        return f"{dt.day} {bulan_indo[dt.month]} {dt.year}"
    except Exception:
        return date_str


# ==========================================
# 2. ROUTE INDEKS DASHBOARD UTAMA
# ==========================================

@web_bp.route('/dashboard')
@login_required
def index():
    counts = {
        'batik_count': current_app.mongo.db.batiks.count_documents({"is_deleted": {"$ne": True}}),
        'users_count': current_app.mongo.db.users.count_documents({}),
        'artikel_count': current_app.mongo.db.informasi.count_documents({}),
        'event_count': current_app.mongo.db.events.count_documents({}),
        'video_count': current_app.mongo.db.videos.count_documents({}),     
        'mapping_count': current_app.mongo.db.mappings.count_documents({}), 
    }
    
    batik_terbaru = list(
        current_app.mongo.db.batiks.find({"is_deleted": {"$ne": True}})
        .sort("_id", -1)
        .limit(5)
    )
    
    event_terbaru = list(
        current_app.mongo.db.events.find({})
        .sort("created_at", -1)
        .limit(3)
    )
    
    if 'tgl_indo' not in current_app.jinja_env.filters:
        current_app.jinja_env.filters['tgl_indo'] = format_tgl_indo

    return render_template(
        'dashboard.html', 
        batik_terbaru=batik_terbaru,
        event_terbaru=event_terbaru,  
        **counts
    )


# ==========================================
# 3. ROUTE HALAMAN PROFILE ADMIN (PRIBADI)
# ==========================================

@web_bp.route('/dashboard/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session.get('user_id')
    user_data = current_app.mongo.db.users.find_one({"_id": ObjectId(user_id)})

    if request.method == 'POST':
        action = request.form.get('action')
        bcrypt = current_app.bcrypt
        
        # A. LOGIKA GANTI PROFILE PICTURE ADMIN
        if action == 'update_avatar':
            file = request.files.get('avatar')
            if file and file.filename != '':
                filename = secure_filename(f"avatar_{user_id}_{file.filename}")
                if not os.path.exists(UPLOAD_AVATAR_FOLDER):
                    os.makedirs(UPLOAD_AVATAR_FOLDER)
                
                file.save(os.path.join(UPLOAD_AVATAR_FOLDER, filename))
                
                current_app.mongo.db.users.update_one(
                    {"_id": ObjectId(user_id)}, 
                    {"$set": {"profile_picture": filename}}
                )
                
                flash('Foto profil berhasil diperbarui!', 'success')
            else:
                flash('Pilih file gambar terlebih dahulu.', 'error')

        # B. LOGIKA GANTI PASSWORD ADMIN
        elif action == 'update_password':
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            if not new_password or not confirm_password:
                flash('Password tidak boleh kosong!', 'error')
            elif new_password != confirm_password:
                flash('Konfirmasi password tidak cocok!', 'error')
            else:
                hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
                
                current_app.mongo.db.users.update_one(
                    {"_id": ObjectId(user_id)}, 
                    {"$set": {"password": hashed_password}}
                )
                flash('Password berhasil diubah!', 'success')

        return redirect(url_for('web_dashboard.profile'))

    return render_template('profile.html', user=user_data)