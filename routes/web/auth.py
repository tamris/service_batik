from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from functools import wraps
from flask import session, redirect, url_for, flash

auth_web = Blueprint('auth', __name__)

@auth_web.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email') # Ambil email dari form
        password = request.form.get('password')
        
        # Cari user berdasarkan email sesuai user_model.py
        user = current_app.mongo.db.users.find_one({"email": email})
        
        if user and current_app.bcrypt.check_password_hash(user['password'], password):
            # Cek Role: Hanya admin/superadmin yang bisa masuk web admin
            if user.get('role') in ['superadmin', 'admin']:
                session['logged_in'] = True
                session['user_id'] = str(user['_id'])
                session['username'] = user['username']
                session['role'] = user.get('role')
                
                flash('Login Berhasil!', 'success')
                return redirect(url_for('web_dashboard.index'))
            else:
                flash('Akses Ditolak: Anda tidak memiliki otoritas Admin.', 'danger')
        else:
            flash('Email atau Password salah!', 'danger')
            
    return render_template('auth.html')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Cek apakah user sudah login
        if 'logged_in' not in session:
            flash("Silahkan login terlebih dahulu untuk mengakses halaman ini.", "danger")
            return redirect(url_for('auth.login'))
        
        # 2. Cek apakah role-nya Admin atau Superadmin
        # Ini mencegah user mobile yang punya akun tapi role 'users' masuk lewat URL web
        if session.get('role') not in ['admin', 'superadmin']:
            flash("Akses ditolak! Anda tidak memiliki izin admin.", "danger")
            return redirect(url_for('auth.login'))
            
        return f(*args, **kwargs)
    return decorated_function


@auth_web.route('/logout')
def logout():
    session.clear() 
    # Tambahkan kategori "success" di sini agar HTML tidak error saat unpacking
    flash("Anda telah berhasil keluar.", "success") 
    return redirect(url_for('auth.login'))