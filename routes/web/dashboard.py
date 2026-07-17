import os
import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from sympy import sec
from routes.web.auth import login_required
from bson.objectid import ObjectId
from datetime import datetime, timedelta  # <- update import
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

def waktu_lalu_indo(value):
    """Human readable time in Indonesian, contoh: '2 jam lalu'."""
    if not value:
        return "Baru saja"

    try:
        if isinstance(value, datetime):
            dt = value
        else:
            s = str(value).strip()
            # handle ISO string
            if "T" in s:
                s = s.replace("Z", "")
                try:
                    dt = datetime.fromisoformat(s)
                except Exception:
                    dt = datetime.strptime(s.split("T")[0], "%Y-%m-%d")
            else:
                # fallback YYYY-MM-DD
                dt = datetime.strptime(s[:10], "%Y-%m-%d")
    except Exception:
        return "Baru saja"

    now = datetime.now() 
    diff = now - dt
    sec = int(diff.total_seconds())

    if sec < 60:
        return "Baru saja"
    if sec < 3600:
        m = sec // 60
        return f"{m} menit lalu"
    if sec < 86400:
        h = sec // 3600
        return f"{h} jam lalu"
    if sec < 2592000:
        d = sec // 86400
        return f"{d} hari lalu"
    if sec < 31104000:
        mo = sec // 2592000
        return f"{mo} bulan lalu"
    y = sec // 31104000
    return f"{y} tahun lalu"


# ==========================================
# 2. ROUTE INDEKS DASHBOARD UTAMA
# ==========================================

@web_bp.route('/dashboard')
@login_required
def index():
   # 1. Tentukan tanggal awal bulan ini (Jam 00:00:00)
    now = datetime.utcnow()
    awal_bulan = datetime(now.year, now.month, 1)

    # 2. Query total seluruh data (Statistik Utama)
    counts = {
        'batik_count': current_app.mongo.db.batiks.count_documents({"is_deleted": {"$ne": True}}),
        'users_count': current_app.mongo.db.users.count_documents({}),
        'artikel_count': current_app.mongo.db.informasi.count_documents({}),
        'event_count': current_app.mongo.db.events.count_documents({}),
        'video_count': current_app.mongo.db.videos.count_documents({}),
        'mapping_count': current_app.mongo.db.mappings.count_documents({}),
    }

    # 3. Masukkan dictionary 'growth' langsung ke dalam 'counts' agar ikut dibongkar oleh **counts
    growth = {
        'users_growth': current_app.mongo.db.users.count_documents({"created_at": {"$gte": awal_bulan}}),
        'batik_growth': current_app.mongo.db.batiks.count_documents({"created_at": {"$gte": awal_bulan}, "is_deleted": {"$ne": True}}),
        'artikel_growth': current_app.mongo.db.informasi.count_documents({"created_at": {"$gte": awal_bulan}}),
        'event_growth': current_app.mongo.db.events.count_documents({"created_at": {"$gte": awal_bulan}}),
        'video_growth': current_app.mongo.db.videos.count_documents({"created_at": {"$gte": awal_bulan}}),
        'mapping_growth': current_app.mongo.db.mappings.count_documents({"created_at": {"$gte": awal_bulan}}),
    }

    batik_terbaru = list(
        current_app.mongo.db.batiks.find({"is_deleted": {"$ne": True}})
        .sort("_id", -1)
        .limit(5)
    )

    # Tetap bisa dipakai kalau masih dibutuhkan di tempat lain
    # event_terbaru = list(
    #     current_app.mongo.db.events.find({})
    #     .sort("created_at", -1)
    #     .limit(3)
    # )

    # ===============================
    # AKTIVITAS TERBARU (Lintas Modul)
    # ===============================
    aktivitas = []

    # Artikel
    for d in current_app.mongo.db.informasi.find({}).sort("_id", -1).limit(8):
        created = d.get("created_at") or d.get("updated_at") or d.get("date")
        aktivitas.append({
            "tipe": "Artikel",
            "icon": "bx bxs-news",
            "warna": "artikel",
            "judul": d.get("title") or d.get("judul") or "Artikel baru",
            "waktu": created,
            "link": url_for("informasi.index")
        })

    # Event
    for d in current_app.mongo.db.events.find({}).sort("_id", -1).limit(8):
        created = d.get("created_at") or d.get("updated_at") or d.get("event_date")
        aktivitas.append({
            "tipe": "Event",
            "icon": "bx bxs-calendar-event",
            "warna": "event",
            "judul": d.get("title") or d.get("name") or "Event baru",
            "waktu": created,
            "link": url_for("event.index")
        })

    # Video
    for d in current_app.mongo.db.videos.find({}).sort("_id", -1).limit(8):
        created = d.get("created_at") or d.get("updated_at")
        aktivitas.append({
            "tipe": "Video",
            "icon": "bx bxs-video",
            "warna": "video",
            "judul": d.get("title") or d.get("judul") or "Video baru",
            "waktu": created,
            "link": url_for("video.index")
        })

    # Mapping
    for d in current_app.mongo.db.mappings.find({}).sort("_id", -1).limit(8):
        created = d.get("created_at") or d.get("updated_at")
        aktivitas.append({
            "tipe": "Mapping",
            "icon": "bx bxs-map",
            "warna": "mapping",
            "judul": d.get("title") or d.get("nama") or d.get("name") or "Lokasi baru",
            "waktu": created,
            "link": url_for("mapping.index")
        })

    # User (opsional, terutama superadmin)
    for d in current_app.mongo.db.users.find({}).sort("_id", -1).limit(8):
        created = d.get("created_at")
        aktivitas.append({
            "tipe": "User",
            "icon": "bx bxs-user",
            "warna": "user",
            "judul": d.get("username") or d.get("name") or "User baru",
            "waktu": created,
            "link": url_for("user_manager.index") if session.get("role") == "superadmin" else "#"
        })

    def sort_key(x):
        w = x.get("waktu")
        if isinstance(w, datetime):
            return w
        return datetime.min

    aktivitas = sorted(aktivitas, key=sort_key, reverse=True)[:8]

    for item in aktivitas:
        # Panggil fungsi konversi string bawaan kamu
        item["waktu_lalu"] = waktu_lalu_indo(item.get("waktu"))
        
        # Best Practice: Konversi datetime objek ke ISO 8601 string sebelum dikirim ke HTML
        waktu_obj = item.get("waktu")
        if isinstance(waktu_obj, datetime):
            item["waktu_iso"] = waktu_obj.isoformat()
        elif waktu_obj:
            item["waktu_iso"] = str(waktu_obj)
        else:
            item["waktu_iso"] = ""

    
    # waktu_sekarang_iso = datetime.now().isoformat()

    return render_template(
        'dashboard.html',
        batik_terbaru=batik_terbaru,
        # event_terbaru=event_terbaru,
        aktivitas_terbaru=aktivitas,
        growth=growth,
        # waktu_sekarang_iso=waktu_sekarang_iso,
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