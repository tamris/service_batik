import math
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.batik_model import BatikModel

galeri_bp = Blueprint('galeri', __name__)
batik_model = BatikModel()

@galeri_bp.route('/data-batik')
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

    return render_template('galeri/index.html', 
                           batiks=data_tampil, 
                           page=page, 
                           total_pages=total_pages,
                           total_items=total_items,
                           start_index=start_index,
                           end_index=end_index,
                           search_query=search_query)

@galeri_bp.route('/data-batik/tambah', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        gambar_file = request.files.get('gambar')
        nama_gambar = gambar_file.filename if gambar_file and gambar_file.filename != '' else 'default.png'

        data_baru = {
            "nama": request.form['nama_motif'],
            "harga": request.form['harga'],
            "makna": request.form['makna'],
            "gambar": nama_gambar
        }

        batik_model.create(data_baru)
        flash('Data batik berhasil ditambahkan ke database!', 'success')
        return redirect(url_for('galeri.index'))

    return render_template('galeri/create.html')

@galeri_bp.route('/data-batik/edit/<string:batik_id>', methods=['GET', 'POST'])
def edit(batik_id):
    # Ambil data dari DB berdasarkan ObjectId
    batik_terpilih = batik_model.get_by_id(batik_id)

    if not batik_terpilih:
        flash('Data tidak ditemukan!', 'danger')
        return redirect(url_for('galeri.index'))

    if request.method == 'POST':
        data_update = {
            "nama": request.form['nama_motif'],
            "harga": request.form['harga'],
            "makna": request.form['makna']
        }
        
        gambar_file = request.files.get('gambar')
        if gambar_file and gambar_file.filename != '':
            data_update['gambar'] = gambar_file.filename
        
        batik_model.update(batik_id, data_update)
        flash('Data batik berhasil diperbarui!', 'success')
        return redirect(url_for('galeri.index'))

    return render_template('galeri/edit.html', batik=batik_terpilih)

@galeri_bp.route('/data-batik/hapus/<string:batik_id>')
def delete(batik_id):
    batik_model.delete(batik_id)
    flash('Data batik berhasil dihapus!', 'success')
    return redirect(url_for('galeri.index'))