<h1 align="center">👁️🚶‍♂️📊 Real-Time People Counter</h1>
<p align="center">Sistem deteksi dan penghitung orang <i>real-time</i> berbasis YOLOv8 + Flask, dengan dashboard interaktif.</p>

<p align="center">
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" />
  <img src="https://img.shields.io/badge/YOLOv8-FFCC00?style=for-the-badge&logo=github&logoColor=black" />
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" />
  <img src="https://img.shields.io/badge/HTML/CSS-E34F26?style=for-the-badge&logo=html5&logoColor=white" />
</p>

<p align="center">
  <img src="SCREENSHOT.jpeg" alt="Live Demo Aplikasi" width="700"/>
</p>

---

## ✨ Fitur Utama

✅ Deteksi objek real-time menggunakan YOLOv8m  
✅ Video streaming langsung ke browser (Flask)  
✅ Penghitungan satu arah dengan logika *line crossing*  
✅ Dashboard interaktif tanpa refresh (fetch API)  
✅ Reset counter instan  
✅ Logging data ke file `.csv` untuk analisis lanjutan  

---

## 🛠️ Teknologi yang Digunakan

- **Backend:** Python, Flask, OpenCV, PyTorch, Ultralytics YOLOv8  
- **Frontend:** HTML5, CSS3, JavaScript (vanilla)  
- **Concurrency:** Python `threading.Lock` untuk menghindari race condition

---

## 🚀 Cara Instalasi

```bash
# 1. Clone repo ini
git clone [URL_REPOSITORY_LO]
cd [NAMA_FOLDER_PROJECT_LO]

# 2. Buat virtual environment
python3 -m venv venv

# 3. Aktifkan (macOS/Linux)
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

💡 *Catatan:* File model `.pt` akan otomatis diunduh saat pertama kali dijalankan.

---

## ▶️ Jalankan Aplikasi

```bash
python main_web.py
```

Lalu buka browser ke alamat: [http://127.0.0.1:5001](http://127.0.0.1:5001)

---

## 🐞 Studi Kasus & Solusi Teknis (FIXED)

Selama pengembangan, ada beberapa tantangan menarik yang berhasil diatasi:

### Kasus 1: Server Crash saat Tombol Reset Diklik (500 Error)
* **Masalah:** Aplikasi mengalami *500 Internal Server Error* setiap kali tombol "Reset Counter" diklik saat video sedang berjalan.
* **Diagnosis:** Terjadi **Race Condition**. Fungsi *video streaming* (`generate_frames`) terus-menerus membaca data counter, sementara di saat yang sama fungsi `reset_counter` mencoba menghapus total data tersebut. Perebutan akses ini menyebabkan crash.
* **Solusi:** Mengimplementasikan **`threading.Lock()`**. Sebuah "kunci" dibuat untuk data counter. Baik fungsi *streaming* maupun fungsi *reset* harus "memegang kunci" ini sebelum bisa mengakses data. Ini memastikan hanya satu proses yang bisa memodifikasi data pada satu waktu, sehingga mencegah "tabrakan".

### Kasus 2: Tampilan Dashboard Terpotong atau "Tenggelam"
* **Masalah:** Panel dashboard di sisi kanan tidak tampil sepenuhnya atau terpotong.
* **Diagnosis:** Properti CSS **`object-fit: cover`** pada tag `<img>` video memaksa gambar (yang lebih lebar karena sudah digabung dengan dashboard oleh OpenCV) untuk memenuhi wadahnya dengan cara di-zoom dan dipotong, sehingga bagian kanan (dashboard) hilang.
* **Solusi:** Mengubah arsitektur. Dashboard tidak lagi digambar oleh OpenCV. Backend hanya menyediakan API data (`/get_counts`), dan frontend (HTML/CSS/JS) membuat layout-nya sendiri dan mengambil data secara berkala. Ini memisahkan logika tampilan dan data, menghasilkan solusi yang lebih bersih dan modern.

### Kasus 3: `TypeError` di Mac M2 saat Kalkulasi
* **Masalah:** Saat versi awal (desktop) dikembangkan, terjadi `TypeError` saat melakukan operasi matematika.
* **Diagnosis:** Library **NumPy** tidak bisa secara langsung memproses data **PyTorch Tensor** yang berada di memori GPU Mac M2 (MPS device).
* **Solusi:** Memindahkan data tensor dari GPU ke CPU terlebih dahulu sebelum diubah menjadi format NumPy. Ini dilakukan dengan menambahkan method `.cpu().numpy()` pada data tensor yang relevan.

---

## 👨‍💻 Dibuat Oleh

**Rivaldi**   
📫 DM via [Threads](https://www.threads.net/@awpetrik)

---

> ⭐ Star repo ini kalau bermanfaat!  
> 👀 Feedback & issue? Jangan ragu buka *Issue tab* di atas.
