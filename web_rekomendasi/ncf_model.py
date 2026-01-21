import tensorflow as tf
from tensorflow.keras.layers import Input, Embedding, Flatten, Concatenate, Dense
from tensorflow.keras.models import Model

def build_ncf_model(num_users, num_items, embedding_size=50):
    # 1. INPUT LAYER
    # Menerima ID User dan ID Produk (sudah di-encode jadi angka 0,1,2...)
    user_input = Input(shape=(1,), name='user_input')
    item_input = Input(shape=(1,), name='item_input')

    # 2. EMBEDDING LAYER (Mengubah ID jadi Vektor)
    # User Embedding
    user_embedding = Embedding(input_dim=num_users, output_dim=embedding_size, name='user_embedding')(user_input)
    user_vec = Flatten()(user_embedding)

    # Item Embedding
    item_embedding = Embedding(input_dim=num_items, output_dim=embedding_size, name='item_embedding')(item_input)
    item_vec = Flatten()(item_embedding)

    # 3. CONCATENATE (Menggabungkan Vektor User & Item)
    merged = Concatenate()([user_vec, item_vec])

    # 4. MLP LAYERS (Jaringan Syaraf Tiruan)
    # Layer 1
    dense_1 = Dense(128, activation='relu')(merged)
    # Layer 2 (Dropout untuk mencegah overfitting opsional)
    dense_2 = Dense(64, activation='relu')(dense_1)
    
    # 5. OUTPUT LAYER
    # Satu neuron output (Prediksi Rating 1-5)
    output = Dense(1, activation='linear', name='output')(dense_2)

    # Gabungkan jadi Model
    model = Model(inputs=[user_input, item_input], outputs=output)
    model.compile(optimizer='adam', loss='mean_squared_error')
    
    return model