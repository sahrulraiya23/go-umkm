from django.db import models
from django.contrib.auth.models import User

# ==========================================
# 1. MODEL UMKM (Diupdate)
# ==========================================
class UMKM(models.Model):
    # JEMBATAN: Menghubungkan Akun Login dengan Data Toko
    # on_delete=CASCADE artinya kalau User dihapus, Toko juga terhapus
    pemilik = models.OneToOneField(User, on_delete=models.CASCADE, related_name='toko', null=True, blank=True) 
    
    nama_umkm = models.CharField(max_length=100)
    alamat = models.TextField()
    
    # KITA PAKAI FIELD INI UNTUK CHATBOT WA
    # Ganti no_telepon jadi no_whatsapp biar jelas, atau pakai yang ada
    no_whatsapp = models.CharField(max_length=20, help_text="Format: 628xxx (Tanpa +)", default='628xxxxx')
    
    deskripsi = models.TextField()

    def __str__(self):
        return self.nama_umkm

# ==========================================
# 2. MODEL KATEGORI
# ==========================================
class Kategori(models.Model):
    nama_kategori = models.CharField(max_length=50)

    def __str__(self):
        return self.nama_kategori

# ==========================================
# 3. MODEL PRODUK
# ==========================================
class Produk(models.Model):
    # Produk milik UMKM mana?
    umkm = models.ForeignKey(UMKM, on_delete=models.CASCADE) 
    
    kategori = models.ForeignKey(Kategori, on_delete=models.CASCADE)
    nama_produk = models.CharField(max_length=200)
    harga = models.DecimalField(max_digits=10, decimal_places=0) # Ubah decimal_places=0 biar harga bulat (Rp 15000)
    deskripsi = models.TextField()
    gambar_produk = models.ImageField(upload_to='produk/')

    def __str__(self):
        return self.nama_produk

# ==========================================
# 4. RATING & PREFERENSI (TETAP SAMA)
# ==========================================
class Penilaian(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    produk = models.ForeignKey(Produk, on_delete=models.CASCADE)
    rating = models.IntegerField()
    ulasan = models.TextField(blank=True, null=True)
    tanggal = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'produk')

class PreferensiPengguna(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    kategori_disukai = models.ManyToManyField(Kategori)