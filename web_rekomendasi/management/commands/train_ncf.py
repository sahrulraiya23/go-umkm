from django.core.management.base import BaseCommand
from web_rekomendasi.models import Penilaian, User, Produk
from web_rekomendasi.ncf_model import build_ncf_model
import pandas as pd
import numpy as np
import pickle
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Melatih Model NCF berdasarkan data rating terbaru'

    def handle(self, *args, **kwargs):
        self.stdout.write("Mengambil data rating dari database...")
        
        # 1. AMBIL DATA
        ratings = list(Penilaian.objects.all().values('user_id', 'produk_id', 'rating'))
        df = pd.DataFrame(ratings)
        
        if df.empty:
            self.stdout.write(self.style.ERROR("Data rating kosong! Isi dummy data dulu."))
            return

        # 2. ENCODING ID (Mapping ID Asli Database ke Index 0,1,2...)
        # TensorFlow butuh input berurutan mulai dari 0
        user_ids = df['user_id'].unique().tolist()
        item_ids = df['produk_id'].unique().tolist()

        # Buat Peta (Dictionary): ID Asli -> Index Baru
        user2user_encoded = {x: i for i, x in enumerate(user_ids)}
        item2item_encoded = {x: i for i, x in enumerate(item_ids)}
        
        # Peta Balik: Index Baru -> ID Asli (Untuk menerjemahkan hasil prediksi nanti)
        item_encoded2item = {i: x for i, x in enumerate(item_ids)}

        # Terapkan encoding ke Dataframe
        df['user'] = df['user_id'].map(user2user_encoded)
        df['item'] = df['produk_id'].map(item2item_encoded)

        num_users = len(user2user_encoded)
        num_items = len(item2item_encoded)

        self.stdout.write(f"Data siap: {len(df)} rating, {num_users} users, {num_items} items.")

        # 3. TRAINING MODEL
        self.stdout.write("Membangun & Melatih Model...")
        model = build_ncf_model(num_users, num_items)
        
        # Input: [List User Index, List Item Index], Target: Rating
        X = [df['user'].values, df['item'].values]
        y = df['rating'].values

        # Latih selama 10 epoch (putaran)
        model.fit(X, y, epochs=10, batch_size=32, verbose=1)

        # 4. SIMPAN MODEL & MAPPING
        # Kita simpan di folder 'ml_data' agar rapi
        path = os.path.join(settings.BASE_DIR, 'ml_data')
        if not os.path.exists(path):
            os.makedirs(path)

        # Simpan Model (.h5)
        model.save(os.path.join(path, 'ncf_model.h5'))
        
        # Simpan Mapping (.pkl) agar recommender tau cara baca modelnya
        mappings = {
            'user2user_encoded': user2user_encoded,
            'item2item_encoded': item2item_encoded,
            'item_encoded2item': item_encoded2item
        }
        with open(os.path.join(path, 'mappings.pkl'), 'wb') as f:
            pickle.dump(mappings, f)

        self.stdout.write(self.style.SUCCESS("BERHASIL! Model NCF dan Mapping telah disimpan."))