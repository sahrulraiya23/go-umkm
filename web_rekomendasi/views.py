from django.shortcuts import render, redirect, get_object_or_404
# Import login di-alias kan jadi auth_login agar tidak bentrok nama variabel
from django.contrib.auth import login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm # <--- Penting untuk login
from django.contrib import messages
from django.db.models import Q 
from .models import Produk, Penilaian, PreferensiPengguna
from .forms import UserRegisterForm, PreferensiForm
from .recommender import get_rekomendasi
from django.core.paginator import Paginator # <--- 1. Import Paginator
# ==========================================
# 0. LANDING PAGE (GOJEK STYLE)
# ==========================================
def landing_page(request):
    # Jika user sudah login, jangan tampilkan Welcome Screen, langsung ke Dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Jika belum login, tampilkan halaman Welcome ala Gojek
    return render(request, 'welcome.html')

# ==========================================
# 1. DASHBOARD (HALAMAN UTAMA)
# ==========================================
@login_required(login_url='/login/')
def dashboard(request):
    user = request.user
    
    # ==========================================
    # 1. LOGIKA REKOMENDASI (Tidak Berubah)
    # ==========================================
    try:
        rekomendasi_list = get_rekomendasi(user.id, n=4)
    except Exception as e:
        print(f"Error di Algoritma: {e}")
        rekomendasi_list = []

    if rekomendasi_list is None:
        rekomendasi_list = []
    
    is_new_user = not Penilaian.objects.filter(user=user).exists()
    
    # ==========================================
    # 2. LOGIKA PENCARIAN & QUERYSET
    # ==========================================
    search_query = request.GET.get('q') 

    if search_query:
        # Jika user mencari, filter berdasarkan nama/deskripsi/umkm
        product_list = Produk.objects.filter(
            Q(nama_produk__icontains=search_query) | 
            Q(deskripsi__icontains=search_query) |
            Q(umkm__nama_umkm__icontains=search_query)
        ).order_by('-id')
    else:
        # Jika tidak, ambil semua produk (urut terbaru)
        product_list = Produk.objects.all().order_by('-id')

    # ==========================================
    # 3. LOGIKA PAGINATION (Penting!)
    # ==========================================
    # Bagi produk menjadi 12 per halaman
    paginator = Paginator(product_list, 12) 
    
    # Ambil nomor halaman dari URL (misal: ?page=2)
    page_number = request.GET.get('page')
    
    # Ambil data produk khusus untuk halaman tersebut
    page_obj = paginator.get_page(page_number)

    # ==========================================
    # 4. KIRIM KE TEMPLATE
    # ==========================================
    context = {
        'rekomendasi_list': rekomendasi_list,
        'all_produk': page_obj,       # <--- Kirim 'page_obj', BUKAN 'product_list'
        'is_new_user': is_new_user,
        'search_query': search_query, # Supaya teks pencarian tidak hilang saat pindah halaman
    }
    
    return render(request, 'dashboard.html', context)
# ==========================================
# 2. LOGIN USER (YANG TADI HILANG)
# ==========================================
def login_view(request):
    # Jika sudah login, lempar ke dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user) # Proses login sesungguhnya
            
            # Cek apakah ada 'next' url (redirect tujuan awal)
            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

# ==========================================
# 3. REGISTER USER BARU
# ==========================================
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user) # Langsung login setelah daftar
            return redirect('pilih_preferensi')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

# ==========================================
# 4. PILIH PREFERENSI (KNN COLD START)
# ==========================================
@login_required
def pilih_preferensi_view(request):
    pref_user = PreferensiPengguna.objects.filter(user=request.user).first()

    if request.method == 'POST':
        form = PreferensiForm(request.POST, instance=pref_user)
        if form.is_valid():
            preferensi = form.save(commit=False)
            preferensi.user = request.user
            preferensi.save()
            form.save_m2m() 
            return redirect('dashboard')
    else:
        form = PreferensiForm(instance=pref_user)

    return render(request, 'preferensi.html', {'form': form})

# ==========================================
# 5. LOGOUT
# ==========================================
def logout_view(request):
    logout(request)
    # Redirect ke landing page setelah logout
    return redirect('landing_page') 

# ==========================================
# 6. DETAIL PRODUK & RATING
# ==========================================
@login_required
def detail_produk_view(request, produk_id):
    produk = get_object_or_404(Produk, id=produk_id)
    penilaian_user = Penilaian.objects.filter(user=request.user, produk=produk).first()
    
    if request.method == 'POST':
        rating_input = request.POST.get('rating')
        ulasan_input = request.POST.get('ulasan')
        
        if rating_input:
            Penilaian.objects.update_or_create(
                user=request.user,
                produk=produk,
                defaults={
                    'rating': rating_input,
                    'ulasan': ulasan_input
                }
            )
            messages.success(request, "Terima kasih! Rating Anda telah disimpan.")
            return redirect('detail_produk', produk_id=produk.id)

    semua_ulasan = Penilaian.objects.filter(produk=produk).order_by('-tanggal')

    context = {
        'produk': produk,
        'penilaian_user': penilaian_user,
        'semua_ulasan': semua_ulasan,
    }
    return render(request, 'detail_produk.html', context)