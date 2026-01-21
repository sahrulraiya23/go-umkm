from django.core.management.base import BaseCommand
from web_rekomendasi.models import Penilaian
from web_rekomendasi.ncf_model import build_ncf_model
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error

class Command(BaseCommand):
    help = 'Menghitung Akurasi Model (RMSE & MAE) untuk Bab 4 Skripsi'

    def handle(self, *args, **kwargs):
        self.stdout.write("--- MEMULAI EVALUASI MODEL NCF ---")

        # 1. Ambil Semua Data Rating
        ratings = list(Penilaian.objects.all().values('user_id', 'produk_id', 'rating'))
        df = pd.DataFrame(ratings)

        # Cek jumlah data
        jumlah_data = len(df)
        self.stdout.write(f"Total Data Rating: {jumlah_data}")

        if jumlah_data < 10:
            self.stdout.write(self.style.ERROR("Data terlalu sedikit (<10). Tambahkan rating dummy dulu minimal 20-50 agar valid."))
            return

        # 2. Encoding (Mapping ID ke Angka 0,1,2...)
        user_ids = df['user_id'].unique().tolist()
        item_ids = df['produk_id'].unique().tolist()

        user2user_encoded = {x: i for i, x in enumerate(user_ids)}
        item2item_encoded = {x: i for i, x in enumerate(item_ids)}

        df['user'] = df['user_id'].map(user2user_encoded)
        df['item'] = df['produk_id'].map(item2item_encoded)

        num_users = len(user2user_encoded)
        num_items = len(item2item_encoded)

        # 3. Split Data (80% Training, 20% Testing)
        # Ini standar skripsi: Model belajar dari 80% data, lalu diuji dengan 20% sisanya.
        X = df[['user', 'item']].values
        y = df['rating'].values

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.stdout.write(f"Data Training: {len(X_train)} | Data Testing: {len(X_test)}")

        # 4. Bangun & Latih Model (Dari Scratch)
        model = build_ncf_model(num_users, num_items)
        
        print("\nMelatih model pada data training...")
        # Train model (Epoch dikit aja buat evaluasi cepat)
        model.fit(
            [X_train[:, 0], X_train[:, 1]], 
            y_train, 
            epochs=10, 
            batch_size=32, 
            verbose=0 # Supaya ga menuhin layar
        )

        # 5. Prediksi pada Data Testing
        print("Melakukan prediksi pada data testing...")
        y_pred = model.predict([X_test[:, 0], X_test[:, 1]]).flatten()

        # 6. Hitung Error (RMSE & MAE)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))

        # 7. Tampilkan Hasil
        self.stdout.write("\n" + "="*30)
        self.stdout.write("HASIL EVALUASI (BAB 4)")
        self.stdout.write("="*30)
        self.stdout.write(f"MAE  (Mean Absolute Error): {mae:.4f}")
        self.stdout.write(f"RMSE (Root Mean Sq. Error): {rmse:.4f}")
        self.stdout.write("="*30)

        # Interpretasi Sederhana
        if rmse < 1.0:
            kualitas = "SANGAT BAIK (Error < 1 Bintang)"
        elif rmse < 1.5:
            kualitas = "CUKUP BAIK (Error masih wajar)"
        else:
            kualitas = "KURANG (Perlu lebih banyak data rating)"
            
        self.stdout.write(f"Kesimpulan Model: {kualitas}")