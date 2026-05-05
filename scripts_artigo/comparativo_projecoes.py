import os
import config
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import umap
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.manifold import trustworthiness
import time

# Configurações
DIR_GRAFICOS = "./overleaf/fig"
DIR_RELATORIOS = "./overleaf/tabs"
os.makedirs(DIR_GRAFICOS, exist_ok=True)
os.makedirs(DIR_RELATORIOS, exist_ok=True)

def main():
    print("Iniciando Comparativo de Projeções (PCA vs t-SNE vs UMAP)...")
    
    # 1. Carregamento e Limpeza Básica
    df = pd.read_csv(str(config.PATHS['hanceniase']), low_memory=False)
    
    # Seleção de variáveis e tratamento (As mesmas de analise_incapacidade.py)
    features = ['NU_IDADE_N', 'AVALIA_N', 'NU_LESOES', 'NERVOSAFET', 'CLASSOPERA', 'CS_SEXO', 'CS_RACA']
    df_clean = df[features].copy()
    
    # Codificação simples
    df_clean['CS_SEXO'] = df_clean['CS_SEXO'].map({'M': 1, 'F': 0}).fillna(-1)
    df_clean['CLASSOPERA'] = df_clean['CLASSOPERA'].map({'1': 0, '2': 1, 1: 0, 2: 1}).fillna(-1)
    
    for col in features:
        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    df_clean = df_clean.dropna()
    
    # Amostragem para agilizar processamento do t-SNE
    if len(df_clean) > 8000:
        df_sample = df_clean.sample(8000, random_state=42)
    else:
        df_sample = df_clean
        
    X = StandardScaler().fit_transform(df_sample.values)
    
    resultados = []
    
    # 2. PCA
    print("Executando PCA...")
    start = time.time()
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)
    t_pca = time.time() - start
    tw_pca = trustworthiness(X, X_pca)
    resultados.append({"Método": "PCA", "Tempo (s)": t_pca, "Trustworthiness": tw_pca})
    
    # 3. t-SNE
    print("Executando t-SNE...")
    start = time.time()
    tsne = TSNE(n_components=2, random_state=42, n_jobs=-1)
    X_tsne = tsne.fit_transform(X)
    t_tsne = time.time() - start
    tw_tsne = trustworthiness(X, X_tsne)
    resultados.append({"Método": "t-SNE", "Tempo (s)": t_tsne, "Trustworthiness": tw_tsne})
    
    # 4. UMAP
    print("Executando UMAP...")
    start = time.time()
    reducer = umap.UMAP(n_components=2, random_state=42)
    X_umap = reducer.fit_transform(X)
    t_umap = time.time() - start
    tw_umap = trustworthiness(X, X_umap)
    resultados.append({"Método": "UMAP", "Tempo (s)": t_umap, "Trustworthiness": tw_umap})
    
    # 5. Visualização Comparativa
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    
    axes[0].scatter(X_pca[:, 0], X_pca[:, 1], s=1, alpha=0.5)
    axes[0].set_title(f"PCA (TW: {tw_pca:.3f})")
    
    axes[1].scatter(X_tsne[:, 0], X_tsne[:, 1], s=1, alpha=0.5, color='orange')
    axes[1].set_title(f"t-SNE (TW: {tw_tsne:.3f})")
    
    axes[2].scatter(X_umap[:, 0], X_umap[:, 1], s=1, alpha=0.5, color='green')
    axes[2].set_title(f"UMAP (TW: {tw_umap:.3f})")
    
    plt.suptitle("Comparativo de Técnicas de Redução de Dimensionalidade")
    plt.savefig(f"{DIR_GRAFICOS}/comparativo_projecoes.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # 6. Salvar Métricas para o LaTeX
    df_res = pd.DataFrame(resultados)
    df_res.to_csv(f"{DIR_RELATORIOS}/metricas_projecao.csv", index=False)
    
    # Gerar a tabela LaTeX diretamente
    latex_table = df_res.to_latex(index=False, caption="Comparativo de Métricas de Projeção", label="tab:metricas_projecao")
    with open(f"{DIR_RELATORIOS}/tabela_projecoes.tex", "w") as f:
        f.write(latex_table)
        
    print("Comparativo de projeções concluído com sucesso.")

if __name__ == "__main__":
    main()
