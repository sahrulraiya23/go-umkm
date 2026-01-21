from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Produk, Penilaian, PreferensiPengguna
from .forms import UserRegisterForm, PreferensiForm
from .recommender import get_rekomendasi
from django.db.models import Q # Tambahkan ini di paling atas untuk fitur search

# ==========================================
# 1. DASHBOARD (HALAMAN UTAMA)
# ==========================================
@login_required(login_url='/login/')
def dashboard(request):
    user = request.user
    
    # 1. LOGIKA REKOMENDASI (Tidak Berubah)
    try:
        rekomendasi_list = get_rekomendasi(user.id, n=4)
    except Exception as e:
        print(f"Error di Algoritma: {e}")
        rekomendasi_list = []

    if rekomendasi_list is None:
        rekomendasi_list = []
    
    is_new_user = not Penilaian.objects.filter(user=user).exists()
    
    # 2. LOGIKA PENCARIAN & KATALOG (Ini yang diubah)
    search_query = request.GET.get('q') # Ambil kata kunci dari URL (?q=bakso)

    if search_query:
        # Jika user mencari sesuatu, cari di nama produk atau deskripsi atau nama UMKM
        all_produk = Produk.objects.filter(
            Q(nama_produk__icontains=search_query) | 
            Q(deskripsi__icontains=search_query) |
            Q(umkm__nama_umkm__icontains=search_query)
        )
    else:
        # Jika tidak mencari, tampilkan 20 produk terbaru seperti biasa
        all_produk = Produk.objects.all().order_by('-id')[:20]

    context = {
        'rekomendasi_list': rekomendasi_list,
        'all_produk': all_produk,
        'is_new_user': is_new_user,
        'search_query': search_query, # Kirim balik ke HTML agar text tidak hilang
    }
    
    return render(request, 'dashboard.html', context)
# ==========================================
# 2. REGISTER USER BARU
# ==========================================
def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('pilih_preferensi')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

# ==========================================
# 3. PILIH PREFERENSI (KNN COLD START)
# ==========================================
@login_required
@login_required
def pilih_preferensi_view(request):
    # --- PERBAIKAN DI SINI ---
    # Gunakan .filter().first() untuk mencari data dengan aman.
    # Jika tidak ada, hasilnya None (tidak akan error).
    pref_user = PreferensiPengguna.objects.filter(user=request.user).first()
    # -------------------------

    if request.method == 'POST':
        # Jika pref_user None, form akan membuat data baru.
        # Jika pref_user ada, form akan meng-update data tersebut.
        form = PreferensiForm(request.POST, instance=pref_user)
        if form.is_valid():
            preferensi = form.save(commit=False)
            preferensi.user = request.user
            preferensi.save()
            form.save_m2m() # Penting untuk menyimpan checkbox kategori
            return redirect('dashboard')
    else:
        form = PreferensiForm(instance=pref_user)

    return render(request, 'preferensi.html', {'form': form})
# ==========================================
# 4. LOGOUT
# ==========================================
def logout_view(request):
    logout(request)
    return redirect('login')

# ==========================================
# 5. DETAIL PRODUK & RATING
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