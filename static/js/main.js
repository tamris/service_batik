document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('searchInput');
    const tableBody = document.getElementById('tableBody');
    const paginationContainer = document.getElementById('paginationContainer');
    let timeout = null;

    // EVENT LISTENER (LIVE SEARCH)
    if (searchInput) {
        searchInput.addEventListener('input', function () {
            const query = this.value;
            // Ambil URL endpoint yang dititipkan di atribut data-url HTML
            const endpointUrl = this.getAttribute('data-url');

            clearTimeout(timeout);
            timeout = setTimeout(() => {
                fetchData(query, endpointUrl);
            }, 300);
        });
    }

    // FUNGSI AJAX FETCH
    function fetchData(query, baseUrl) {
        fetch(`${baseUrl}?q=${query}`)
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');

                const newTableBody = doc.getElementById('tableBody');
                if (newTableBody && tableBody) {
                    tableBody.innerHTML = newTableBody.innerHTML;
                }

                const newPagination = doc.getElementById('paginationContainer');
                if (newPagination && paginationContainer) {
                    paginationContainer.innerHTML = newPagination.innerHTML;
                }
            })
            .catch(err => console.error('Error fetching data:', err));
    }
});

// FUNGSI DELETE (Ditaruh di luar DOMContentLoaded agar bisa dipanggil lewat onclick di HTML)
function confirmDelete(batikId, batikName) {
    const isDark = document.body.classList.contains('dark');

    Swal.fire({
        title: 'Apakah Anda yakin?',
        text: `Motif "${batikName}" akan dinonaktifkan dari katalog publik.`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Ya, Nonaktifkan!',
        cancelButtonText: 'Batal',
        background: isDark ? '#0C0C1E' : '#fff',
        color: isDark ? '#fff' : '#000'
    }).then((result) => {
        if (result.isConfirmed) {
            // Alihkan langsung ke route soft delete Flask
            window.location.href = `/data-batik/hapus/${batikId}`;
        }
    });
}

function confirmRestore(batikId, batikName) {
    const isDark = document.body.classList.contains('dark');
    Swal.fire({
        title: 'Aktifkan Kembali?',
        text: `Motif "${batikName}" akan diaktifkan penuh seperti semula.`,
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#28a745',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Ya, Aktifkan!',
        cancelButtonText: 'Batal',
        background: isDark ? '#0C0C1E' : '#fff',
        color: isDark ? '#fff' : '#000'
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = `/data-batik/restore/${batikId}`;
        }
    });
}

function artikelDelete(id) {
    Swal.fire({
        title: 'Hapus Data?',
        text: "Data artikel akan dihapus permanen!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Ya, Hapus!',
        cancelButtonText: 'Batal',
        background: document.body.classList.contains('dark') ? '#0C0C1E' : '#fff',
        color: document.body.classList.contains('dark') ? '#fff' : '#000'
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = "/data-informasi/hapus/" + id;
        }
    })
}

function eventDelete(id) {
    Swal.fire({
        title: 'Hapus Data?',
        text: "Data event akan dihapus permanen!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Ya, Hapus!',
        cancelButtonText: 'Batal',
        background: document.body.classList.contains('dark') ? '#0C0C1E' : '#fff',
        color: document.body.classList.contains('dark') ? '#fff' : '#000'
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = "/data-events/hapus/" + id;
        }
    })
}

function videoDelete(id) {
    Swal.fire({
        title: 'Hapus Data?',
        text: "Data video akan dihapus permanen!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Ya, Hapus!',
        cancelButtonText: 'Batal',
        background: document.body.classList.contains('dark') ? '#0C0C1E' : '#fff',
        color: document.body.classList.contains('dark') ? '#fff' : '#000'
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = "/data-video/hapus/" + id;
        }
    })
}

