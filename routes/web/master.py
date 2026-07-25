from datetime import datetime
from bson.objectid import ObjectId
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.web.auth import login_required

from models.master_model import MasterDataModel

master_bp = Blueprint('master', __name__)
master_model = MasterDataModel()

# =========================================================================
# 🎨 MASTER DATA BATIK (Kategori & Teknik Pembuatan)
# =========================================================================

@master_bp.route('/master/batik', methods=['GET'])
@login_required
def batik():
    kategori_list = master_model.get_by_type('kategori_batik')
    teknik_list = master_model.get_by_type('teknik_batik')
    
    return render_template(
        'master/master_batik.html', 
        kategori_list=kategori_list, 
        teknik_list=teknik_list
    )

# --- ACTION KATEGORI BATIK ---
@master_bp.route('/master/batik/kategori/tambah', methods=['POST'])
@login_required
def tambah_kategori():
    nama_kategori = request.form.get('nama_kategori')
    deskripsi = request.form.get('deskripsi')

    if nama_kategori:
        master_model.create_master(
            master_type='kategori_batik', 
            name=nama_kategori, 
            description=deskripsi
        )
        flash('Kategori batik berhasil ditambahkan!', 'success')
    else:
        flash('Nama kategori wajib diisi!', 'danger')

    return redirect(url_for('master.batik'))

# --- ACTION TEKNIK PEMBUATAN BATIK ---
@master_bp.route('/master/batik/teknik/tambah', methods=['POST'])
@login_required
def tambah_teknik():
    nama_teknik = request.form.get('nama_teknik')
    deskripsi = request.form.get('deskripsi_teknik')

    if nama_teknik:
        master_model.create_master(
            master_type='teknik_batik', 
            name=nama_teknik, 
            description=deskripsi
        )
        flash('Teknik pembuatan berhasil ditambahkan!', 'success')
    else:
        flash('Nama teknik wajib diisi!', 'danger')

    return redirect(url_for('master.batik'))

# --- ACTION HAPUS PERMANEN GENERIK ---
@master_bp.route('/master/hapus/<string:master_id>')
@login_required
def hapus_master(master_id):
    master_model.delete_master(master_id)
    flash('Data master berhasil dihapus secara permanen!', 'success')
    return redirect(url_for('master.batik'))