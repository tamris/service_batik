from datetime import datetime
import math
import os
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
    per_page = 7
    
    # Ambil data dari MongoDB berdasarkan pencarian
    all_data = batik_model.get_all(search_query)

    total_items = len(all_data)
    total_pages = math.ceil(total_items / per_page)
    
    start = (page - 1) * per_page
    end = start + per_page
    data_tampil = all_data[start:end]
    
    start_index = start + 1 if total_items > 0 else 0
    end_index = min(end, total_items)

    print("SESSION FLASH:", session.get('_flashes'))

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
        # Ubah gambar menjadi image_url[cite: 7]
        file = request.files.get('image_url') 
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            image_url = filename
        else:
            image_url = 'default_batik.png'
            
        data_baru = {
            "name": request.form['name'], # Ubah nama menjadi name[cite: 7]
            "category": request.form['category'], # Tambahan field category[cite: 7]
            "makna": request.form['makna'],
            "image_url": image_url, # Ubah gambar menjadi image_url[cite: 7]
            "created_at": datetime.now()
        }

        batik_model.create(data_baru)
        flash('Data batik berhasil ditambahkan!', 'success')
        return redirect(url_for('galeri.index'))

    return render_template('galeri/create.html')

@galeri_bp.route('/data-batik/edit/<string:batik_id>', methods=['GET', 'POST'])
def edit(batik_id):
    batik_terpilih = batik_model.get_by_id(batik_id)

    if not batik_terpilih:
        flash('Data tidak ditemukan!', 'danger')
        return redirect(url_for('galeri.index'))

    if request.method == 'POST':
        page = request.form.get('page', 1, type=int)
        data_update = {
            "name": request.form['name'], # Ubah penangkapan update ke name[cite: 7]
            "category": request.form['category'], # Buka comment ini nanti kalau form edit juga ditambah category
            "makna": request.form['makna']
        }
        
        # Ubah gambar menjadi image_url[cite: 7]
        gambar_file = request.files.get('image_url') 
        if gambar_file and gambar_file.filename != '':
            filename = secure_filename(gambar_file.filename)
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            gambar_file.save(os.path.join(UPLOAD_FOLDER, filename))
            data_update['image_url'] = filename # Update field image_url[cite: 7]
        
        batik_model.update(batik_id, data_update)
        flash('Data batik berhasil diperbarui!', 'success')
        return redirect(url_for('galeri.index', page=page))

    return render_template('galeri/edit.html', batik=batik_terpilih)

@galeri_bp.route('/data-batik/hapus/<string:batik_id>')
def delete(batik_id):
    batik_model.delete(batik_id)
    flash('Data batik berhasil dihapus!', 'success')
    return redirect(url_for('galeri.index'))