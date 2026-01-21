from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

# Pastikan meng-import detail_produk_view di sini
from web_rekomendasi.views import (
    dashboard, 
    logout_view, 
    register_view, 
    pilih_preferensi_view, 
    detail_produk_view 
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Dashboard (Halaman Utama)
    path('', dashboard, name='dashboard'),
    
    # Autentikasi
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    
    # Fitur Preferensi (KNN Cold Start)
    path('preferensi/', pilih_preferensi_view, name='pilih_preferensi'),
    
    # === [PENYEBAB ERROR ANDA] ===
    # Baris ini sebelumnya hilang, makanya error "NoReverseMatch"
    path('produk/<int:produk_id>/', detail_produk_view, name='detail_produk'),
]

# Konfigurasi untuk menampilkan gambar produk
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)