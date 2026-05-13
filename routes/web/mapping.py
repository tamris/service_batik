import os
import math
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.web.auth import login_required
from models.mapping_model import MappingModel
from bson.objectid import ObjectId

mapping_bp = Blueprint('mapping', __name__)
mapping_model = MappingModel()

UPLOAD_FOLDER = 'static/img/mapping'

@mapping_bp.route('/mapping-lokasi')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '')
    per_page = 5
    
    all_data = mapping_model.get_all(search_query)

    total_items = len(all_data)
    total_pages = math.ceil(total_items / per_page)
    
    start = (page - 1) * per_page
    end = start + per_page
    data_tampil = all_data[start:end]
    
    start_index = start + 1 if total_items > 0 else 0
    end_index = min(end, total_items)

    return render_template('mapping/index.html', 
                           mappings=data_tampil, 
                           page=page, 
                           total_pages=total_pages,
                           total_items=total_items,
                           start_index=start_index,
                           end_index=end_index,
                           search_query=search_query)

@mapping_bp.route('/mapping-lokasi/tambah', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        # Handle Upload Gambar
        file = request.files.get('image_url')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            image_url = filename
        else:
            image_url = 'default_map.png'

        # Susun data sesuai skema database kamu
        data_baru = {
            "user_id": ObjectId(session.get('user_id')), # KUNCI: Track siapa yang buat
            "name": request.form['name'],
            "description": request.form['description'],
            "category": request.form['category'],
            "latitude": request.form['latitude'],
            "longitude": request.form['longitude'],
            "address": {
                "full": request.form['address_full']
            },
            "image_url": image_url,
            "created_at": datetime.now(),
            "update_at": datetime.now()
        }

        mapping_model.create(data_baru)
        flash('Data Lokasi berhasil ditambahkan!', 'success')
        return redirect(url_for('mapping.index'))

    return render_template('mapping/create.html')

@mapping_bp.route('/mapping-lokasi/edit/<string:mapping_id>', methods=['GET', 'POST'])
@login_required
def edit(mapping_id):
    mapping_terpilih = mapping_model.get_by_id(mapping_id)

    if not mapping_terpilih:
        flash('Data tidak ditemukan!', 'error')
        return redirect(url_for('mapping.index'))

    if request.method == 'POST':
        page = request.form.get('page', 1, type=int)
        
        data_update = {
            "name": request.form['name'],
            "description": request.form['description'],
            "category": request.form['category'],
            "latitude": request.form['latitude'],
            "longitude": request.form['longitude'],
            "address": {
                "full": request.form['address_full']
            },
            "update_at": datetime.now()
        }
        
        # Jika gambar diganti
        file = request.files.get('image_url')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            data_update['image_url'] = filename
        
        mapping_model.update(mapping_id, data_update)
        flash('Data Lokasi berhasil diperbarui!', 'success')
        return redirect(url_for('mapping.index', page=page))

    return render_template('mapping/edit.html', mapping=mapping_terpilih)

@mapping_bp.route('/mapping-lokasi/hapus/<string:mapping_id>', methods=['POST'])
@login_required
def delete(mapping_id):
    # 1. Cari data lokasinya dulu
    mapping = mapping_model.get_by_id(mapping_id)
    
    if mapping:
        # 2. Hapus file fotonya dari folder static (Kecuali kalau dia pakai gambar default)
        if mapping.get('image_url') and mapping['image_url'] != 'default_map.png':
            image_path = os.path.join(UPLOAD_FOLDER, mapping['image_url'])
            # Cek apakah filenya beneran ada di dalam folder
            if os.path.exists(image_path):
                os.remove(image_path)
                
        # 3. Hapus data dari MongoDB
        mapping_model.delete(mapping_id)
        flash('Data lokasi beserta gambarnya berhasil dihapus!', 'success')
    else:
        flash('Data tidak ditemukan!', 'error')
        
    # Redirect kembali ke halaman index dengan membawa nomor page terakhir
    page = request.args.get('page', 1, type=int)
    return redirect(url_for('mapping.index', page=page))