import math
from flask import Blueprint, render_template, request, redirect, url_for

# Bikin Blueprint khusus galeri
galeri_bp = Blueprint('galeri', __name__)

# --- DATA DUMMY DIPINDAH KE SINI (GLOBAL) ---
# Biar bisa diakses sama fungsi index() DAN create()
data_batik = [
        {
            "id": 1,
            "nama": "Sekar Jagad",
            "harga": "Rp 350.000 - Rp 500.000",
            "makna": """Motif Sekar Jagad sering dimaknai sebagai peta dunia yang tersusun dari beragam bentuk dan ornamen, merepresentasikan keindahan dalam keberagaman. Ia melambangkan perjalanan hidup, pertemuan budaya, serta harapan akan persatuan dalam perbedaan. Karena maknanya yang sarat harmoni, motif ini kerap dipilih pada momen-momen penting sebagai doa agar rumah tangga dan komunitas senantiasa rukun dan sejahtera.

Komposisinya yang padat namun seimbang menghadirkan pesan tentang keteraturan di tengah kompleksitas. Setiap elemen kecil mengingatkan bahwa identitas yang berbeda-beda dapat saling melengkapi, menumbuhkan sikap terbuka, toleran, dan penuh syukur pada perjalanan hidup.""",
            "gambar": "batik1.jpg" 
        },
        {
            "id": 2,
            "nama": "Mega Mendung",
            "harga": "Rp 350.000 - Rp 500.000",
            "makna": """Mega Mendung menampilkan lapis-lapis awan yang teduh, menjadi simbol kesabaran, ketenangan, dan kebijaksanaan. Awan yang bergulung mengajarkan agar manusia tetap sejuk pikiran dan hati dalam menghadapi gejolak, sehingga mampu mengambil keputusan yang jernih. Motif ini dikenal kuat berakar di Cirebon, dengan sentuhan akulturasi yang memperkaya estetikanya.

Gradasi warna pada motif Mega Mendung kerap dimaknai sebagai harapan akan turunnya berkah—umpama hujan yang menyuburkan. Ia menjadi pengingat bahwa pemimpin atau pribadi yang matang diharapkan dapat membawa keteduhan bagi lingkungan sekitar, menebarkan rasa aman, damai, dan harapan.""",
            "gambar": "batik2.jpg"
        },
        {
            "id": 3,
            "nama": "Kawung",
            "harga": "Rp 350.000 - Rp 500.000",
            "makna": """Kawung terinspirasi dari penampang buah kolang-kaling (aren) yang tersusun simetris. Motif ini melambangkan kesederhanaan, pengendalian diri, dan kemurnian niat. Secara historis, Kawung kerap dikaitkan dengan kebangsawanan dan martabat, sehingga mengandung pesan tentang tanggung jawab moral dalam bertindak.

Empat kelopak yang berulang dipercaya mewakili arah mata angin dan keseimbangan hidup. Ia menjadi penanda keharmonisan antara pikiran, rasa, dan perbuatan—mengajak pemakainya untuk berlaku adil, jujur, serta rendah hati dalam menjalani peran di tengah masyarakat.""",
            "gambar": "batik3.jpg"
        },
        {
            "id": 4,
            "nama": "Parang",
            "harga": "Rp 450.000 - Rp 650.000",
            "makna": """Parang melambangkan tekad dan ketangguhan. Pola miring berulang
seperti ombak yang terus menerjang, mengajarkan konsistensi, disiplin,
dan keberanian dalam menghadapi tantangan hidup. Motif ini kerap
dikaitkan dengan kepemimpinan dan daya juang yang elegan.""",
            "gambar": "batik2.jpg"
        },
        {
            "id": 5,
            "nama": "Truntum",
            "harga": "Rp 400.000 - Rp 600.000",
            "makna": """Truntum bermakna tumbuh kembali. Diciptakan sebagai simbol kasih
yang tak pernah padam, ia menandakan kehangatan keluarga dan
kesetiaan. Motif ini sering dipakai dalam upacara pernikahan sebagai doa
agar cinta terus bertumbuh dan menerangi perjalanan hidup.""",
            "gambar": "batik1.jpg"
        },
        {
            "id": 6,
            "nama": "Sido Mukti",
            "harga": "Rp 500.000 - Rp 750.000",
            "makna": """Sido Mukti bermakna hidup yang makmur dan bahagia. Motif ini
menjadi harapan agar pemakainya memperoleh kelapangan rezeki,
keselarasan batin, serta keluhuran budi dalam menapaki kehidupan.""",
            "gambar": "batik2.jpg"
        },
        {
            "id": 7,
            "nama": "Sido Asih",
            "harga": "Rp 420.000 - Rp 620.000",
            "makna": """Sido Asih menekankan kasih sayang dan kelembutan hati. Ia menjadi
penyemai hubungan yang harmonis, mendorong empati dan kepedulian
antar sesama dalam keluarga maupun masyarakat.""",
            "gambar": "batik1.jpg"
        },
        {
            "id": 8,
            "nama": "Lereng",
            "harga": "Rp 380.000 - Rp 520.000",
            "makna": """Lereng berpola garis miring yang ritmis, melambangkan langkah
maju, ketekunan, dan keteraturan. Ia mengajak pemakainya untuk
bersikap tekun dan fokus mengejar cita-cita.""",
            "gambar": "batik3.jpg"
        },
        {
            "id": 9,
            "nama": "Tambal",
            "harga": "Rp 360.000 - Rp 520.000",
            "makna": """Tambal adalah kolase motif-motif kecil yang disusun bersama.
Ia melambangkan upaya memperbaiki diri dan menyatukan kekuatan
beragam unsur menjadi harmoni yang baru.""",
            "gambar": "batik2.jpg"
        },
        {
            "id": 10,
            "nama": "Cendrawasih",
            "harga": "Rp 480.000 - Rp 700.000",
            "makna": """Terinspirasi dari burung Cendrawasih, motif ini menandakan
keanggunan, harapan, dan kemuliaan. Ia mengajak untuk merawat
keindahan alam dan menjaga martabat dalam setiap langkah.""",
            "gambar": "batik1.jpg"
        },
        {
            "id": 11,
            "nama": "Lasem",
            "harga": "Rp 420.000 - Rp 680.000",
            "makna": """Lasem dikenal dengan warna merah khas yang kuat. Motifnya
mencerminkan keberanian, kehangatan budaya pesisir, dan semangat
dagang yang terbuka terhadap pertemuan lintas budaya.""",
            "gambar": "batik3.jpg"
        },
    ]

@galeri_bp.route('/data-batik')
def index():
    # 1. Config Pagination
    per_page = 10
    page = request.args.get('page', 1, type=int)
    total_items = len(data_batik)
    total_pages = math.ceil(total_items / per_page)

    # 2. Slicing Data
    start = (page - 1) * per_page
    end = start + per_page
    data_tampil = data_batik[start:end]

    # 3. Hitung Info "Showing X to Y"
    # Kalau datanya kosong, start_index 0. Kalau ada, start dari (start + 1)
    start_index = start + 1 if total_items > 0 else 0
    
    # End index gak boleh lebih dari total items
    end_index = min(end, total_items)

    # 4. Kirim semua variabel ke HTML
    return render_template('galeri/index.html', 
                           batiks=data_tampil, 
                           page=page, 
                           total_pages=total_pages,
                           total_items=total_items,  # <-- Kirim Total
                           start_index=start_index,  # <-- Kirim Angka Awal
                           end_index=end_index)      # <-- Kirim Angka Akhir

# --- ROUTE BARU BUAT TAMBAH DATA ---
@galeri_bp.route('/data-batik/tambah', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        # 1. Ambil data dari Form HTML
        nama_input = request.form['nama_motif']
        harga_input = request.form['harga']
        makna_input = request.form['makna']
        
        # 2. Handle Gambar (Sementara kita simpan nama filenya aja)
        # Nanti pas pake Database beneran, ini ada kodingan uploadnya
        gambar_file = request.files['gambar']
        nama_gambar = gambar_file.filename if gambar_file else 'default.png'

        # 3. Bikin Dictionary Data Baru
        data_baru = {
            "id": len(data_batik) + 1, # ID otomatis nambah
            "nama": nama_input,
            "harga": harga_input,
            "makna": makna_input,
            "gambar": nama_gambar
        }

        # 4. Masukin ke List Global
        data_batik.append(data_baru)

        # 5. Balik lagi ke halaman list
        return redirect(url_for('galeri.index'))

    # Kalau metodenya GET (buka halaman), tampilkan form
    return render_template('galeri/create.html')




