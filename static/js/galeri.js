const searchInput = document.getElementById('searchInput');
const tableBody = document.getElementById('tableBody');
const paginationContainer = document.getElementById('paginationContainer');
let timeout = null;

// EVENT LISTENER (LIVE SEARCH)
// 'input' mendeteksi setiap ketikan DAN klik tombol silang (clear)
searchInput.addEventListener('input', function () {
    const query = this.value;

    // Debounce: Tunggu user selesai ngetik 300ms baru cari (biar gak berat)
    clearTimeout(timeout);
    timeout = setTimeout(() => {
        fetchData(query);
    }, 300);
});

// FUNGSI AJAX FETCH
function fetchData(query) {
    // Panggil backend tanpa reload browser
    // query kosong = ambil semua data
    fetch(`{{ url_for('galeri.index') }}?q=${query}`)
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');

            // Update Tabel
            const newTableBody = doc.getElementById('tableBody');
            if (newTableBody && tableBody) {
                tableBody.innerHTML = newTableBody.innerHTML;
            }

            // Update Pagination
            const newPagination = doc.getElementById('paginationContainer');
            if (newPagination && paginationContainer) {
                paginationContainer.innerHTML = newPagination.innerHTML;
            }
        })
        .catch(err => console.error('Error fetching data:', err));
}