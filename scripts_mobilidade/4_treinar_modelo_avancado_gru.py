# 4_treinar_modelo_avancado_gru.py (Versão com salvamento de resultados)
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU, Dense, InputLayer
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import matplotlib.pyplot as plt
import config

def create_sequences(data, features, target, sequence_length):
    X, y, ids = [], [], []
    for id_mun, group in data.groupby('id_municipio'):
        group = group.sort_values('ano')
        feature_data = group[features].values
        target_data = group[target].values
        if len(group) > sequence_length:
            for i in range(len(group) - sequence_length):
                X.append(feature_data[i:(i + sequence_length)])
                y.append(target_data[i + sequence_length])
                ids.append(group.iloc[i + sequence_length]['id_municipio']) # Salva o ID do município para cada sequência
    return np.array(X), np.array(y), np.array(ids)

def run():
    print("--- INICIANDO SCRIPT 4: TREINAMENTO DO MODELO AVANÇADO (GRU) ---")
    df = pd.read_csv(config.OUTPUT_PATHS['ml_dataset'])
    df.fillna(0, inplace=True)
    
    FEATURES = ['populacao', 'casos_ano_anterior', 'centralidade_grau', 'centralidade_intermediacao', 'risco_importado', 'casos_hanseniase']
    TARGET = 'casos_hanseniase'
    
    train_df = df[df['ano'] < config.ANO_FINAL_ANALISE]
    test_df = df[df['ano'] == config.ANO_FINAL_ANALISE]

    scaler_features = MinMaxScaler()
    scaler_target = MinMaxScaler()

    train_df[FEATURES] = scaler_features.fit_transform(train_df[FEATURES])
    train_df[[TARGET]] = scaler_target.fit_transform(train_df[[TARGET]])

    SEQUENCE_LENGTH = 1
    X_train, y_train, _ = create_sequences(train_df, FEATURES, TARGET, SEQUENCE_LENGTH)

    if X_train.shape[0] == 0:
        print("ERRO: Nenhuma sequência de treino pôde ser criada.")
        return

    print(f"Dados de treino transformados em {len(X_train)} sequências.")

    model = Sequential([
        InputLayer(shape=(X_train.shape[1], X_train.shape[2])),
        GRU(50, return_sequences=True),
        GRU(50),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    model.summary()
    
    print("\nTreinando o modelo GRU...")
    model.fit(X_train, y_train, epochs=20, batch_size=32, validation_split=0.2, verbose=1)
    
    last_train_year_df = df[df['ano'] == config.ANO_FINAL_ANALISE - 1]
    predict_sequence_df = pd.concat([last_train_year_df, test_df])
    predict_sequence_df[FEATURES] = scaler_features.transform(predict_sequence_df[FEATURES])
    predict_sequence_df[[TARGET]] = scaler_target.transform(predict_sequence_df[[TARGET]])
    
    X_test, y_test_scaled, ids_test = create_sequences(predict_sequence_df, FEATURES, TARGET, SEQUENCE_LENGTH)
    
    print("\nFazendo previsões no conjunto de teste...")
    predictions_scaled = model.predict(X_test)
    
    predictions = scaler_target.inverse_transform(predictions_scaled)
    y_test = scaler_target.inverse_transform(y_test_scaled.reshape(-1, 1))
    
    print("\n--- AVALIAÇÃO DO MODELO GRU ---")
    r2 = r2_score(y_test, predictions)
    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    
    print(f"R² (Coeficiente de Determinação): {r2:.4f}")
    print(f"MAE (Erro Médio Absoluto): {mae:.4f}")
    print(f"RMSE (Raiz do Erro Quadrático Médio): {rmse:.4f}")

    # NOVO: Salvar os resultados da predição em um arquivo CSV
    results_df = pd.DataFrame({
        'id_municipio': ids_test,
        'casos_reais': y_test.flatten(),
        'casos_previstos': predictions.flatten()
    })
    
    # Adicionar nomes dos municípios para facilitar
    nomes_municipios = df[['id_municipio', 'nome_municipio']].drop_duplicates()
    results_df = pd.merge(results_df, nomes_municipios, on='id_municipio', how='left')
    
    output_path = config.RESULTS_PATH / f"resultados_predicao_gru_{config.ANO_FINAL_ANALISE}.csv"
    results_df.to_csv(output_path, index=False)
    print(f"\nPrevisões do modelo GRU salvas em: {output_path}")

    print("--- SCRIPT 4 CONCLUÍDO ---")

if __name__ == '__main__':
    run()