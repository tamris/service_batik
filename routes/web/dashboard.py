import os
import re
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
        if isinstance(date_str, datetime):
            dt = date_str
        else:
            date_str = str(date_str)
            if 'T' in date_str:
                date_str = date_str.split('T')[0]
            dt = datetime.strptime(date_str, "%Y-%m-%d")

        bulan_indo = [
            "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ]
        return f"{dt.day} {bulan_indo[dt.month]} {dt.year}"
    except Exception:
        return str(date_str)


@web_bp.app_template_filter('tgl_indo')
def tgl_indo_filter(date_str):
    """Registrasi filter Jinja global: {{ value|tgl_indo }}"""
    return format_tgl_indo(date_str)


def is_strong_password(password: str) -> bool:
    """
    Minimal 8 karakter, mengandung:
    - huruf besar
    - huruf kecil
    - angka
    """
    if not password or len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    return True


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

        # B. LOGIKA GANTI PASSWORD ADMIN (PAKAI VERIFIKASI PASSWORD LAMA)
        elif action == 'update_password':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            if not current_password or not new_password or not confirm_password:
                flash('Semua field password wajib diisi!', 'error')
            elif not user_data or not user_data.get('password'):
                flash('Data akun tidak valid. Silakan login ulang.', 'error')
            elif not bcrypt.check_password_hash(user_data.get('password', ''), current_password):
                flash('Password lama salah!', 'error')
            elif new_password != confirm_password:
                flash('Konfirmasi password tidak cocok!', 'error')
            elif current_password == new_password:
                flash('Password baru tidak boleh sama dengan password lama!', 'error')
            elif not is_strong_password(new_password):
                flash('Password minimal 8 karakter dan wajib mengandung huruf besar, huruf kecil, serta angka!', 'error')
            else:
                hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

                current_app.mongo.db.users.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": {"password": hashed_password}}
                )

                flash('Password berhasil diubah!', 'success')

        return redirect(url_for('web_dashboard.profile'))

    return render_template('profile.html', user=user_data)