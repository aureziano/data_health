# 3_treinar_modelo_preditivo.py (VERSÃO COM FEATURES DE SÉRIE TEMPORAL)
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import numpy as np
import config

def run():
    print("--- INICIANDO SCRIPT 3: TREINAMENTO DO MODELO PREDITIVO COM DADOS ENRIQUECIDOS ---")
    
    # Carregar o dataset final
    df = pd.read_csv(config.OUTPUT_PATHS['ml_dataset'])
    
    # NOVO: Adicionar as novas features de série temporal à lista de preditores
    FEATURES = [
        'populacao', 
        'casos_ano_anterior', 
        'centralidade_grau', 
        'centralidade_intermediacao',
        'risco_importado',
        'media_movel_3a',   # <-- NOVA FEATURE
        'tendencia_2a'      # <-- NOVA FEATURE
    ]
    TARGET = 'casos_hanseniase'
    
    df.fillna(0, inplace=True)
    df = df[df['populacao'] > 0]

    # Dividir em treino e teste
    train_df = df[df['ano'] < config.ANO_FINAL_ANALISE]
    test_df = df[df['ano'] == config.ANO_FINAL_ANALISE]

    X_train = train_df[FEATURES]
    y_train = train_df[TARGET]
    X_test = test_df[FEATURES]
    y_test = test_df[TARGET]
    
    print(f"Dados divididos: {len(X_train)} registros para treino, {len(X_test)} para teste.")
    
    # Treinar o modelo
    print("Treinando o modelo RandomForestRegressor...")
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    # Fazer previsões
    predictions = model.predict(X_test)
    
    # Avaliar o modelo
    print("\n--- AVALIAÇÃO DO MODELO ---")
    r2 = r2_score(y_test, predictions)
    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    
    print(f"R² (Coeficiente de Determinação): {r2:.4f}")
    print(f"MAE (Erro Médio Absoluto): {mae:.4f}")
    print(f"RMSE (Raiz do Erro Quadrático Médio): {rmse:.4f}")

    results_df = test_df[['id_municipio', 'nome_municipio', 'sigla_uf', 'ano']].copy()
    results_df['casos_reais'] = y_test
    results_df['casos_previstos'] = predictions
    results_df.to_csv(config.OUTPUT_PATHS['model_results'], index=False)
    print(f"\nPrevisões salvas em: {config.OUTPUT_PATHS['model_results']}")
    
    # Análise de Importância das Features (Interpretabilidade - XAI)
    print("\n--- IMPORTÂNCIA DAS FEATURES ---")
    feature_importance = pd.Series(model.feature_importances_, index=FEATURES).sort_values(ascending=False)
    print(feature_importance)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x=feature_importance, y=feature_importance.index)
    plt.title('Importância de Cada Variável no Modelo Preditivo')
    plt.xlabel('Importância')
    plt.ylabel('Variável')
    plt.tight_layout()
    plt.savefig(config.OUTPUT_PATHS['feature_importance_plot'])
    print(f"Gráfico de importância das features salvo em: {config.OUTPUT_PATHS['feature_importance_plot']}")
    
    # Gráfico de Previsões vs. Real
    plt.figure(figsize=(10, 10))
    sample_df = results_df.sample(n=min(len(results_df), 1000), random_state=42)
    plt.scatter(sample_df['casos_reais'], sample_df['casos_previstos'], alpha=0.5)
    plt.plot([0, max(sample_df['casos_reais'])], [0, max(sample_df['casos_reais'])], 'r--')
    plt.title('Previsões do Modelo vs. Casos Reais')
    plt.xlabel('Casos Reais')
    plt.ylabel('Casos Previstos')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig(config.OUTPUT_PATHS['prediction_plot'])
    print(f"Gráfico de previsões salvo em: {config.OUTPUT_PATHS['prediction_plot']}")
    print("--- SCRIPT 3 CONCLUÍDO ---")

if __name__ == '__main__':
    run()