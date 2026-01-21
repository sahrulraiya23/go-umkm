import os
import pickle
import numpy as np
import pandas as pd
from django.conf import settings
from .models import Penilaian, Produk, PreferensiPengguna
from tensorflow.keras.models import load_model

# ==========================================
# 1. LOGIKA UTAMA & KNN (TETAP SAMA)
# ==========================================
# ... (Bagian get_rekomendasi dan knn_cold_start JANGAN DIHAPUS / Biarkan seperti sebelumnya) ...
# Biar aman, copas ulang saja full satu file ini:

def get_rekomendasi(user_id, n=10):
    cek_interaksi = Penilaian.objects.filter(user_id=user_id).exists()
    if cek_interaksi:
        return ncf_recommendation(user_id, n)
    else:
        return knn_cold_start(user_id, n)

def knn_cold_start(user_id, n=10):
    preferensi = PreferensiPengguna.objects.filter(user_id=user_id).first()
    if not preferensi: return Produk.objects.all().order_by('?')[:n]
    kategori_ids = list(preferensi.kategori_disukai.values_list('id', flat=True))
    if not kategori_ids: return Produk.objects.all().order_by('?')[:n]
    return Produk.objects.filter(kategori_id__in=kategori_ids).order_by('?')[:n] 

# ==========================================
# 2. ALGORITMA NCF (ASLI / LIVE PREDICTION)
# ==========================================

def ncf_recommendation(user_id, n=10):
    # Path ke file model & mapping
    model_path = os.path.join(settings.BASE_DIR, 'ml_data', 'ncf_model.h5')
    map_path = os.path.join(settings.BASE_DIR, 'ml_data', 'mappings.pkl')

    # Cek apakah model sudah dilatih?
    if not os.path.exists(model_path) or not os.path.exists(map_path):
        print("Model NCF belum dilatih! Menggunakan fallback random.")
        return Produk.objects.all().order_by('?')[:n]

    # Load Mapping
    with open(map_path, 'rb') as f:
        mappings = pickle.load(f)
    
    u2u = mappings['user2user_encoded']
    i2i = mappings['item2item_encoded']
    i_enc2i = mappings['item_encoded2item']

    # Cek apakah user ini ada dalam 'pengetahuan' model?
    # Jika user baru daftar SETELAH training terakhir, model tidak kenal dia.
    if user_id not in u2u:
        print(f"User {user_id} belum dikenal model (perlu training ulang). Fallback ke Popular/Random.")
        return Produk.objects.all().order_by('?')[:n]

    # --- PROSES PREDIKSI ---
    
    # 1. Siapkan Kandidat (Produk yang BELUM dirating user ini)
    #    Kita hanya memprediksi produk yang belum dibeli/rating.
    all_produk_ids = list(Produk.objects.values_list('id', flat=True))
    rated_produk_ids = list(Penilaian.objects.filter(user_id=user_id).values_list('produk_id', flat=True))
    
    unrated_ids = [pid for pid in all_produk_ids if pid not in rated_produk_ids]
    
    # Filter hanya produk yang 'dikenal' model (ada di mapping)
    candidate_items = [pid for pid in unrated_ids if pid in i2i]

    if not candidate_items:
        return []

    # 2. Encode Input untuk TensorFlow
    #    Kita butuh array: [User_Index, Item_Index] untuk setiap kandidat
    user_encoded = u2u[user_id]
    
    user_input = np.array([user_encoded] * len(candidate_items))
    item_input = np.array([i2i[pid] for pid in candidate_items])

    # 3. Load Model & Prediksi (Hanya load sekali idealnya, tapi ini ok untuk skripsi)
    model = load_model(model_path)
    
    # Prediksi Rating (Output berupa array float, misal [4.5, 3.2, ...])
    predictions = model.predict([user_input, item_input], verbose=0)
    
    # 4. Urutkan Hasil Prediksi (Rating Tertinggi ke Terendah)
    #    Gabungkan ID Produk dengan Skor Prediksinya
    pred_list = []
    for i, pid in enumerate(candidate_items):
        score = predictions[i][0]
        pred_list.append((pid, score))
    
    # Sort descending (besar ke kecil)
    pred_list.sort(key=lambda x: x[1], reverse=True)
    
    # Ambil Top-N ID
    top_n_ids = [pid for pid, score in pred_list[:n]]
    
    # 5. Ambil Objek Produk dari Database (Preserve Order)
    #    Django filter tidak menjamin urutan, jadi kita sort manual atau pakai logic ini:
    rekomendasi_final = []
    for pid in top_n_ids:
        rekomendasi_final.append(Produk.objects.get(id=pid))
        
    return rekomendasi_final