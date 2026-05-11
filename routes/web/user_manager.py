import math
import secrets
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.web.auth import login_required
from models.user_model import get_all_users, get_user_by_id, create_user, update_admin

user_bp = Blueprint('user_manager', __name__)

# DECORATOR KHUSUS SUPERADMIN
def superadmin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'superadmin':
            flash('Akses Ditolak! Hanya Superadmin yang diizinkan mengelola pengguna.', 'error')
            return redirect(url_for('web_dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

@user_bp.route('/users-manager')
@login_required
@superadmin_required
def index():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '')
    # TANGKAP PARAMETER ROLE DARI URL
    role_filter = request.args.get('role', 'all') 
    
    # Ambil semua data user dari model
    all_users = get_all_users(search_query) 
    
    # FILTER KASTA (ROLE) DI PYTHON
    if role_filter != 'all':
        # Saring hanya user yang rolenya sesuai pilihan dropdown
        all_users = [u for u in all_users if u.get('role', 'users') == role_filter]
    
    # --- LOGIKA PAGINATION ---
    per_page = 10 # Sesuaikan dengan jumlah datamu per halaman
    total_items = len(all_users)
    total_pages = math.ceil(total_items / per_page)
    
    start = (page - 1) * per_page
    end = start + per_page
    users_tampil = all_users[start:end]
    
    start_index = start + 1 if total_items > 0 else 0
    end_index = min(end, total_items)
    
    return render_template('users/index.html', 
                           users=users_tampil, 
                           page=page, 
                           total_pages=total_pages,
                           total_items=total_items,
                           start_index=start_index,
                           end_index=end_index,
                           search_query=search_query,
                           role_filter=role_filter) # Jangan lupa lempar ke template

@user_bp.route('/users-manager/tambah-admin', methods=['GET', 'POST'])
@login_required
@superadmin_required
def create():
    if request.method == 'POST':
        # Sesuaikan dengan dictionary yang dibutuhkan model create_user
        data_baru = {
            "username": request.form['username'], # Pakai username[cite: 8]
            "email": request.form['email'],
            "password": request.form['password'], # Raw password, biar di-hash oleh model
            "role": "admin", 
            "api_key": secrets.token_hex(16), # Generate API key unik
            "is_verified": True # Langsung terverifikasi
        }
        
        create_user(data_baru) # Panggil fungsi dari model kamu[cite: 8]
        flash('Akun Admin berhasil ditambahkan!', 'success')
        return redirect(url_for('user_manager.index'))

    return render_template('users/create.html')

@user_bp.route('/users-manager/edit/<string:user_id>', methods=['GET', 'POST'])
@login_required
@superadmin_required
def edit(user_id):
    user_terpilih = get_user_by_id(user_id)
    
    # Proteksi ganda: Jangan sampai URL dipakai buat ngedit user biasa
    if user_terpilih and user_terpilih.get('role') == 'users':
        flash('Tidak dapat mengedit data User biasa!', 'warning')
        return redirect(url_for('user_manager.index'))

    if request.method == 'POST':
        page = request.form.get('page', 1, type=int)
        
        data_update = {
            "username": request.form['username'],
            "email": request.form['email']
        }
        
        # Jika ada input password baru
        new_password = request.form.get('password')
        if new_password:
            data_update['password'] = new_password
            
        update_admin(user_id, data_update)
        flash('Data Admin berhasil diperbarui!', 'success')
        return redirect(url_for('user_manager.index', page=page))

    return render_template('users/edit.html', user=user_terpilih)