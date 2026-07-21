import sqlite3
import os
import shutil

# Jika berjalan di Vercel Serverless, gunakan folder /tmp agar database SQLite bisa ditulis (writable)
if os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV'):
    DATABASE_NAME = '/tmp/database.db'
else:
    DATABASE_NAME = 'database.db'

def ensure_db_file():
    """Memastikan file database di Vercel ter-copy ke /tmp dan terisi data seeder."""
    if os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV'):
        if not os.path.exists(DATABASE_NAME):
            base_db = os.path.join(os.path.dirname(__file__), 'database.db')
            if os.path.exists(base_db):
                shutil.copy(base_db, DATABASE_NAME)

def get_db_connection():
    """Membuat koneksi ke database SQLite dan mengembalikan objek koneksi dengan Row factory."""
    ensure_db_file()
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Menginisialisasi tabel database jika belum ada."""
    ensure_db_file()
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    
    # Tabel Users / Admin
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nama_lengkap TEXT NOT NULL,
            role TEXT DEFAULT 'admin'
        )
    ''')
    
    # Tabel Ruang Kelas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ruang (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kode_ruang TEXT UNIQUE NOT NULL,
            nama_ruang TEXT NOT NULL,
            gedung TEXT NOT NULL,
            kapasitas INTEGER NOT NULL,
            fasilitas TEXT,
            status TEXT DEFAULT 'Tersedia'
        )
    ''')
    
    # Tabel Jadwal Penggunaan Ruang
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jadwal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ruang_id INTEGER NOT NULL,
            mata_kuliah TEXT NOT NULL,
            dosen TEXT NOT NULL,
            hari TEXT NOT NULL,
            jam_mulai TEXT NOT NULL,
            jam_selesai TEXT NOT NULL,
            kelas TEXT NOT NULL,
            keterangan TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ruang_id) REFERENCES ruang (id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database SQLite berhasil diinisialisasi.")
