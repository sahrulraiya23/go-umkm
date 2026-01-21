from django.contrib import admin
from .models import UMKM, Kategori, Produk, Penilaian, PreferensiPengguna

# 1. Konfigurasi Tampilan Tabel Produk agar lebih rapi
class ProdukAdmin(admin.ModelAdmin):
    list_display = ('nama_produk', 'kategori', 'umkm', 'harga') # Kolom yang muncul di list
    search_fields = ('nama_produk',) # Kotak pencarian
    list_filter = ('kategori', 'umkm') # Filter di samping kanan

# 2. Konfigurasi Tampilan Penilaian
class PenilaianAdmin(admin.ModelAdmin):
    list_display = ('user', 'produk', 'rating', 'tanggal')
    list_filter = ('rating',)

# 3. Daftarkan semua model ke Admin
admin.site.register(UMKM)
admin.site.register(Kategori)
admin.site.register(Produk, ProdukAdmin) # Gunakan konfigurasi khusus tadi
admin.site.register(Penilaian, PenilaianAdmin)
admin.site.register(PreferensiPengguna)