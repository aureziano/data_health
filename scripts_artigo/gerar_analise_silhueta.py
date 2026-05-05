import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import os
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_samples, silhouette_score
import umap

# Configurações
dir_graficos = "./overleaf/fig"
os.makedirs(dir_graficos, exist_ok=True)

def plot_silhouette_analysis():
    """Gera uma análise de silhueta detalhada para K=2 e K=3."""
    print("Iniciando análise de silhueta detalhada...")
    df_X = pd.read_csv("./tratamento/dados_tratados.csv")
    df_sample = df_X.sample(n=min(3000, len(df_X)), random_state=42)
    X_scaled = StandardScaler().fit_transform(df_sample.values)
    
    range_n_clusters = [2, 3]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
    axes = [ax1, ax2]
    
    for i, n_clusters in enumerate(range_n_clusters):
        ax = axes[i]
        
        # O coeficiente de silhueta pode variar de -1 a 1
        ax.set_xlim([-0.1, 1])
        # O (n_clusters+1)*10 é para inserir espaço em branco entre os perfis
        ax.set_ylim([0, len(X_scaled) + (n_clusters + 1) * 10])

        clusterer = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = clusterer.fit_predict(X_scaled)

        silhouette_avg = silhouette_score(X_scaled, cluster_labels)
        print(f"Para n_clusters = {n_clusters}, o score médio é {silhouette_avg:.4f}")

        sample_silhouette_values = silhouette_samples(X_scaled, cluster_labels)

        y_lower = 10
        for j in range(n_clusters):
            ith_cluster_silhouette_values = sample_silhouette_values[cluster_labels == j]
            ith_cluster_silhouette_values.sort()

            size_cluster_i = ith_cluster_silhouette_values.shape[0]
            y_upper = y_lower + size_cluster_i

            color = cm.nipy_spectral(float(j) / n_clusters)
            ax.fill_betweenx(np.arange(y_lower, y_upper),
                              0, ith_cluster_silhouette_values,
                              facecolor=color, edgecolor=color, alpha=0.7)

            ax.text(-0.05, y_lower + 0.5 * size_cluster_i, str(j))
            y_lower = y_upper + 10  # 10 for the 0 samples

        ax.set_title(f"Análise de Silhueta para K={n_clusters}\nScore Médio: {silhouette_avg:.2f}", fontsize=12)
        ax.set_xlabel("Coeficiente de Silhueta")
        ax.set_ylabel("Label do Cluster")

        # A linha vertical para o score médio de silhueta de todos os valores
        ax.axvline(x=silhouette_avg, color="red", linestyle="--")
        ax.set_yticks([])  # Limpar os yticks
        ax.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])

    plt.suptitle("Validação do Número de Clusters: Perfil de Silhueta", fontsize=16, fontweight='bold')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(f"{dir_graficos}/analise_silhueta_k2_k3.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Gráfico de análise de silhueta gerado.")

if __name__ == "__main__":
    plot_silhouette_analysis()
