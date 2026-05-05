import os
import pandas as pd
import numpy as np
import joblib
import umap
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import sys

# Importar config da raiz
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
try:
    import config
except ImportError:
    pass

BASE_DIR = os.path.dirname(__file__)

def extrair_idade(valor):
    try:
        valor_str = str(int(float(valor))).zfill(4)
        unidade = int(valor_str[0])
        quantidade = int(valor_str[1:])
        if unidade == 4: return quantidade
        return 0
    except: return 0

def prepare_dynamic_data():
    print("🚀 Gerando dados dinâmicos para o Dashboard...")

    # 1. Carregar Dados Brutos (mesmo do config)
    try:
        path_data = str(config.PATHS['hanceniase'])
        df = pd.read_csv(path_data, low_memory=False)
    except:
        print("⚠️ Erro ao carregar dados do config. Tentando fallback...")
        return

    # 2. Engenharia de Features (Sincronizado com prepare_shiny_data.py)
    print("🛠️ Processando Engenharia de Features...")
    df['Idade'] = df['NU_IDADE_N'].apply(extrair_idade)
    df['Sexo_Masc'] = df['CS_SEXO'].map({'M': 1, 'F': 0, '1': 1, '0': 0, 1: 1, 0: 0}).fillna(0)
    df['Class_MB'] = df['CLASSOPERA'].map({'1': 0, '2': 1, 1: 0, 2: 1}).fillna(0)
    
    # Colunas numéricas
    for col in ['NU_LESOES', 'NERVOSAFET', 'DOSE_RECEB', 'AVALIA_N']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    features_model = ['Idade', 'NU_LESOES', 'NERVOSAFET', 'Class_MB', 'Sexo_Masc', 'DOSE_RECEB']
    
    # Filtrar válidos para clustering (onde houve avaliação)
    df_valid = df[df['AVALIA_N'].isin([1, 2, 3])].copy()
    
    # --- ETAPA 1: Dados de Agrupamento (UMAP + Clusters) ---
    print("📍 Processando UMAP e Clusters...")
    
    df_sample = df_valid.sample(min(10000, len(df_valid)), random_state=42)
    X = df_sample[features_model].values
    X_scaled = StandardScaler().fit_transform(X)

    reducer = umap.UMAP(n_neighbors=30, min_dist=0.1, n_components=2, random_state=42)
    embedding = reducer.fit_transform(X_scaled)

    kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)

    df_umap = pd.DataFrame({
        'UMAP_1': embedding[:, 0],
        'UMAP_2': embedding[:, 1],
        'Cluster': clusters,
        'Idade': df_sample['Idade'],
        'GIF': df_sample['AVALIA_N'] - 1, # Normalizar para 0, 1, 2
        'Nervos': df_sample['NERVOSAFET']
    })
    df_umap.to_csv(os.path.join(BASE_DIR, "cluster_plot_data.csv"), index=False)

    # --- ETAPA 2: Médias de Risco para Calculadora ---
    print("📊 Calculando médias de referência...")
    perfil = df_sample.groupby(clusters)[features_model].mean()
    perfil.to_csv(os.path.join(BASE_DIR, "cluster_averages.csv"))

    # --- ETAPA 3: Dados Socio-Clínicos ---
    print("🌍 Processando indicadores socio-clínicos...")
    # Taxa de G2D (Grau 2) por categoria
    df['G2D'] = (df['AVALIA_N'] == 3).astype(int) # SINAN bruto 3 = Grau II
    
    social_sexo = df.groupby('Sexo_Masc')['G2D'].mean().reset_index()
    social_sexo['Sexo_Masc'] = social_sexo['Sexo_Masc'].map({1: 'Masculino', 0: 'Feminino'})
    
    social_classe = df.groupby('Class_MB')['G2D'].mean().reset_index()
    social_classe['Class_MB'] = social_classe['Class_MB'].map({1: 'Multibacilar (MB)', 0: 'Paucibacilar (PB)'})
    
    social_sexo.to_csv(os.path.join(BASE_DIR, "social_sexo.csv"), index=False)
    social_classe.to_csv(os.path.join(BASE_DIR, "social_classe.csv"), index=False)

    # --- ETAPA 4: Importância Global ---
    print("🔑 Exportando importância das variáveis...")
    try:
        risk_bundle = joblib.load(os.path.join(BASE_DIR, "model_risk.joblib"))
        models = risk_bundle.get('models', {})
        # Fallback para modelo único
        model = models.get('lgbm') if models else risk_bundle.get('model')
        
        if model:
            feat_imp = pd.DataFrame({
                'Feature': risk_bundle['features'],
                'Importance': model.feature_importances_
            }).sort_values('Importance', ascending=True)
            feat_imp.to_csv(os.path.join(BASE_DIR, "global_importance.csv"), index=False)
    except:
        pass

    print("✅ Todos os dados dinâmicos foram salvos com sucesso.")

if __name__ == "__main__":
    prepare_dynamic_data()
