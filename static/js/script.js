const allSideMenu = document.querySelectorAll('#sidebar .side-menu.top li a');

allSideMenu.forEach(item => {
	const li = item.parentElement;

	item.addEventListener('click', function () {
		allSideMenu.forEach(i => {
			i.parentElement.classList.remove('active');
		})
		li.classList.add('active');
	})
});

// TOGGLE SIDEBAR
const menuBar = document.querySelector('#content nav .bx.bx-menu');
const sidebar = document.getElementById('sidebar');

if (menuBar) { // Tambahkan pengecekan agar aman
	menuBar.addEventListener('click', function () {
		sidebar.classList.toggle('hide');
	})
}

// --- BAGIAN YANG BIKIN ERROR (DIPERBAIKI) ---
const searchButton = document.querySelector('#content nav form .form-input button');
const searchButtonIcon = document.querySelector('#content nav form .form-input button .bx');
const searchForm = document.querySelector('#content nav form');

// Cek dulu: "Ada gak tombol search-nya?" Kalau ada baru jalankan fungsi
if (searchButton && searchButtonIcon && searchForm) {
	searchButton.addEventListener('click', function (e) {
		if (window.innerWidth < 576) {
			e.preventDefault();
			searchForm.classList.toggle('show');
			if (searchForm.classList.contains('show')) {
				searchButtonIcon.classList.replace('bx-search', 'bx-x');
			} else {
				searchButtonIcon.classList.replace('bx-x', 'bx-search');
			}
		}
	})

	window.addEventListener('resize', function () {
		if (this.innerWidth > 576) {
			searchButtonIcon.classList.replace('bx-x', 'bx-search');
			searchForm.classList.remove('show');
		}
	})
}
// --------------------------------------------

if (window.innerWidth < 768) {
	sidebar.classList.add('hide');
}

// DARK MODE (Pastiin ini tetap di bawah)
const switchMode = document.getElementById('switch-mode');

if (switchMode) { // Tambahkan pengecekan
	if (localStorage.getItem('theme') === 'dark') {
		document.body.classList.add('dark');
		switchMode.checked = true;
	}

	switchMode.addEventListener('change', function () {
		if (this.checked) {
			document.body.classList.add('dark');
			localStorage.setItem('theme', 'dark');
		} else {
			document.body.classList.remove('dark');
			localStorage.setItem('theme', 'light');
		}
	});
}