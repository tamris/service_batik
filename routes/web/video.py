import re
import math
import requests
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.video_model import VideoModel
from datetime import datetime

video_bp = Blueprint('video', __name__)
video_model = VideoModel()

YT_API_KEY = "AIzaSyBTqRhdOeCZTnMDAip3UciyUjcmm3JCPUs"

def extract_video_id(url):
    patterns = [
        r'(?:v=)([a-zA-Z0-9_-]{11})',
        r'(?:youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'(?:shorts/)([a-zA-Z0-9_-]{11})'
    ]
    for p in patterns:
        match = re.search(p, url)
        if match:
            return match.group(1)
    return None

# ─── ROUTES (tidak ada yang berubah kecuali create) ───────────────────────────

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
        youtube_url = request.form['youtube_url']
        video_id    = extract_video_id(youtube_url)

        if not video_id:
            flash('URL YouTube tidak valid!', 'danger')
            return redirect(url_for('video.create'))

        meta = fetch_yt_metadata(video_id)
        if not meta:
            flash('Gagal mengambil data dari YouTube, cek API key atau URL!', 'danger')
            return redirect(url_for('video.create'))

        data_baru = {
            "youtube_url":      youtube_url,
            "video_id":         video_id,
            "category":         request.form['category'],
            "created_at":       datetime.now(),
            # semua dari YT API
            "title":            meta['title'],
            "description":      meta['description'],
            "thumbnail_url":    meta['thumbnail_url'],
            "view_count":       meta['view_count'],
            "duration_minutes": meta['duration_minutes'],
            "duration_seconds": meta['duration_seconds'],
            "channel_name":     meta['channel_name'],
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
        youtube_url  = request.form['youtube_url']
        new_video_id = extract_video_id(youtube_url)

        if not new_video_id:
            flash('URL YouTube tidak valid!', 'danger')
            return redirect(url_for('video.edit', video_id=video_id))

        meta = fetch_yt_metadata(new_video_id)
        if not meta:
            flash('Gagal mengambil data dari YouTube!', 'danger')
            return redirect(url_for('video.edit', video_id=video_id))

        data_update = {
            "youtube_url":      youtube_url,
            "video_id":         new_video_id,
            "category":         request.form['category'],
            # refresh semua dari YT
            "title":            meta['title'],
            "description":      meta['description'],
            "thumbnail_url":    meta['thumbnail_url'],
            "view_count":       meta['view_count'],
            "duration_minutes": meta['duration_minutes'],
            "duration_seconds": meta['duration_seconds'],
            "channel_name":     meta['channel_name'],
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


def fetch_yt_metadata(video_id):
    url = (
        f"https://www.googleapis.com/youtube/v3/videos"
        f"?id={video_id}&part=snippet,statistics,contentDetails"
        f"&key={YT_API_KEY}"
    )
    try:
        res = requests.get(url, timeout=5)
        data = res.json()
        if not data.get('items'):
            return None
        item = data['items'][0]
        snippet = item['snippet']
        stats   = item.get('statistics', {})
        dur_match = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?',
                              item['contentDetails']['duration'])
        hours   = int(dur_match.group(1) or 0)
        minutes = int(dur_match.group(2) or 0)
        seconds = int(dur_match.group(3) or 0)
        total_minutes = hours * 60 + minutes + (1 if seconds > 0 else 0)
        total_seconds = hours * 3600 + minutes * 60 + seconds
        return {
            "title":            snippet['title'],           # ← tambah
            "description":      snippet.get('description', ''),  # ← tambah
            "thumbnail_url":    snippet['thumbnails']['high']['url'],
            "view_count":       int(stats.get('viewCount', 0)),
            "duration_minutes": total_minutes,
            "duration_seconds": total_seconds,
            "channel_name":     snippet['channelTitle'],
        }
    except Exception:
        return None