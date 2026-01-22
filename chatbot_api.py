import os
import django
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import random

# ==========================================
# 1. SETUP DJANGO ENVIRONMENT (Agar bisa baca DB)
# ==========================================
# Ganti 'skripsi_rekomendasi' dengan nama folder project utama Anda (yang ada settings.py)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skripsi_rekomendasi.settings')
django.setup()

# Import Model setelah setup berhasil
from web_rekomendasi.models import Produk

# ==========================================
# 2. KONFIGURASI FASTAPI
# ==========================================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatInput(BaseModel):
    message: str

# ==========================================
# 3. LOGIKA KECERDASAN BOT
# ==========================================
def get_bot_response(msg: str):
    msg = msg.lower()

    # --- FITUR 1: PENCARIAN PRODUK ---
    if "cari" in msg or "produk" in msg or "lihat" in msg:
        # Ambil kata kunci setelah kata "cari" (misal: "cari bakso" -> "bakso")
        kata_kunci = msg.replace("cari", "").replace("produk", "").replace("lihat", "").strip()
        
        if not kata_kunci:
            return "Mau cari produk apa? Ketik: <b>'Cari [Nama Produk]'</b> ya."

        # Cari di Database Django
        hasil = Produk.objects.filter(nama_produk__icontains=kata_kunci)[:3] # Ambil max 3

        if hasil.exists():
            jawaban = f"Ditemukan {hasil.count()} produk untuk '<b>{kata_kunci}</b>':<br>"
            for p in hasil:
                # Kita buat Link HTML ke detail produk
                url_produk = f"/produk/{p.id}/"
                jawaban += f"- <a href='{url_produk}' target='_blank'><b>{p.nama_produk}</b></a> (Rp {p.harga})<br>"
            return jawaban
        else:
            return f"Maaf, produk '<b>{kata_kunci}</b>' belum tersedia di UMKMGo. 😔"

    # --- FITUR 2: REKOMENDASI ---
    elif "rekomendasi" in msg or "saran" in msg:
        # Ambil 3 produk secara acak/terbaru
        items = Produk.objects.all().order_by('?')[:3]
        if items:
            jawaban = "Coba cek produk unggulan kami ini:<br>"
            for p in items:
                jawaban += f"⭐ <a href='/produk/{p.id}/' target='_blank'>{p.nama_produk}</a><br>"
            return jawaban
        return "Belum ada data produk nih."

    # --- FITUR 3: SAPAAN ---
    elif "halo" in msg or "hai" in msg or "pagi" in msg:
        sapaan = ["Halo!", "Hai kak!", "Selamat datang!"]
        return f"{random.choice(sapaan)} 👋 Ada yang bisa saya bantu carikan? Coba ketik <b>'Cari Kripik'</b>."

    # --- FITUR 4: BANTUAN ---
    elif "bantu" in msg or "help" in msg:
        return """
        Saya bisa bantu:
        1. <b>Cari [Nama]</b>: Mencari produk.
        2. <b>Rekomendasi</b>: Saran produk acak.
        3. <b>Info</b>: Tentang aplikasi ini.
        """

    else:
        return "Maaf saya kurang paham. Coba ketik <b>'Cari [Nama Barang]'</b> atau <b>'Rekomendasi'</b>."

@app.post("/chat")
def chat_endpoint(input_data: ChatInput):        # <--- Hapus kata 'async'
    response_text = get_bot_response(input_data.message)
    return {"reply": response_text}