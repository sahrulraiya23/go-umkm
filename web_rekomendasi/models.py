from django.db import models
from django.contrib.auth.models import User

# Model UMKM 
class UMKM(models.Model):
    nama_umkm = models.CharField(max_length=100)
    alamat = models.TextField()
    no_telepon = models.CharField(max_length=15)
    deskripsi = models.TextField()
    # Field lain sesuai kebutuhan

    def __str__(self):
        return self.nama_umkm

# Model Kategori (Penting untuk KNN/Cold Start) 
class Kategori(models.Model):
    nama_kategori = models.CharField(max_length=50)

    def __str__(self):
        return self.nama_kategori

# Model Produk 
class Produk(models.Model):
    umkm = models.ForeignKey(UMKM, on_delete=models.CASCADE)
    kategori = models.ForeignKey(Kategori, on_delete=models.CASCADE)
    nama_produk = models.CharField(max_length=200)
    harga = models.DecimalField(max_digits=10, decimal_places=2)
    deskripsi = models.TextField()
    gambar_produk = models.ImageField(upload_to='produk/')

    def __str__(self):
        return self.nama_produk

# Model Rating/Penilaian (Penting untuk NCF) 
class Penilaian(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    produk = models.ForeignKey(Produk, on_delete=models.CASCADE)
    rating = models.IntegerField() # Skala 1-5
    ulasan = models.TextField(blank=True, null=True)
    tanggal = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'produk') # Satu user hanya rating 1x per produk

# Model Preferensi Pengguna (Untuk Cold Start KNN) [cite: 1591]
class PreferensiPengguna(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    kategori_disukai = models.ManyToManyField(Kategori)