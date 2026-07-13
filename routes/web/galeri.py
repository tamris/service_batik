from datetime import datetime
import math
import os
import cv2 
import numpy as np

from bson.objectid import ObjectId
from routes.web.auth import login_required
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.batik_model import BatikModel

galeri_bp = Blueprint('galeri', __name__)
batik_model = BatikModel()

UPLOAD_FOLDER = 'static/img/galeri'

# 🛠️ FUNGSI FILTER OPENCV PREMIUM TRANSPARAN (FIXED PATH & UNIQUE NAME)
def generate_premium_sketch(input_path, output_filename):
    img = cv2.imread(input_path)
    if img is None:
        return False
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    inverted = 255 - gray
    blurred = cv2.GaussianBlur(inverted, (21, 21), 0)
    sketch = cv2.divide(gray, 255 - blurred, scale=256)
    
    # Mengubah background menjadi transparan (PNG 4-Channel)
    rgba = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    rgba[:, :, 3] = np.where(sketch > 240, 0, 255)
    
    rgba[:, :, 0] = 50 # Blue
    rgba[:, :, 1] = 50 # Green
    rgba[:, :, 2] = 50 # Red
    
    TARGET_SKETCH_FOLDER = 'static/img/sketch'
    if not os.path.exists(TARGET_SKETCH_FOLDER):
        os.makedirs(TARGET_SKETCH_FOLDER)
    
    output_path = os.path.join(TARGET_SKETCH_FOLDER, output_filename)
    cv2.imwrite(output_path, rgba) 
    return True


@galeri_bp.route('/data-batik')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '')
    selected_category = request.args.get('c', '') # Ambil dari dropdown filter
    per_page = 10
    
    # Memanggil fungsi get_all dengan parameter category baru yang sudah ditambahkan di model
    all_data = batik_model.get_all(search_query=search_query, category=selected_category, include_deleted=True)

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
                           search_query=search_query,
                           selected_category=selected_category) # Jangan lupa lempar ke template


@galeri_bp.route('/data-batik/tambah', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        file = request.files.get('image_url')
        image_url = 'default_batik.png'
        sketch_image_url = ''
        is_sketsa_available = False

        is_sketch_requested = request.form.get('activate_sketch') == 'true'

        if file and file.filename != '':
            filename = secure_filename(file.filename)
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            
            full_input_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(full_input_path)
            image_url = filename

            if is_sketch_requested:
                name_part, ext_part = os.path.splitext(filename)
                
                # 💡 SEED UNIK 1: Tambahkan format waktu unik saat data batik dibuat baru
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                sketch_filename = f"{name_part}_sketch_{timestamp}.png"

                sketch_success = generate_premium_sketch(full_input_path, sketch_filename)
                if sketch_success:
                    sketch_image_url = sketch_filename
                    is_sketsa_available = True

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
            "image_url": image_url, 
            "sketch_image_url": sketch_image_url, 
            "is_sketsa_available": is_sketsa_available,
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

        is_sketch_requested = request.form.get('activate_sketch') == 'true'

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
            
            full_input_path = os.path.join(UPLOAD_FOLDER, filename)
            gambar_file.save(full_input_path)
            data_update['image_url'] = filename  
            
            if is_sketch_requested:
                name_part, ext_part = os.path.splitext(filename)
                
                # 💡 SEED UNIK 2: Tambahkan waktu unik saat admin mengedit & mengganti file gambar baru
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                sketch_filename = f"{name_part}_sketch_{timestamp}.png"
                
                sketch_success = generate_premium_sketch(full_input_path, sketch_filename)
                if sketch_success:
                    data_update['sketch_image_url'] = sketch_filename
                    data_update['is_sketsa_available'] = True
            else:
                data_update['sketch_image_url'] = ''
                data_update['is_sketsa_available'] = False
        else:
            if is_sketch_requested:
                if not batik_terpilih.get('is_sketsa_available') and batik_terpilih.get('image_url'):
                    current_image = batik_terpilih['image_url']
                    full_input_path = os.path.join(UPLOAD_FOLDER, current_image)
                    
                    name_part, ext_part = os.path.splitext(current_image)
                    
                    # 💡 SEED UNIK 3: Tambahkan waktu unik saat admin hanya mengaktifkan checkbox sketsa (tanpa ganti gambar)
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    sketch_filename = f"{name_part}_sketch_{timestamp}.png"
                    
                    sketch_success = generate_premium_sketch(full_input_path, sketch_filename)
                    if sketch_success:
                        data_update['sketch_image_url'] = sketch_filename
                        data_update['is_sketsa_available'] = True
            else:
                data_update['sketch_image_url'] = ''
                data_update['is_sketsa_available'] = False
        
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