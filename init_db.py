from database import get_db_connection, init_db
from werkzeug.security import generate_password_hash

def seed_data():
    """Mengisi database dengan data awal (admin, ruang kelas, dan jadwal sampel)."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Seed User Admin
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        hashed_password = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, password_hash, nama_lengkap, role)
            VALUES (?, ?, ?, ?)
        ''', ('admin', hashed_password, 'Administrator Akademik', 'admin'))
        print("-> User admin default berhasil dibuat: admin / admin123")
    
    # 2. Seed Data Ruang Kelas
    cursor.execute("SELECT COUNT(*) FROM ruang")
    if cursor.fetchone()[0] == 0:
        data_ruang = [
            ('RK-101', 'Ruang Kuliah 101', 'Gedung A Utama', 40, 'Proyektor, AC, Whiteboard, Sound System', 'Tersedia'),
            ('RK-102', 'Ruang Kuliah 102', 'Gedung A Utama', 40, 'Proyektor, AC, Whiteboard', 'Tersedia'),
            ('LAB-KOM1', 'Laboratorium Komputer 1', 'Gedung B Lab', 35, '35 Unit PC, AC, Proyektor, LAN/Wi-Fi High Speed', 'Tersedia'),
            ('LAB-KOM2', 'Laboratorium Komputer 2', 'Gedung B Lab', 35, '35 Unit PC, AC, Proyektor, LAN/Wi-Fi High Speed', 'Tersedia'),
            ('AUD-01', 'Auditorium Utama', 'Gedung Rektorat Lt. 3', 150, 'Sound System Premium, Stage, AC Central, Proyektor Ganda', 'Tersedia'),
            ('RK-201', 'Ruang Kuliah 201', 'Gedung C Lt. 2', 50, 'Proyektor, AC, Whiteboard, Smart TV', 'Tersedia')
        ]
        cursor.executemany('''
            INSERT INTO ruang (kode_ruang, nama_ruang, gedung, kapasitas, fasilitas, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', data_ruang)
        print("-> Data ruang kelas awal berhasil dimasukkan.")
        
    # Fetch ruang IDs for foreign keys
    cursor.execute("SELECT id, kode_ruang FROM ruang")
    ruang_map = {row['kode_ruang']: row['id'] for row in cursor.fetchall()}
    
    # 3. Seed Data Jadwal Sampel
    cursor.execute("SELECT COUNT(*) FROM jadwal")
    if cursor.fetchone()[0] == 0 and ruang_map:
        data_jadwal = [
            (ruang_map.get('RK-101'), 'Pengantar Pemrograman Python', 'Dr. Ir. Hendra Wijaya, M.T.', 'Senin', '08:00', '10:30', 'TI-1A', 'Perkuliahan Teori'),
            (ruang_map.get('RK-101'), 'Basis Data & SQL', 'Budi Santoso, M.Kom.', 'Senin', '11:00', '13:30', 'TI-1B', 'Perkuliahan Teori & Praktik'),
            (ruang_map.get('LAB-KOM1'), 'Pemrograman Web Flask', 'Siti Rahmawati, S.Kom., M.T.', 'Senin', '09:00', '12:00', 'SI-2A', 'Praktikum di Lab'),
            (ruang_map.get('RK-102'), 'Struktur Data & Algoritma', 'Dr. Ir. Hendra Wijaya, M.T.', 'Selasa', '08:00', '10:30', 'TI-1A', 'Perkuliahan Teori'),
            (ruang_map.get('LAB-KOM2'), 'Jaringan Komputer', 'Ahmad Fauzi, M.T.', 'Selasa', '13:00', '15:30', 'SK-2B', 'Praktikum Jaringan'),
            (ruang_map.get('AUD-01'), 'Kuliah Umum Kecerdasan Buatan', 'Prof. Dr. Agus Subagyo', 'Rabu', '09:00', '12:00', 'All-Prodi', 'Seminar Kebangsaan & AI'),
            (ruang_map.get('RK-201'), 'Sistem Informasi Manajemen', 'Siti Rahmawati, S.Kom., M.T.', 'Kamis', '10:00', '12:30', 'SI-3A', 'Diskusi Kelompok'),
            (ruang_map.get('RK-101'), 'Rekayasa Perangkat Lunak', 'Budi Santoso, M.Kom.', 'Jumat', '08:30', '11:00', 'TI-3A', 'Presentasi Proyek')
        ]
        cursor.executemany('''
            INSERT INTO jadwal (ruang_id, mata_kuliah, dosen, hari, jam_mulai, jam_selesai, kelas, keterangan)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', data_jadwal)
        print("-> Data jadwal perkuliahan awal berhasil dimasukkan.")
        
    conn.commit()
    conn.close()
    print("Seeding database selesai!")

if __name__ == '__main__':
    seed_data()
