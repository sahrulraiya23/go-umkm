import os
import django
import difflib # Library untuk mendeteksi kemiripan teks (Typo)

# ==========================================
# 1. SETUP DJANGO ENVIRONMENT (Wajib di atas)
# ==========================================
# Pastikan nama 'skripsi_rekomendasi.settings' sesuai dengan nama folder projectmu
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skripsi_rekomendasi.settings')
django.setup()

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from web_rekomendasi.models import Produk

# ==========================================
# 2. KONFIGURASI FASTAPI
# ==========================================
app = FastAPI(title="API Chatbot UMKM Kendari")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Mengizinkan request dari frontend Django
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
    """Mencari produk. Jika tidak ketemu pas, cari yang mirip (typo)."""
    # 1. Coba cari yang PAS dulu
    hasil = Produk.objects.filter(nama_produk__icontains=keyword)
    
    # 2. Jika KOSONG, coba cari pakai Fuzzy Logic (Anti Typo)
    if not hasil.exists():
        semua_nama = list(Produk.objects.values_list('nama_produk', flat=True))
        # Cari kata yang mirip minimal 50%
        mirip = difflib.get_close_matches(keyword, semua_nama, n=1, cutoff=0.5)
        
        if mirip:
            return Produk.objects.filter(nama_produk__icontains=mirip[0]), mirip[0]
        return None, None
    
    return hasil, keyword

def format_jawaban_produk(queryset, pesan_awal):
    jawaban = f"{pesan_awal}<br>"
    for p in queryset[:3]: # Limit 3 biar chat ga kepanjangan
        # Sesuaikan format URL dengan url Django milikmu
        url = f"/detail/{p.id}/" 
        # Format Rupiah Indonesia
        harga_format = f"Rp {int(p.harga):,}".replace(",", ".")
        jawaban += f"🛍️ <a href='{url}' target='_blank' style='color:#198754; text-decoration:none;'><b>{p.nama_produk}</b></a> - <span class='text-dark fw-bold'>{harga_format}</span><br>"
    return jawaban

def get_bot_response(msg: str):
    msg = msg.lower().strip()

    # --- FITUR 1: FAQ UMKM (Cara Pesan & Jam Buka) ---
    if any(x in msg for x in ['pesan', 'beli', 'order', 'cara']):
        return "Untuk memesan, klik judul produk yang kakak suka dari obrolan ini, lalu tekan tombol <b>'Chat Penjual'</b> untuk pesan via WhatsApp ya! 🛒"
    
    if any(x in msg for x in ['buka', 'tutup', 'jam', 'operasional']):
        return "Rata-rata UMKM di Kendari buka dari jam 08:00 sampai 17:00 WITA. Kakak bisa klik detail produk untuk nanya langsung ke penjualnya! ⏰"

    # --- FITUR 2: INTENT RECOGNITION (Deteksi Kategori) ---
    if any(x in msg for x in ['lapar', 'haus', 'makan', 'minum', 'enak', 'kuliner']):
        # Perbaikan: Akses nama_kategori lewat ForeignKey
        hasil = Produk.objects.filter(kategori__nama_kategori__icontains='kuliner').order_by('?')[:3]
        if hasil.exists():
            return format_jawaban_produk(hasil, "Lagi lapar ya? Nih rekomendasi kuliner mantap:")
            
    if any(x in msg for x in ['baju', 'celana', 'kain', 'tenun', 'fashion']):
        hasil = Produk.objects.filter(kategori__nama_kategori__icontains='fashion').order_by('?')[:3]
        if hasil.exists():
            return format_jawaban_produk(hasil, "Mau tampil kece? Cek produk fashion lokal ini:")

    # --- FITUR 3: REKOMENDASI MURAH/MAHAL ---
    if any(x in msg for x in ['murah', 'hemat', 'diskon']):
        murah = Produk.objects.all().order_by('harga')[:3]
        return format_jawaban_produk(murah, "Siap! Ini produk paling ramah di kantong:")

    if any(x in msg for x in ['mahal', 'premium', 'sultan']):
        mahal = Produk.objects.all().order_by('-harga')[:3]
        return format_jawaban_produk(mahal, "Wih, lagi cari barang premium ya? Cek ini:")

    # --- FITUR 4: PENCARIAN DENGAN ANTI-TYPO ---
    if "cari" in msg or "ada" in msg:
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

    # --- FITUR 5: SAPAAN & DEFAULT ---
    if any(x in msg for x in ['halo', 'hai', 'pagi', 'sore', 'malam', 'assalamualaikum']):
        return "Halo kak! 👋 Selamat datang di Chatbot UMKM Kendari. Mau cari <b>Kuliner</b>, <b>Fashion</b>, atau nanya <b>Cara Pesan</b>?"

    # DEFAULT FALLBACK
    return """
    Maaf aku belum paham. Coba ketik:
    <br>👉 <b>"Cari Bakso"</b> (Pencarian Produk)
    <br>👉 <b>"Saya Lapar"</b> (Cari Makanan)
    <br>👉 <b>"Yang Murah"</b> (Filter Harga)
    <br>👉 <b>"Cara Pesan"</b> (Bantuan)
    """

# ==========================================
# 4. ENDPOINT (API URL)
# ==========================================
@app.post("/api/chat/")
def chat_endpoint(input_data: ChatInput):
    response_text = get_bot_response(input_data.message)
    # Ubah key balasan menjadi 'jawaban' agar sesuai dengan script JS di frontend kita
    return {"jawaban": response_text}