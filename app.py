from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from database import get_db_connection, init_db
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import datetime

app = Flask(__name__)
app.secret_key = 'super-secret-key-uas-pengantar-pemrograman-academic'

# Pastikan database terinisialisasi saat aplikasi dinyalakan
init_db()

# Decorator untuk memproteksi route admin
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu untuk mengakses halaman admin.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def check_schedule_conflict(ruang_id, hari, jam_mulai, jam_selesai, exclude_jadwal_id=None):
    """
    Fungsi validasi server-side untuk mengecek apakah ada bentrok jadwal 
    pada ruang dan hari yang sama pada rentang jam_mulai hingga jam_selesai.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT j.*, r.nama_ruang 
        FROM jadwal j
        JOIN ruang r ON j.ruang_id = r.id
        WHERE j.ruang_id = ? 
          AND j.hari = ? 
          AND (? < j.jam_selesai AND ? > j.jam_mulai)
    '''
    params = [ruang_id, hari, jam_mulai, jam_selesai]
    
    if exclude_jadwal_id:
        query += ' AND j.id != ?'
        params.append(exclude_jadwal_id)
        
    cursor.execute(query, params)
    conflict = cursor.fetchone()
    conn.close()
    return conflict

# Mapping Hari Bahasa Indonesia
DAYS_ID = {
    'Monday': 'Senin',
    'Tuesday': 'Selasa',
    'Wednesday': 'Rabu',
    'Thursday': 'Kamis',
    'Friday': 'Jumat',
    'Saturday': 'Sabtu',
    'Sunday': 'Minggu'
}

# --- ROUTES PUBLIK ---

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Filter parameter
    q_search = request.args.get('search', '').strip()
    f_hari = request.args.get('hari', '').strip()
    f_ruang = request.args.get('ruang_id', '').strip()
    
    # Hari ini versi Bahasa Indonesia
    now = datetime.datetime.now()
    today_name_en = now.strftime('%A')
    today_id = DAYS_ID.get(today_name_en, 'Senin')
    current_time_str = now.strftime('%H:%M')
    
    # Base query jadwal
    sql_jadwal = '''
        SELECT j.*, r.kode_ruang, r.nama_ruang, r.gedung, r.kapasitas, r.status AS status_ruang
        FROM jadwal j
        JOIN ruang r ON j.ruang_id = r.id
        WHERE 1=1
    '''
    params = []
    
    if f_hari:
        sql_jadwal += ' AND j.hari = ?'
        params.append(f_hari)
        
    if f_ruang:
        sql_jadwal += ' AND j.ruang_id = ?'
        params.append(f_ruang)
        
    if q_search:
        sql_jadwal += ' AND (j.mata_kuliah LIKE ? OR j.dosen LIKE ? OR j.kelas LIKE ? OR r.nama_ruang LIKE ?)'
        wildcard = f"%{q_search}%"
        params.extend([wildcard, wildcard, wildcard, wildcard])
        
    sql_jadwal += ' ORDER BY CASE j.hari WHEN "Senin" THEN 1 WHEN "Selasa" THEN 2 WHEN "Rabu" THEN 3 WHEN "Kamis" THEN 4 WHEN "Jumat" THEN 5 WHEN "Sabtu" THEN 6 ELSE 7 END, j.jam_mulai ASC'
    
    cursor.execute(sql_jadwal, params)
    jadwal_list = cursor.fetchall()
    
    # Ambil list ruang untuk dropdown filter
    cursor.execute('SELECT * FROM ruang ORDER BY gedung ASC, kode_ruang ASC')
    ruang_list = cursor.fetchall()
    
    # Tentukan status real-time tiap ruangan hari ini
    cursor.execute('''
        SELECT j.*, r.kode_ruang, r.nama_ruang 
        FROM jadwal j
        JOIN ruang r ON j.ruang_id = r.id
        WHERE j.hari = ?
    ''', (today_id,))
    jadwal_today = cursor.fetchall()
    
    active_rooms = {}
    for r in ruang_list:
        rid = r['id']
        schedules_r = [j for j in jadwal_today if j['ruang_id'] == rid]
        is_occupied = False
        current_class = None
        
        for sc in schedules_r:
            if sc['jam_mulai'] <= current_time_str <= sc['jam_selesai']:
                is_occupied = True
                current_class = sc
                break
                
        active_rooms[rid] = {
            'is_occupied': is_occupied,
            'current_class': current_class
        }
        
    conn.close()
    
    days = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
    return render_template(
        'index.html', 
        jadwal_list=jadwal_list, 
        ruang_list=ruang_list,
        days=days,
        today_id=today_id,
        current_time_str=current_time_str,
        active_rooms=active_rooms,
        f_hari=f_hari,
        f_ruang=f_ruang,
        q_search=q_search
    )

# --- AUTENTIKASI ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Username dan Password wajib diisi!', 'danger')
            return render_template('login.html')
            
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['nama_lengkap'] = user['nama_lengkap']
            flash(f'Selamat datang kembali, {user["nama_lengkap"]}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Username atau Password salah. Silakan coba lagi.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah berhasil keluar (logout).', 'info')
    return redirect(url_for('index'))

# --- DASHBOARD ADMIN ---

@app.route('/admin/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Statistik utama
    cursor.execute('SELECT COUNT(*) FROM ruang')
    total_ruang = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM jadwal')
    total_jadwal = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(DISTINCT dosen) FROM jadwal')
    total_dosen = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(DISTINCT mata_kuliah) FROM jadwal')
    total_matkul = cursor.fetchone()[0]
    
    # Distribusi Jadwal per Hari (Chart Data)
    days = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
    chart_hari_labels = days
    chart_hari_values = []
    for d in days:
        cursor.execute('SELECT COUNT(*) FROM jadwal WHERE hari = ?', (d,))
        chart_hari_values.append(cursor.fetchone()[0])
        
    # Distribusi Ruangan per Gedung (Chart Data)
    cursor.execute('SELECT gedung, COUNT(*) as jumlah FROM ruang GROUP BY gedung')
    gedung_rows = cursor.fetchall()
    chart_gedung_labels = [g['gedung'] for g in gedung_rows]
    chart_gedung_values = [g['jumlah'] for g in gedung_rows]
    
    # Jadwal Terbaru
    cursor.execute('''
        SELECT j.*, r.nama_ruang, r.kode_ruang 
        FROM jadwal j
        JOIN ruang r ON j.ruang_id = r.id
        ORDER BY j.created_at DESC LIMIT 5
    ''')
    recent_jadwal = cursor.fetchall()
    
    conn.close()
    
    return render_template(
        'dashboard.html',
        total_ruang=total_ruang,
        total_jadwal=total_jadwal,
        total_dosen=total_dosen,
        total_matkul=total_matkul,
        chart_hari_labels=chart_hari_labels,
        chart_hari_values=chart_hari_values,
        chart_gedung_labels=chart_gedung_labels,
        chart_gedung_values=chart_gedung_values,
        recent_jadwal=recent_jadwal
    )

# --- CRUD RUANG KELAS ---

@app.route('/admin/ruang')
@login_required
def ruang_list():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ruang ORDER BY gedung ASC, kode_ruang ASC')
    ruang_data = cursor.fetchall()
    conn.close()
    return render_template('ruang.html', ruang_data=ruang_data)

@app.route('/admin/ruang/tambah', methods=['POST'])
@login_required
def ruang_tambah():
    kode_ruang = request.form.get('kode_ruang', '').strip().upper()
    nama_ruang = request.form.get('nama_ruang', '').strip()
    gedung = request.form.get('gedung', '').strip()
    kapasitas = request.form.get('kapasitas', 0, type=int)
    fasilitas = request.form.get('fasilitas', '').strip()
    status = request.form.get('status', 'Tersedia').strip()
    
    if not kode_ruang or not nama_ruang or not gedung or kapasitas <= 0:
        flash('Data ruang tidak lengkap atau kapasitas tidak valid!', 'danger')
        return redirect(url_for('ruang_list'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Cek keunikan kode_ruang
    cursor.execute('SELECT id FROM ruang WHERE kode_ruang = ?', (kode_ruang,))
    if cursor.fetchone():
        conn.close()
        flash(f'Kode ruang "{kode_ruang}" sudah digunakan! Silakan gunakan kode lain.', 'danger')
        return redirect(url_for('ruang_list'))
        
    cursor.execute('''
        INSERT INTO ruang (kode_ruang, nama_ruang, gedung, kapasitas, fasilitas, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (kode_ruang, nama_ruang, gedung, kapasitas, fasilitas, status))
    
    conn.commit()
    conn.close()
    flash(f'Ruang kelas {nama_ruang} ({kode_ruang}) berhasil ditambahkan.', 'success')
    return redirect(url_for('ruang_list'))

@app.route('/admin/ruang/edit/<int:id>', methods=['POST'])
@login_required
def ruang_edit(id):
    kode_ruang = request.form.get('kode_ruang', '').strip().upper()
    nama_ruang = request.form.get('nama_ruang', '').strip()
    gedung = request.form.get('gedung', '').strip()
    kapasitas = request.form.get('kapasitas', 0, type=int)
    fasilitas = request.form.get('fasilitas', '').strip()
    status = request.form.get('status', 'Tersedia').strip()
    
    if not kode_ruang or not nama_ruang or not gedung or kapasitas <= 0:
        flash('Validasi gagal. Mohon periksa kembali input data ruangan.', 'danger')
        return redirect(url_for('ruang_list'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Cek duplikasi kode_ruang selain id ini
    cursor.execute('SELECT id FROM ruang WHERE kode_ruang = ? AND id != ?', (kode_ruang, id))
    if cursor.fetchone():
        conn.close()
        flash(f'Kode ruang "{kode_ruang}" telah dipakai oleh ruangan lain.', 'danger')
        return redirect(url_for('ruang_list'))
        
    cursor.execute('''
        UPDATE ruang 
        SET kode_ruang = ?, nama_ruang = ?, gedung = ?, kapasitas = ?, fasilitas = ?, status = ?
        WHERE id = ?
    ''', (kode_ruang, nama_ruang, gedung, kapasitas, fasilitas, status, id))
    
    conn.commit()
    conn.close()
    flash(f'Data ruang kelas {kode_ruang} berhasil diperbarui.', 'success')
    return redirect(url_for('ruang_list'))

@app.route('/admin/ruang/hapus/<int:id>', methods=['POST'])
@login_required
def ruang_hapus(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT nama_ruang FROM ruang WHERE id = ?', (id,))
    r = cursor.fetchone()
    if r:
        nama = r['nama_ruang']
        cursor.execute('DELETE FROM ruang WHERE id = ?', (id,))
        conn.commit()
        flash(f'Ruang kelas "{nama}" dan seluruh jadwal terkait berhasil dihapus.', 'success')
    else:
        flash('Data ruang tidak ditemukan.', 'warning')
        
    conn.close()
    return redirect(url_for('ruang_list'))

# --- CRUD JADWAL PERKULIAHAN ---

@app.route('/admin/jadwal')
@login_required
def jadwal_list():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT j.*, r.kode_ruang, r.nama_ruang, r.gedung 
        FROM jadwal j
        JOIN ruang r ON j.ruang_id = r.id
        ORDER BY CASE j.hari WHEN "Senin" THEN 1 WHEN "Selasa" THEN 2 WHEN "Rabu" THEN 3 WHEN "Kamis" THEN 4 WHEN "Jumat" THEN 5 WHEN "Sabtu" THEN 6 ELSE 7 END, j.jam_mulai ASC
    ''')
    jadwal_data = cursor.fetchall()
    
    cursor.execute('SELECT * FROM ruang WHERE status = "Tersedia" ORDER BY kode_ruang ASC')
    ruang_options = cursor.fetchall()
    
    conn.close()
    days = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
    return render_template('jadwal.html', jadwal_data=jadwal_data, ruang_options=ruang_options, days=days)

@app.route('/admin/jadwal/tambah', methods=['POST'])
@login_required
def jadwal_tambah():
    ruang_id = request.form.get('ruang_id', type=int)
    mata_kuliah = request.form.get('mata_kuliah', '').strip()
    dosen = request.form.get('dosen', '').strip()
    hari = request.form.get('hari', '').strip()
    jam_mulai = request.form.get('jam_mulai', '').strip()
    jam_selesai = request.form.get('jam_selesai', '').strip()
    kelas = request.form.get('kelas', '').strip()
    keterangan = request.form.get('keterangan', '').strip()
    
    # Validasi Dasar
    if not ruang_id or not mata_kuliah or not dosen or not hari or not jam_mulai or not jam_selesai or not kelas:
        flash('Semua kolom bertanda bintang (*) wajib diisi!', 'danger')
        return redirect(url_for('jadwal_list'))
        
    if jam_mulai >= jam_selesai:
        flash('Jam mulai harus lebih awal daripada jam selesai!', 'danger')
        return redirect(url_for('jadwal_list'))
        
    # Validasi Bentrok Jadwal (Conflict Engine)
    conflict = check_schedule_conflict(ruang_id, hari, jam_mulai, jam_selesai)
    if conflict:
        flash(f'BENTROK JADWAL! Ruangan "{conflict["nama_ruang"]}" sudah terpakai pada hari {hari} ({conflict["jam_mulai"]} - {conflict["jam_selesai"]}) untuk mata kuliah {conflict["mata_kuliah"]}.', 'danger')
        return redirect(url_for('jadwal_list'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO jadwal (ruang_id, mata_kuliah, dosen, hari, jam_mulai, jam_selesai, kelas, keterangan)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (ruang_id, mata_kuliah, dosen, hari, jam_mulai, jam_selesai, kelas, keterangan))
    
    conn.commit()
    conn.close()
    flash(f'Jadwal {mata_kuliah} ({kelas}) berhasil ditambahkan!', 'success')
    return redirect(url_for('jadwal_list'))

@app.route('/admin/jadwal/edit/<int:id>', methods=['POST'])
@login_required
def jadwal_edit(id):
    ruang_id = request.form.get('ruang_id', type=int)
    mata_kuliah = request.form.get('mata_kuliah', '').strip()
    dosen = request.form.get('dosen', '').strip()
    hari = request.form.get('hari', '').strip()
    jam_mulai = request.form.get('jam_mulai', '').strip()
    jam_selesai = request.form.get('jam_selesai', '').strip()
    kelas = request.form.get('kelas', '').strip()
    keterangan = request.form.get('keterangan', '').strip()
    
    if not ruang_id or not mata_kuliah or not dosen or not hari or not jam_mulai or not jam_selesai or not kelas:
        flash('Semua kolom bertanda bintang (*) wajib diisi!', 'danger')
        return redirect(url_for('jadwal_list'))
        
    if jam_mulai >= jam_selesai:
        flash('Jam mulai harus lebih awal daripada jam selesai!', 'danger')
        return redirect(url_for('jadwal_list'))
        
    # Cek bentrok mengabaikan jadwal ini sendiri
    conflict = check_schedule_conflict(ruang_id, hari, jam_mulai, jam_selesai, exclude_jadwal_id=id)
    if conflict:
        flash(f'BENTROK JADWAL! Ruangan "{conflict["nama_ruang"]}" sudah terpakai pada hari {hari} ({conflict["jam_mulai"]} - {conflict["jam_selesai"]}) untuk matkul {conflict["mata_kuliah"]}.', 'danger')
        return redirect(url_for('jadwal_list'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE jadwal
        SET ruang_id = ?, mata_kuliah = ?, dosen = ?, hari = ?, jam_mulai = ?, jam_selesai = ?, kelas = ?, keterangan = ?
        WHERE id = ?
    ''', (ruang_id, mata_kuliah, dosen, hari, jam_mulai, jam_selesai, kelas, keterangan, id))
    
    conn.commit()
    conn.close()
    flash(f'Jadwal {mata_kuliah} berhasil diperbarui.', 'success')
    return redirect(url_for('jadwal_list'))

@app.route('/admin/jadwal/hapus/<int:id>', methods=['POST'])
@login_required
def jadwal_hapus(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM jadwal WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Jadwal berhasil dihapus.', 'success')
    return redirect(url_for('jadwal_list'))

# --- LAPORAN & REKAPITULASI ---

@app.route('/admin/laporan')
@login_required
def laporan():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    f_gedung = request.args.get('gedung', '').strip()
    
    # Query rekap penggunaan per ruang
    sql_rekap = '''
        SELECT r.kode_ruang, r.nama_ruang, r.gedung, r.kapasitas, r.status,
               COUNT(j.id) AS total_jadwal,
               SUM(CASE WHEN j.hari = 'Senin' THEN 1 ELSE 0 END) AS count_senin,
               SUM(CASE WHEN j.hari = 'Selasa' THEN 1 ELSE 0 END) AS count_selasa,
               SUM(CASE WHEN j.hari = 'Rabu' THEN 1 ELSE 0 END) AS count_rabu,
               SUM(CASE WHEN j.hari = 'Kamis' THEN 1 ELSE 0 END) AS count_kamis,
               SUM(CASE WHEN j.hari = 'Jumat' THEN 1 ELSE 0 END) AS count_jumat,
               SUM(CASE WHEN j.hari = 'Sabtu' THEN 1 ELSE 0 END) AS count_sabtu
        FROM ruang r
        LEFT JOIN jadwal j ON r.id = j.ruang_id
    '''
    params = []
    if f_gedung:
        sql_rekap += ' WHERE r.gedung = ?'
        params.append(f_gedung)
        
    sql_rekap += ' GROUP BY r.id ORDER BY r.gedung ASC, r.kode_ruang ASC'
    
    cursor.execute(sql_rekap, params)
    rekap_ruang = cursor.fetchall()
    
    # List gedung untuk filter
    cursor.execute('SELECT DISTINCT gedung FROM ruang ORDER BY gedung ASC')
    gedung_list = [row['gedung'] for row in cursor.fetchall()]
    
    conn.close()
    return render_template('laporan.html', rekap_ruang=rekap_ruang, gedung_list=gedung_list, f_gedung=f_gedung)

if __name__ == '__main__':
    print("Menjalankan Sistem Informasi Manajemen Jadwal Ruang Kelas...")
    app.run(debug=True, port=5000)
