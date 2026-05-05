import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import seaborn as sns
import umap
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Configurações
dir_graficos = "./overleaf/fig"
os.makedirs(dir_graficos, exist_ok=True)

def plot_walk_forward_illustration():
    """Gera uma ilustração gráfica de como funciona a Janela Deslizante (Walk-forward)."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    n_splits = 5
    width = 0.8
    
    for i in range(n_splits):
        # Treino
        ax.barh(i, 5 + i * 2, left=0, color='skyblue', edgecolor='black', label='Treino' if i == 0 else "")
        # Teste (Ponto seguinte)
        ax.barh(i, 2, left=5 + i * 2, color='orange', edgecolor='black', label='Teste' if i == 0 else "")
        
        ax.text(-1, i, f"Iteração {i+1}", va='center', ha='right', fontsize=10)

    ax.set_yticks([])
    ax.set_xlabel("Tempo (Meses/Anos)", fontsize=12)
    ax.set_title("Esquema de Validação Walk-forward (Sliding Window)", fontsize=14)
    ax.legend(loc='upper right')
    ax.grid(axis='x', linestyle='--', alpha=0.6)
    
    plt.savefig(f"{dir_graficos}/ilustracao_walkforward.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Ilustração Walk-forward gerada.")

def compare_clusters_k2_k3():
    """Gera comparativo visual de UMAP para K=2 e K=3."""
    print("Iniciando comparativo de clusters K=2 vs K=3...")
    df_X = pd.read_csv("./tratamento/dados_tratados.csv")
    if len(df_X) > 5000:
        df_sample = df_X.sample(n=5000, random_state=42)
    else:
        df_sample = df_X

    X_scaled = StandardScaler().fit_transform(df_sample.values)
    
    reducer = umap.UMAP(n_neighbors=30, min_dist=0.1, n_components=2, random_state=42)
    embedding = reducer.fit_transform(X_scaled)
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    # K=2
    kmeans2 = KMeans(n_clusters=2, random_state=42, n_init=10)
    labels2 = kmeans2.fit_predict(X_scaled)
    axes[0].scatter(embedding[:, 0], embedding[:, 1], c=labels2, cmap='viridis', s=5, alpha=0.6)
    axes[0].set_title("Configuração Ótima (K=2)\nMaior Coesão Estatística (Silhouette: 0.69)", fontsize=12)
    
    # K=3
    kmeans3 = KMeans(n_clusters=3, random_state=42, n_init=10)
    labels3 = kmeans3.fit_predict(X_scaled)
    axes[1].scatter(embedding[:, 0], embedding[:, 1], c=labels3, cmap='plasma', s=5, alpha=0.6)
    axes[1].set_title("Configuração Detalhada (K=3)\nMaior Granularidade de Perfis (Silhouette: 0.58)", fontsize=12)
    
    for ax in axes:
        ax.set_xticks([])
        ax.set_yticks([])
        
    plt.suptitle("Comparativo de Clusterização UMAP + K-Means", fontsize=16)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(f"{dir_graficos}/comparativo_clusters_k2_k3.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Comparativo de clusters gerado.")

if __name__ == "__main__":
    plot_walk_forward_illustration()
    compare_clusters_k2_k3()
