import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU, Dense, Dropout

# Configurações
dir_graficos = "./scripts_artigo/graficos/series_temporais"
dir_relatorios = "./scripts_artigo/relatorios"
os.makedirs(dir_graficos, exist_ok=True)

print("Carregando dados para modelagem GRU...")
df = pd.read_csv(str(config.PATHS['hanceniase']), low_memory=False)
df['DT_NOTIFIC'] = pd.to_datetime(df['DT_NOTIFIC'])
ts = df.set_index('DT_NOTIFIC').resample('M').size()

# 1. Preparação dos Dados (Train/Test)
# Pré-pandemia para treino
train_data = ts[ts.index < '2020-03-01'].values.reshape(-1, 1)
test_data = ts[ts.index >= '2020-03-01'].values.reshape(-1, 1)

scaler = MinMaxScaler()
train_scaled = scaler.fit_transform(train_data)

def create_dataset(dataset, look_back=12):
    X, Y = [], []
    for i in range(len(dataset) - look_back):
        X.append(dataset[i:(i + look_back), 0])
        Y.append(dataset[i + look_back, 0])
    return np.array(X), np.array(Y)

look_back = 12
X_train, y_train = create_dataset(train_scaled, look_back)
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

# 2. Construção do Modelo GRU
print("Treinando modelo GRU...")
model = Sequential([
    GRU(50, return_sequences=True, input_shape=(look_back, 1)),
    Dropout(0.2),
    GRU(50),
    Dropout(0.2),
    Dense(1)
])

model.compile(optimizer='adam', loss='mean_squared_error')
model.fit(X_train, y_train, epochs=50, batch_size=8, verbose=0)

# 3. Predição do Cenário Contra-factual (Pandêmico)
inputs = ts[len(ts) - len(test_data) - look_back:].values.reshape(-1, 1)
inputs = scaler.transform(inputs)

X_test, _ = create_dataset(inputs, look_back)
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

pred_scaled = model.predict(X_test)
pred_gru = scaler.inverse_transform(pred_scaled).flatten()

# 4. Salvar resultados para integração
df_gru = pd.DataFrame({
    'Data': ts.index[ts.index >= '2020-03-01'],
    'Real': ts[ts.index >= '2020-03-01'].values,
    'GRU_Pred': pred_gru
})
df_gru.to_csv(f"{dir_relatorios}/predicoes_gru.csv", index=False)

# Gráfico GRU
plt.figure(figsize=(12, 6))
plt.plot(ts, label='Real', color='black')
plt.plot(df_gru['Data'], df_gru['GRU_Pred'], label='Predição GRU (Cenário Sem Pandemia)', color='purple', linestyle='--')
plt.axvline(pd.Timestamp('2020-03-01'), color='gray', linestyle='--')
plt.title("Predição de Longo Prazo via GRU (Ajustado Pré-Pandemia)")
plt.legend()
plt.savefig(f"{dir_graficos}/gru_forecasting.png")
plt.close()

print("Modelagem GRU concluída.")
