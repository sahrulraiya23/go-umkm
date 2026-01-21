from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from web_rekomendasi.models import UMKM, Kategori, Produk, Penilaian, PreferensiPengguna
import random

class Command(BaseCommand):
    help = 'Mengisi database dengan data dummy untuk pengujian KNN dan NCF'

    def handle(self, *args, **kwargs):
        self.stdout.write('Menghapus data lama...')
        # Urutan hapus penting karena Foreign Key
        Penilaian.objects.all().delete()
        PreferensiPengguna.objects.all().delete()
        Produk.objects.all().delete()
        UMKM.objects.all().delete()
        Kategori.objects.all().delete()
        User.objects.exclude(username='admin').delete() # Sisakan admin

        self.stdout.write('Membuat Kategori...')
        # Sesuai Proposal Tabel 3.4 
        list_kategori = ['Kuliner', 'Kerajinan', 'Fashion', 'Jasa']
        kategori_objs = [Kategori.objects.create(nama_kategori=k) for k in list_kategori]

        self.stdout.write('Membuat Data UMKM...')
        # Sesuai Proposal [cite: 532]
        list_umkm = ['UMKM Asinan Myesha', 'UMKM Anyaman Kendari', 'UMKM Tenun Sultra', 'Warung Bakso Ikan']
        umkm_objs = []
        for nama in list_umkm:
            umkm = UMKM.objects.create(
                nama_umkm=nama,
                alamat='Jl. Contoh No. 123, Kendari',
                no_telepon='08123456789',
                deskripsi=f'UMKM yang memproduksi {nama}'
            )
            umkm_objs.append(umkm)

        self.stdout.write('Membuat Produk...')
        # Membuat 20 produk dummy
        produk_objs = []
        for i in range(20):
            kategori = random.choice(kategori_objs)
            umkm = random.choice(umkm_objs)
            produk = Produk.objects.create(
                umkm=umkm,
                kategori=kategori,
                nama_produk=f"Produk {kategori.nama_kategori} {i+1}",
                harga=random.randint(10000, 150000),
                deskripsi="Deskripsi contoh produk UMKM Kendari",
                # gambar_produk kosong dulu
            )
            produk_objs.append(produk)

        self.stdout.write('Membuat User & Skenario...')
        
        # --- SKENARIO 1: USER BARU (COLD START - KNN) ---
        # User ini BELUM pernah rating, tapi punya preferensi kategori
        user_baru = User.objects.create_user(username='user_baru', email='baru@test.com', password='password123')
        
        # Set Preferensi: Suka 'Kuliner' dan 'Kerajinan' (Sesuai contoh proposal) [cite: 636]
        pref = PreferensiPengguna.objects.create(user=user_baru)
        kat_pilihan = Kategori.objects.filter(nama_kategori__in=['Kuliner', 'Kerajinan'])
        pref.kategori_disukai.set(kat_pilihan)
        self.stdout.write(f'-> Dibuat: {user_baru.username} (Scenario KNN/Cold Start)')

        # --- SKENARIO 2: USER LAMA (WARM START - NCF) ---
        # User ini SUDAH punya rating (history interaksi)
        user_lama = User.objects.create_user(username='user_lama', email='lama@test.com', password='password123')
        
        # Beri 5 rating random
        for _ in range(5):
            prod = random.choice(produk_objs)
            # Pastikan tidak duplikat rating
            if not Penilaian.objects.filter(user=user_lama, produk=prod).exists():
                Penilaian.objects.create(
                    user=user_lama,
                    produk=prod,
                    rating=random.randint(3, 5), # Rating bagus
                    ulasan="Produk mantap!"
                )
        self.stdout.write(f'-> Dibuat: {user_lama.username} (Scenario NCF/Warm Start)')

        self.stdout.write(self.style.SUCCESS('Selesai! Database telah diisi.'))