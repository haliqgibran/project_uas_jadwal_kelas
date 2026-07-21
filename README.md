# Sistem Informasi Manajemen Jadwal Penggunaan Ruang Kelas Berbasis Web

> **Tugas UAS Berbasis Project - Mata Kuliah Pengantar Pemrograman**  
> Pembangunan Sistem Informasi Sederhana Berbasis Python Flask dengan Dashboard Admin & Classic Academic Design System.

---

## 📌 Deskripsi Proyek

Sistem Informasi Manajemen Jadwal Penggunaan Ruang Kelas adalah aplikasi berbasis web yang dirancang untuk mengelola dan memantau penggunaan ruangan perkuliahan di lingkungan akademis secara efektif, terstruktur, dan transparan. Sistem ini dilengkapi dengan **Deteksi Otomatis Bentrok Jadwal (Schedule Collision Engine)** Sisi Server untuk mencegah bentrok waktu penggunaan ruangan, serta memiliki 2 sisi pengguna (Sisi Publik & Sisi Administrator).

Antarmuka dirancang mengusung tema **Classic Academic Design System** dengan kombinasi warna *Parchment Cream*, *Deep Royal Navy*, *Burgundy*, dan aksen *Antique Gold* yang elegan.

---

## ✨ Fitur-Fitur Utama

### 1. Sisi Pengguna Umum / Publik
- 🏠 **Monitoring Ruangan Real-time**: Menampilkan status keterisian tiap ruangan hari ini (*Sedang Terpakai* vs *Tersedia*) beserta detail perkuliahan yang sedang berlangsung.
- 🔎 **Pencarian & Filtering**: Pencarian jadwal berdasarkan Kata Kunci (Mata Kuliah, Dosen, Kelas), Filter Hari, dan Filter Ruangan.
- 📅 **Tabel Jadwal Terstruktur**: Menampilkan seluruh jam dan hari perkuliahan secara kronologis.

### 2. Autentikasi & Keamanan Admin
- 🔐 **Login Admin (Session-Based)**: Proteksi halaman dashboard admin dari akses tanpa autentikasi.
- 🔑 **Password Hashing**: Menggunakan `werkzeug.security` (`generate_password_hash` & `check_password_hash`).
- 🚪 **Logout Safe Session**: Pembersihan sesi penuh saat logout.

### 3. Dashboard Admin & Visualisasi Data
- 📊 **Kartu Ringkasan Statistik**: Total Ruangan, Total Jadwal, Dosen Aktif, dan Mata Kuliah Terdaftar.
- 📈 **Grafik Interaktif (Chart.js)**: Visualisasi grafik distribusi jadwal per hari dan sebaran ruangan per gedung.
- 📋 **Tabel Aktivitas Terakhir**: Menampilkan jadwal yang baru ditambahkan.

### 4. CRUD Entitas Utama 1: Ruang Kelas
- ➕ **Tambah Ruangan**: Input kode ruang, nama ruang, gedung/lokasi, kapasitas kursi, fasilitas, dan status.
- ✏️ **Edit Ruangan**: Perbarui detail data ruangan.
- 🗑️ **Hapus Ruangan**: Hapus data ruangan dan jadwal terkait.
- ⚠️ **Validasi Keunikan Kode Ruang**: Mencegah duplikasi kode ruangan.

### 5. CRUD Entitas Utama 2: Jadwal Perkuliahan & Conflict Engine
- ➕ **Tambah & Edit Jadwal**: Pengaturan Hari, Jam Mulai, Jam Selesai, Ruangan, Mata Kuliah, Dosen, dan Kelas.
- 🚨 **Server-Side Schedule Collision Engine**: Menguji dan menolak secara otomatis jika ada jadwal lain yang jam & ruangannya beririsan pada hari yang sama.

### 6. Rekapitulasi & Laporan Siap Cetak
- 📋 **Rekapitulasi Penggunaan**: Matriks frekuensi penggunaan ruangan per hari (Senin-Sabtu).
- 🖨️ **Fitur Print Friendly**: Format tampilan yang disesuaikan saat mencetak dokumen laporan (`window.print()`).

---

## 🛠️ Teknologi & Dependensi

- **Bahasa Pemrograman**: Python 3.x
- **Web Framework**: Flask >= 3.0.0
- **Basis Data**: SQLite3 (`database.db`)
- **Keamanan**: Werkzeug Security
- **Tampilan**: HTML5, CSS3 Custom (Vanilla CSS Classic Academic Theme), JavaScript, Chart.js

---

## 🚀 Panduan Instalasi & Menjalankan Aplikasi

### 1. Clone Repository & Masuk ke Folder Proyek
```bash
git clone https://github.com/haliqgibran/project_uas_jadwal_kelas.git
cd project_uas_jadwal_kelas
```

### 2. Buat Virtual Environment (Opsional tapi Disarankan)
```bash
python -m venv venv
# Untuk Windows:
venv\Scripts\activate
# Untuk macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependensi
```bash
pip install -r requirements.txt
```

### 4. Inisialisasi Database & Seeding Data Awal
```bash
python init_db.py
```

### 5. Jalankan Server Flask
```bash
python app.py
```

Buka peramban (browser) dan akses: **`http://127.0.0.1:5000`**

---

## 🔑 Kredensial Administrator Default

Untuk masuk ke Halaman Dashboard Admin:
- **URL Login**: `http://127.0.0.1:5000/login`
- **Username**: `admin`
- **Password**: `admin123`

---

## 📁 Struktur Direktori Proyek

```
project_uas_jadwal_kelas/
├── app.py                 # Core routing, autentikasi session, validasi bentrok, CRUD routes
├── database.py            # Modul koneksi SQLite & pembuatan skema tabel
├── init_db.py             # Script inisialisasi & seeding data sampel awal
├── requirements.txt       # Daftar dependensi Python (Flask, Werkzeug)
├── database.db            # Database SQLite (dibuat otomatis oleh init_db.py)
├── static/
│   └── css/
│       └── style.css      # CSS kustom Classic Academic Aesthetics
├── templates/
│   ├── base.html          # Master layout template, header crest, navbar & flash alerts
│   ├── index.html         # Halaman Publik (Jadwal & Real-time status ruangan)
│   ├── login.html         # Halaman Form Login Administrator
│   ├── dashboard.html     # Dashboard Admin (Statistik & Visualisasi Chart.js)
│   ├── ruang.html         # Halaman Kelola Data Ruang Kelas (CRUD)
│   ├── jadwal.html        # Halaman Kelola Data Jadwal Perkuliahan (CRUD & Conflict Engine)
│   └── laporan.html       # Halaman Rekapitulasi Data & Print View
├── README.md              # Dokumentasi lengkap proyek
└── .gitignore             # Berkas pengabaian git
```
