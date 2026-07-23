import math
import os

from bson import ObjectId
from routes.web.auth import login_required
from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from werkzeug.utils import secure_filename
from models.event_model import EventModel
from datetime import datetime

event_bp = Blueprint('event', __name__)
event_model = EventModel()

UPLOAD_FOLDER = 'static/img/events'

@event_bp.route('/data-events')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '')
    selected_category = request.args.get('c', '') # 1. Tangkap parameter filter kategori baru
    per_page = 10

    # 2. Kirim parameter search_query dan selected_category ke model
    all_data = event_model.get_all(search_query=search_query, category=selected_category)

    total_items = len(all_data)
    total_pages = math.ceil(total_items / per_page)
    
    start = (page - 1) * per_page
    end = start + per_page
    data_tampil = all_data[start:end]
    
    start_index = start + 1 if total_items > 0 else 0
    end_index = min(end, total_items)

    # 3. Lempar data selected_category ke template HTML
    return render_template('events/index.html', 
                           events=data_tampil, 
                           page=page, 
                           total_pages=total_pages,
                           total_items=total_items,
                           start_index=start_index,
                           end_index=end_index,
                           search_query=search_query,
                           selected_category=selected_category)

@event_bp.route('/data-events/tambah', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        # Handle Upload Banner
        file = request.files.get('banner')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            banner_url = filename
        else:
            banner_url = 'default_event.png'

        data_baru = {
            "user_id": ObjectId(session.get('user_id')),
            "title": request.form.get("title"),
            "category": request.form.get("category"),
            "description": request.form.get("description"),
            "banner_image_url": banner_url,
            "event_date": request.form.get("event_date"),
            "latitude": request.form.get("latitude"),
            "longitude": request.form.get("longitude"),
            "address": {"full": request.form.get("address")},
            "is_free": request.form.get("is_free") == "on",
            "price": request.form.get("price") if request.form.get("is_free") != "on" else "0",
            "registration_url": request.form.get("registration_url"),
            "created_at": datetime.now()
        }

        event_model.create(data_baru)
        flash('Event baru berhasil ditambahkan!', 'success')
        return redirect(url_for('event.index'))

    return render_template('events/create.html')

@event_bp.route('/data-events/edit/<string:event_id>', methods=['GET', 'POST'])
@login_required
def edit(event_id):
    page = request.form.get('page', 1, type=int)
    event = event_model.get_by_id(event_id)
    
    if request.method == 'POST':
        file = request.files.get('banner')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            banner_url = filename
        else:
            banner_url = event.get('banner_image_url', 'default_event.png')

        data_update = {
            "title": request.form.get("title"),
            "category": request.form.get("category"),
            "description": request.form.get("description"),
            "banner_image_url": banner_url,
            "event_date": request.form.get("event_date"),
            "latitude": request.form.get("latitude"),
            "longitude": request.form.get("longitude"),
            "address": {"full": request.form.get("address")},
            "is_free": request.form.get("is_free") == "on",
            "price": request.form.get("price") if request.form.get("is_free") != "on" else "0",
            "registration_url": request.form.get("registration_url"),
            "updated_at": datetime.now(),
            
            # --- TAMBAHKAN INI: Catat ID admin yang sedang mengedit ---
            "updated_by": ObjectId(session.get('user_id')) 
        }

        event_model.update(event_id, data_update)
        flash('Data event berhasil diperbarui!', 'success')
        return redirect(url_for('event.index', page=page))

    return render_template('events/edit.html', event=event)

@event_bp.route('/data-events/hapus/<string:event_id>')
def delete(event_id):
    event_model.delete(event_id)
    flash('Event berhasil dihapus!', 'success')
    return redirect(url_for('event.index'))