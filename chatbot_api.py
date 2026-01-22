import os
import django
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import random
import difflib # Library untuk mendeteksi kemiripan teks (Typo)

# ==========================================
# 1. SETUP DJANGO ENVIRONMENT
# ==========================================
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skripsi_rekomendasi.settings')
django.setup()

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
# 3. LOGIKA CERDAS (SMART LOGIC)
# ==========================================

def cari_produk_fuzzy(keyword):
    """
    Mencari produk. Jika tidak ketemu pas, cari yang mirip (typo).
    """
    # 1. Coba cari yang PAS dulu
    hasil = Produk.objects.filter(nama_produk__icontains=keyword)
    
    # 2. Jika KOSONG, coba cari pakai Fuzzy Logic (Anti Typo)
    if not hasil.exists():
        semua_nama = list(Produk.objects.values_list('nama_produk', flat=True))
        # Cari kata yang mirip minimal 60%
        mirip = difflib.get_close_matches(keyword, semua_nama, n=1, cutoff=0.6)
        
        if mirip:
            # Jika nemu yang mirip, ambil produk itu
            return Produk.objects.filter(nama_produk__icontains=mirip[0]), mirip[0]
        return None, None
    
    return hasil, keyword

def format_jawaban_produk(queryset, pesan_awal):
    jawaban = f"{pesan_awal}<br>"
    for p in queryset[:3]: # Limit 3 biar chat ga kepanjangan
        url = f"/produk/{p.id}/"
        jawaban += f"🛍️ <a href='{url}' target='_blank'><b>{p.nama_produk}</b></a> - <span class='text-success fw-bold'>Rp {p.harga:,}</span><br>"
    return jawaban

def get_bot_response(msg: str):
    msg = msg.lower()

    # --- FITUR 1: DETEKSI KATEGORI (INTENT RECOGNITION) ---
    if any(x in msg for x in ['lapar', 'haus', 'makan', 'minum', 'enak']):
        hasil = Produk.objects.filter(kategori__iexact='kuliner').order_by('?')[:3]
        if hasil:
            return format_jawaban_produk(hasil, "Lagi lapar ya? Nih rekomendasi kuliner mantap:")
            
    if any(x in msg for x in ['baju', 'celana', 'kain', 'tenun', 'fashion']):
        hasil = Produk.objects.filter(kategori__iexact='fashion').order_by('?')[:3]
        if hasil:
            return format_jawaban_produk(hasil, "Mau tampil kece? Cek produk fashion lokal ini:")

    # --- FITUR 2: PENCARIAN DENGAN ANTI-TYPO ---
    if "cari" in msg or "ada" in msg:
        # Bersihkan kata perintah
        keyword = msg.replace("cari", "").replace("apakah", "").replace("ada", "").strip()
        
        if len(keyword) < 3:
            return "Mau cari apa kak? Ketik <b>'Cari [Nama Produk]'</b> ya."

        hasil, kata_temu = cari_produk_fuzzy(keyword)

        if hasil and hasil.exists():
            if kata_temu != keyword:
                return format_jawaban_produk(hasil, f"Mungkin maksud kakak '<b>{kata_temu}</b>'? Ini produknya:")
            else:
                return format_jawaban_produk(hasil, f"Ini hasil pencarian untuk '<b>{keyword}</b>':")
        else:
            return f"Waduh, produk '<b>{keyword}</b>' belum ketemu nih. Coba kata kunci lain?"

    # --- FITUR 3: REKOMENDASI MURAH/MAHAL ---
    if "murah" in msg or "hemat" in msg:
        # Cari 3 produk termurah
        murah = Produk.objects.all().order_by('harga')[:3]
        return format_jawaban_produk(murah, "Siap! Ini produk paling ramah di kantong:")

    if "mahal" in msg or "premium" in msg or "sultan" in msg:
        # Cari 3 produk termahal
        mahal = Produk.objects.all().order_by('-harga')[:3]
        return format_jawaban_produk(mahal, "Wih, lagi cari barang premium ya? Cek ini:")

    # --- FITUR 4: REKOMENDASI UMUM ---
    if "rekomendasi" in msg or "saran" in msg:
        items = Produk.objects.all().order_by('?')[:3]
        return format_jawaban_produk(items, "Boleh banget! Ini pilihan terbaik dari kami:")

    # --- FITUR 5: SAPAAN & DEFAULT ---
    if any(x in msg for x in ['halo', 'hai', 'pagi', 'sore', 'malam']):
        return "Halo kak! 👋 Selamat datang di UMKMGo. Mau cari <b>Kuliner</b>, <b>Fashion</b>, atau <b>Kriya</b>?"

    return """
    Maaf aku belum paham. Coba ketik:
    <br>👉 <b>"Cari Bakso"</b> (Pencarian)
    <br>👉 <b>"Saya Lapar"</b> (Kategori)
    <br>👉 <b>"Yang Murah"</b> (Filter Harga)
    """

# ==========================================
# 4. ENDPOINT (SYNC MODE)
# ==========================================
@app.post("/chat")
def chat_endpoint(input_data: ChatInput):
    response_text = get_bot_response(input_data.message)
    return {"reply": response_text}