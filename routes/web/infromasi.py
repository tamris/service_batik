from datetime import datetime
import math
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from models.informasi_model import InformasiModel

# 1. Pastikan nama Blueprint adalah 'informasi' agar url_for('informasi.edit') jalan
informasi_bp = Blueprint('informasi', __name__)
info_model = InformasiModel()

UPLOAD_FOLDER = 'static/img/informasi'

@informasi_bp.route('/data-informasi')
def index():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '')
    per_page = 5 

    all_data = info_model.get_all(search_query)

    # TIPS: Agar data yang baru dibuat muncul paling atas, 
    # pastikan di Model kamu melakukan sorting berdasarkan 'created_at': -1
    
    total_items = len(all_data)
    total_pages = math.ceil(total_items / per_page)
    
    start = (page - 1) * per_page
    end = start + per_page
    data_tampil = all_data[start:end]
    
    start_index = start + 1 if total_items > 0 else 0
    end_index = min(end, total_items)

    return render_template('informasi/index.html', 
                           informasi=data_tampil, 
                           page=page, 
                           total_pages=total_pages,
                           total_items=total_items,
                           start_index=start_index,
                           end_index=end_index,
                           search_query=search_query)

@informasi_bp.route('/data-informasi/tambah', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        file = request.files.get('gambar')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            gambar_url = filename
        else:
            gambar_url = 'default_info.png'

        # 2. MASUKKAN created_at DI SINI
        data_baru = {
            "judul": request.form['judul'],
            "deskripsi": request.form['deskripsi'],
            "kategori": request.form['kategori'],
            "gambar_url": gambar_url,
            "created_at": datetime.now() # Ini akan mencatat waktu saat tombol simpan diklik
        }
        
        info_model.create(data_baru)
        flash('Informasi berhasil ditambahkan!', 'success')
        return redirect(url_for('informasi.index'))
    return render_template('informasi/create.html')

# 2. INI RUTE YANG ERROR TADI: Pastikan nama fungsinya 'edit' dan parameternya 'info_id'
@informasi_bp.route('/data-informasi/edit/<string:info_id>', methods=['GET', 'POST'])
def edit(info_id):
    info_terpilih = info_model.get_by_id(info_id)
    if not info_terpilih:
        flash('Data tidak ditemukan!', 'danger')
        return redirect(url_for('informasi.index'))

    if request.method == 'POST':
        data_update = {
            "judul": request.form['judul'],
            "deskripsi": request.form['deskripsi'],
            "kategori": request.form['kategori']
        }
        
        file = request.files.get('gambar')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            data_update['gambar_url'] = filename
        
        info_model.update(info_id, data_update)
        flash('Informasi berhasil diperbarui!', 'success')
        return redirect(url_for('informasi.index'))
        
    return render_template('informasi/edit.html', info=info_terpilih)

@informasi_bp.route('/data-informasi/hapus/<string:info_id>')
def delete(info_id):
    info_model.delete(info_id)
    flash('Informasi berhasil dihapus!', 'success')
    return redirect(url_for('informasi.index'))