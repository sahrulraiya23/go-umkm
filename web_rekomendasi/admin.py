from django.contrib import admin
from .models import UMKM, Kategori, Produk, Penilaian, PreferensiPengguna

# 1. ADMIN KHUSUS PRODUK (LOGIKA KEAMANAN)
class ProdukAdmin(admin.ModelAdmin):
    list_display = ('nama_produk', 'umkm', 'kategori', 'harga')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Jika Super Admin, tampilkan semua
        if request.user.is_superuser:
            return qs
        
        # Jika User Biasa (Pelaku UMKM), Cek apakah dia punya toko?
        if hasattr(request.user, 'toko'):
            # Filter produk yang UMKM-nya adalah toko milik user ini
            return qs.filter(umkm=request.user.toko)
        
        # Jika user tidak punya toko, jangan tampilkan apa-apa
        return qs.none()

    def save_model(self, request, obj, form, change):
        # Saat simpan produk, otomatis set UMKM ke toko milik user login
        if not request.user.is_superuser and hasattr(request.user, 'toko'):
            obj.umkm = request.user.toko
        super().save_model(request, obj, form, change)
        
    def get_exclude(self, request, obj=None):
        # Sembunyikan pilihan 'UMKM' saat Pelaku UMKM input produk
        # Biar tidak salah pilih toko orang lain
        if not request.user.is_superuser:
            return ('umkm',) 
        return ()

# 2. ADMIN KHUSUS UMKM (Profil Toko)
class UMKMAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Pelaku UMKM hanya bisa lihat profil tokonya sendiri
        return qs.filter(pemilik=request.user)

# DAFTARKAN MODEL
admin.site.register(Produk, ProdukAdmin)
admin.site.register(UMKM, UMKMAdmin)
admin.site.register(Kategori)
admin.site.register(Penilaian)
admin.site.register(PreferensiPengguna)