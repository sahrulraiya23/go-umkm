<div align="center">

# 🛍️ Sistem Rekomendasi Produk UMKM Kota Kendari

[![Python](https://img.shields.io/badge/Python-3.8--3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.x-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)](https://www.tensorflow.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-Academic%20Use%20Only-red?style=for-the-badge)](LICENSE)

<br/>

> **Platform e-commerce cerdas berbasis web untuk UMKM Kota Kendari, dilengkapi Sistem Rekomendasi Hybrid (KNN + Neural Collaborative Filtering) dan Asisten Virtual (Chatbot) guna membantu konsumen menemukan produk yang tepat.**

<br/>

[📦 Instalasi](#-panduan-instalasi) · [✨ Fitur](#-fitur-utama) · [🏗️ Arsitektur](#%EF%B8%8F-arsitektur-sistem) · [📂 Struktur Proyek](#-struktur-direktori) · [👨‍💻 Pengembang](#-tentang-pengembang)

</div>

---

## ✨ Fitur Utama

### 🤖 Hybrid Recommendation System
| Kondisi | Algoritma | Keterangan |
|---|---|---|
| 👤 **User Baru** *(Cold Start)* | K-Nearest Neighbor (KNN) | Rekomendasi berbasis kategori pilihan saat registrasi |
| 🔄 **User Lama** *(Returning)* | Neural Collaborative Filtering (NCF) | Rekomendasi berbasis riwayat rating & ulasan pengguna |

### 💬 Asisten Virtual (Chatbot)
Fitur *floating chat* cerdas yang memungkinkan pengguna mencari dan menemukan produk secara interaktif melalui percakapan teks.

### 🛒 Checkout via WhatsApp
Integrasi langsung ke WhatsApp pemilik UMKM dengan *template* pesan otomatis yang sudah terformat rapi — tanpa perlu input manual.

### ⭐ Sistem Rating & Ulasan
Pengguna dapat memberikan ulasan dan rating bintang (1–5). Data ini secara otomatis menjadi *training data* untuk terus meningkatkan akurasi model AI.

### 🎛️ Dashboard Multi-Role
```
┌─────────────────────────────────────────────────────┐
│  ROLE           │  AKSES                            │
├─────────────────────────────────────────────────────┤
│  👤 Pembeli     │  Eksplorasi produk & preferensi   │
│  🏪 Pemilik UMKM│  Kelola produk & toko             │
│  🔧 Admin       │  Pantau seluruh data (Django Admin)│
└─────────────────────────────────────────────────────┘
```

---

## 🛠️ Teknologi yang Digunakan

| Layer | Teknologi |
|---|---|
| **Backend** | Python 3, Django Web Framework |
| **Database** | MySQL 8.0 |
| **Machine Learning** | TensorFlow, Keras, Scikit-learn |
| **Data Processing** | Pandas, NumPy |
| **Frontend** | HTML5, CSS3, Bootstrap, Vanilla JavaScript |

---

## 🏗️ Arsitektur Sistem

```
┌──────────────────────────────────────────────────────────────┐
│                        CLIENT (Browser)                      │
└───────────────────────────┬──────────────────────────────────┘
                            │ HTTP Request
┌───────────────────────────▼──────────────────────────────────┐
│                     DJANGO WEB SERVER                        │
│  ┌─────────────┐   ┌──────────────┐   ┌─────────────────┐   │
│  │    Views    │◄──│     URLs     │   │    Templates    │   │
│  │  (Logic)   │   │  (Routing)   │   │    (HTML/JS)    │   │
│  └──────┬──────┘   └──────────────┘   └─────────────────┘   │
│         │                                                    │
│  ┌──────▼──────────────────────────────────────────────┐    │
│  │              RECOMMENDATION ENGINE                  │    │
│  │  ┌──────────────────┐    ┌────────────────────────┐ │    │
│  │  │  KNN / Content-  │    │  Neural Collaborative  │ │    │
│  │  │  Based Filtering │    │  Filtering (NCF/Deep   │ │    │
│  │  │  (Cold Start)    │    │  Learning)             │ │    │
│  │  └──────────────────┘    └────────────────────────┘ │    │
│  └─────────────────────────────────────────────────────┘    │
│         │                                                    │
│  ┌──────▼──────┐                                            │
│  │    Models   │──────────────────► MySQL Database          │
│  │    (ORM)    │                                            │
│  └─────────────┘                                            │
└──────────────────────────────────────────────────────────────┘
```

---

## 🚀 Panduan Instalasi

### Prasyarat Sistem

Sebelum memulai, pastikan perangkat Anda sudah terinstal:

- ✅ **Python** versi 3.8 – 3.11
- ✅ **MySQL Server** (via XAMPP atau Laragon)
- ✅ **Git**
- ✅ **pip** (Package manager Python)

---

### Langkah 1 — Clone Repositori

```bash
git clone https://github.com/username-kamu/repo-skripsi-umkm.git
cd repo-skripsi-umkm
```

---

### Langkah 2 — Buat Virtual Environment

Sangat direkomendasikan untuk mengisolasi dependensi proyek ini.

```bash
# Buat virtual environment
python -m venv venv

# Aktifkan (Windows)
venv\Scripts\activate

# Aktifkan (Mac / Linux)
source venv/bin/activate
```

> Tanda `(venv)` di awal baris terminal menandakan virtual environment sudah aktif ✅

---

### Langkah 3 — Instalasi Dependensi

```bash
pip install -r requirements.txt
```

> **Catatan:** Pastikan library utama berikut terinstal: `django`, `mysqlclient`, `tensorflow`, `scikit-learn`, `pandas`, `numpy`.
>
> Jika belum punya `requirements.txt`, generate dengan: `pip freeze > requirements.txt`

---

### Langkah 4 — Konfigurasi Database

**a)** Jalankan MySQL melalui XAMPP / Laragon.

**b)** Buat database baru:
```sql
CREATE DATABASE skripsi_umkm_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**c)** Buka file `sistem_rekomendasi/settings.py` dan sesuaikan bagian `DATABASES`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'skripsi_umkm_db',
        'USER': 'root',           # sesuaikan
        'PASSWORD': '',           # sesuaikan
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

---

### Langkah 5 — Migrasi Database

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### Langkah 6 — Buat Akun Superuser (Admin)

```bash
python manage.py createsuperuser
```

Ikuti instruksi pengisian `username`, `email`, dan `password` di terminal.

---

### Langkah 7 — Training Model AI (NCF)

> ⚠️ Langkah ini **wajib** dilakukan agar sistem rekomendasi NCF dapat berfungsi.

**a)** Isi beberapa data dummy melalui Admin Panel di `http://127.0.0.1:8000/admin` (pengguna, produk, dan rating).

**b)** Jalankan proses training:

```bash
# Menggunakan Django management command
python manage.py train_ncf

# ATAU menggunakan script langsung
python umkm/train_ncf.py
```

**c)** Tunggu hingga terminal menampilkan:

```
✅ TRAINING SELESAI — Model disimpan ke: umkm/ncf_model.h5
```

---

### Langkah 8 — Jalankan Server

```bash
python manage.py runserver
```

🌐 Buka browser dan akses: **http://127.0.0.1:8000/**

---

## 📂 Struktur Direktori

```
skripsi_umkm/
│
├── 📁 sistem_rekomendasi/       # Konfigurasi utama Django
│   ├── settings.py              #   → Pengaturan project (DB, Installed Apps, dll)
│   ├── urls.py                  #   → Routing URL utama
│   ├── asgi.py
│   └── wsgi.py
│
├── 📁 umkm/                     # App utama aplikasi
│   ├── 📁 templates/            #   → File HTML (tampilan frontend)
│   ├── 📁 management/commands/  #   → Custom command Django (train_ncf, dll)
│   ├── models.py                #   → Definisi tabel database (ORM)
│   ├── views.py                 #   → Logika bisnis dan rekomendasi
│   ├── urls.py                  #   → Routing URL app
│   ├── train_ncf.py             #   → Script training model NCF
│   └── ncf_model.h5             #   → ⭐ File model AI hasil training
│
├── 📁 media/                    # Penyimpanan gambar produk (upload)
├── 📁 static/                   # Aset statis (CSS, JS, gambar bawaan)
├── manage.py                    # Script eksekusi utama Django
├── requirements.txt             # Daftar library Python yang digunakan
└── README.md                    # 📄 Dokumentasi proyek ini
```

---

## 🔧 Perintah Berguna

```bash
# Menjalankan server development
python manage.py runserver

# Membuat file migrasi baru setelah mengubah models.py
python manage.py makemigrations

# Menerapkan migrasi ke database
python manage.py migrate

# Membuka Django interactive shell
python manage.py shell

# Melatih ulang model NCF
python manage.py train_ncf

# Mengumpulkan file statis (untuk deployment)
python manage.py collectstatic
```

---

## ❓ Troubleshooting

<details>
<summary><b>❌ Error: mysqlclient tidak bisa diinstal</b></summary>

Coba install terlebih dahulu:
```bash
# Windows: install dari wheel
pip install mysqlclient‑{versi}‑cp311‑cp311‑win_amd64.whl

# Ubuntu/Debian
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
pip install mysqlclient
```
</details>

<details>
<summary><b>❌ Error: ncf_model.h5 not found</b></summary>

Model belum dilatih. Jalankan:
```bash
python manage.py train_ncf
```
</details>

<details>
<summary><b>❌ Error: No module named 'tensorflow'</b></summary>

Pastikan virtual environment aktif, lalu:
```bash
pip install tensorflow
```
</details>

---

## 👨‍💻 Tentang Pengembang

<div align="center">

| | |
|---|---|
| **Nama** | `Muhammad Saharullah Raiya` |
| **NIM** | `E1E122123` |
| **Program Studi** | ` informatika` |
| **Universitas** | `Universitas Halu Oleo` |
| **Tahun** | 2026 |

</div>

Proyek ini dikembangkan sebagai **Tugas Akhir / Skripsi (S1)** untuk memenuhi persyaratan kelulusan.

---

<div align="center">

⚠️ **Hak Cipta & Lisensi**

Kode sumber ini dibuat untuk keperluan **akademik**. Dilarang menyalin, menduplikasi, atau mengomersialisasikan tanpa izin tertulis dari penulis.

<br/>

*Dikembangkan dengan ❤️ di Kota Kendari, Sulawesi Tenggara*

</div>