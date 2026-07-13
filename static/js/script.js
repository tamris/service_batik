document.addEventListener('DOMContentLoaded', function() {
	
	// 1. MANAJEMEN ACTIVE MENU SIDEBAR
	const allSideMenu = document.querySelectorAll('#sidebar .side-menu.top li a');

	allSideMenu.forEach(item => {
		const li = item.parentElement;

		item.addEventListener('click', function () {
			allSideMenu.forEach(i => {
				i.parentElement.classList.remove('active');
			});
			li.classList.add('active');

			// BEST PRACTICE MOBILE: Otomatis tutup sidebar setelah klik menu di HP
			if (window.innerWidth <= 768) {
				const sidebar = document.getElementById('sidebar');
				if (sidebar) sidebar.classList.remove('show');
			}
		});
	});

	// 2. RESPONSIVE SIDEBAR TOGGLE
	const menuBar = document.querySelector('#content nav .bx.bx-menu');
	const sidebar = document.getElementById('sidebar');

	if (menuBar && sidebar) { 
		menuBar.addEventListener('click', function () {
			if (window.innerWidth <= 768) {
				// Mode Mobile: Geser keluar/masuk sidebar
				sidebar.classList.toggle('show');
				sidebar.classList.remove('hide'); 
			} else {
				// Mode Desktop: Ciutkan sidebar ke ukuran minimal
				sidebar.classList.toggle('hide');
				sidebar.classList.remove('show'); 
			}
		});
	}

	// Inisialisasi awal reset kelas sidebar berdasarkan ukuran viewport saat load
	function checkResolution() {
		if (sidebar) {
			if (window.innerWidth <= 768) {
				sidebar.classList.remove('show');
				sidebar.classList.remove('hide');
			} else {
				sidebar.classList.remove('show');
			}
		}
	}
	checkResolution();

	// Pantau jika layar diputar/di-resize secara real-time
	window.addEventListener('resize', function () {
		if (window.innerWidth > 768 && sidebar) {
			sidebar.classList.remove('show');
		}
	});

	// 3. DARK MODE ENGINE
	const switchMode = document.getElementById('switch-mode');

	if (switchMode) { 
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
});