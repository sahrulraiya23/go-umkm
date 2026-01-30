from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# Pastikan semua view di-import di sini
from web_rekomendasi.views import (
    landing_page,       # <--- View baru (Halaman Awal)
    dashboard,          # <--- View Dashboard (JANGAN LUPA INI)
    login_view,         # Sesuaikan dengan nama fungsi di views.py (misal: login_view atau login_user)
    logout_view,
    register_view,
    pilih_preferensi_view,
    detail_produk_view,
    register_umkm_view
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # 1. HALAMAN AWAL (Landing Page Gojek Style)
    path('', landing_page, name='landing_page'),

    # 2. HALAMAN DASHBOARD (Wajib ada name='dashboard')
    path('dashboard/', dashboard, name='dashboard'), 

    # 3. Authentikasi
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('register-umkm/', register_umkm_view, name='register_umkm'),

    # 4. Fitur Lain
    path('preferensi/', pilih_preferensi_view, name='pilih_preferensi'),
    path('produk/<int:produk_id>/', detail_produk_view, name='detail_produk'),
]

# Konfigurasi untuk menampilkan gambar (Media)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)