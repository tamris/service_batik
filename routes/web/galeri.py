from datetime import datetime
import math
import os

from bson.objectid import ObjectId
from routes.web.auth import login_required
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.batik_model import BatikModel
from flask import session

galeri_bp = Blueprint('galeri', __name__)
batik_model = BatikModel()

UPLOAD_FOLDER = 'static/img/galeri'

@galeri_bp.route('/data-batik')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '')
    per_page = 10
    
    # 💡 KITA PAKAI METHOD UTAMA LU: Ambil semua data (aktif & nonaktif)
   # Di dalam file routes/web/galeri.py bagian def index()
    all_data = batik_model.get_all(search_query, include_deleted=True) # 💡 Tambahkan parameter True

    total_items = len(all_data)
    total_pages = math.ceil(total_items / per_page)
    
    start = (page - 1) * per_page
    end = start + per_page
    data_tampil = all_data[start:end]
    
    start_index = start + 1 if total_items > 0 else 0
    end_index = min(end, total_items)

    return render_template('galeri/index.html', 
                           batiks=data_tampil, 
                           page=page, 
                           total_pages=total_pages,
                           total_items=total_items,
                           start_index=start_index,
                           end_index=end_index,
                           search_query=search_query)

@galeri_bp.route('/data-batik/tambah', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        # Kembali menggunakan image_url sesuai database kamu
        file = request.files.get('image_url') 
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            image_url = filename
        else:
            image_url = 'default_batik.png'

        colors = [
            request.form.get('dominant_color_1'),
            request.form.get('dominant_color_2'),
            request.form.get('dominant_color_3'),
            request.form.get('dominant_color_4')
        ]
        dominant_colors_array = [c for c in colors if c]
            
        data_baru = {
            "user_id": ObjectId(session.get('user_id')),
            "name": request.form['name'],
            "category": request.form['category'],
            "makna": request.form['makna'],
            "philosophy": request.form['philosophy'],
            "technique": request.form['technique'],
            "history": request.form['history'],
            "image_url": image_url,  # Tetap image_url
            "dominant_color": dominant_colors_array,
            "created_at": datetime.now(),
            "is_deleted": False
        }

        batik_model.create(data_baru)
        flash('Data batik berhasil ditambahkan!', 'success')
        return redirect(url_for('galeri.index'))

    return render_template('galeri/create.html')

@galeri_bp.route('/data-batik/edit/<string:batik_id>', methods=['GET', 'POST'])
@login_required
def edit(batik_id):
    batik_terpilih = batik_model.get_by_id(batik_id)

    if not batik_terpilih:
        flash('Data tidak ditemukan!', 'danger')
        return redirect(url_for('galeri.index'))

    if request.method == 'POST':
        page = request.form.get('page', 1, type=int)
        
        colors = [
            request.form.get('dominant_color_1'),
            request.form.get('dominant_color_2'),
            request.form.get('dominant_color_3'),
            request.form.get('dominant_color_4')
        ]
        dominant_colors_array = [c for c in colors if c]

        data_update = {
            "name": request.form['name'],
            "category": request.form['category'],
            "makna": request.form['makna'],
            "philosophy": request.form['philosophy'],
            "technique": request.form['technique'],
            "history": request.form['history'],
            "dominant_color": dominant_colors_array
        }
        
        gambar_file = request.files.get('image_url') 
        if gambar_file and gambar_file.filename != '':
            filename = secure_filename(gambar_file.filename)
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            gambar_file.save(os.path.join(UPLOAD_FOLDER, filename))
            data_update['image_url'] = filename  # Tetap image_url
        
        batik_model.update(batik_id, data_update)
        flash('Data batik berhasil diperbarui!', 'success')
        return redirect(url_for('galeri.index', page=page))

    return render_template('galeri/edit.html', batik=batik_terpilih)

@galeri_bp.route('/data-batik/hapus/<string:batik_id>')
@login_required
def delete(batik_id):
    batik_model.delete(batik_id)
    flash('Data batik berhasil dinonaktifkan!', 'success')
    return redirect(url_for('galeri.index'))

@galeri_bp.route('/data-batik/restore/<string:batik_id>')
@login_required
def restore(batik_id):
    batik_model.restore(batik_id)
    flash('Data batik berhasil diaktifkan kembali!', 'success')
    return redirect(url_for('galeri.index'))