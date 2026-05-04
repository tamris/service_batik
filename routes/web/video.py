import math
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.video_model import VideoModel
from datetime import datetime

video_bp = Blueprint('video', __name__)
video_model = VideoModel()

@video_bp.route('/data-video')
def index():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '')
    per_page = 7

    all_data = video_model.get_all(search_query)

    total_items = len(all_data)
    total_pages = math.ceil(total_items / per_page)
    
    start = (page - 1) * per_page
    end = start + per_page
    data_tampil = all_data[start:end]
    
    start_index = start + 1 if total_items > 0 else 0
    end_index = min(end, total_items)

    return render_template('video/index.html', 
                           videos=data_tampil, 
                           page=page, 
                           total_pages=total_pages,
                           total_items=total_items,
                           start_index=start_index,
                           end_index=end_index,
                           search_query=search_query)

@video_bp.route('/data-video/tambah', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        data_baru = {
            "title": request.form['title'],
            "description": request.form['description'],
            "category": request.form['category'],
            "youtube_url": request.form['youtube_url'],
            "created_at": datetime.now() # Menambahkan timestamp pembuatan
        }
        video_model.create(data_baru)
        flash('Video berhasil ditambahkan!', 'success')
        return redirect(url_for('video.index'))
    return render_template('video/create.html')

@video_bp.route('/data-video/edit/<string:video_id>', methods=['GET', 'POST'])
def edit(video_id):
    page = request.form.get('page', 1, type=int)
    video_terpilih = video_model.get_by_id(video_id)
    if not video_terpilih:
        flash('Video tidak ditemukan!', 'danger')
        return redirect(url_for('video.index'))

    if request.method == 'POST':
        data_update = {
            "title": request.form['title'],
            "description": request.form['description'],
            "category": request.form['category'],
            "youtube_url": request.form['youtube_url']
        }
        video_model.update(video_id, data_update)
        flash('Video berhasil diperbarui!', 'success')
        return redirect(url_for('video.index', page=page))
    return render_template('video/edit.html', video=video_terpilih)

@video_bp.route('/data-video/hapus/<string:video_id>')
def delete(video_id):
    video_model.delete(video_id)
    flash('Video berhasil dihapus!', 'success')
    return redirect(url_for('video.index'))