import pandas as pd
import numpy as np
import umap
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score
import matplotlib.pyplot as plt
import os

# Configurações
dir_graficos = "./scripts_artigo/graficos/clustering_otimizado"
dir_relatorios = "./scripts_artigo/relatorios"
os.makedirs(dir_graficos, exist_ok=True)
os.makedirs(dir_relatorios, exist_ok=True)

print("Carregando dados para clusterização otimizada...")
df_X = pd.read_csv("./tratamento/dados_tratados.csv")

# Amostragem para acelerar UMAP e busca de parâmetros
if len(df_X) > 10000:
    print("Amostrando 10.000 registros para otimização acelerada...")
    df_X = df_X.sample(n=10000, random_state=42)

# 1. Parametrização e Busca de Parâmetros
# Vamos testar diferentes n_neighbors para UMAP e n_clusters para K-Means
neighbors_list = [15, 30]
clusters_list = [2, 3, 4, 5]

resultados = []

print("Iniciando busca de parâmetros (UMAP + K-Means)...")

for n_neigh in neighbors_list:
    # Projeção UMAP
    reducer = umap.UMAP(n_neighbors=n_neigh, min_dist=0.1, n_components=2, random_state=42)
    embedding = reducer.fit_transform(df_X)
    
    for k in clusters_list:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(embedding)
        
        # Métricas
        sil = silhouette_score(embedding, labels)
        db = davies_bouldin_score(embedding, labels)
        
        resultados.append({
            "n_neighbors": n_neigh,
            "n_clusters": k,
            "Silhouette": sil,
            "Davies_Bouldin": db
        })
        print(f"Vizinhos: {n_neigh}, Clusters: {k} -> Silhouette: {sil:.4f}")

df_res = pd.DataFrame(resultados)

# 2. Identificação da Melhor Configuração (Maior Silhouette)
melhor = df_res.loc[df_res['Silhouette'].idxmax()]
print("\nMelhor Configuração Encontrada:")
print(melhor)

# 3. Gráfico de Otimização (Silhouette vs Clusters para diferentes Vizinhos)
plt.figure(figsize=(10, 6))
for n_neigh in neighbors_list:
    sub = df_res[df_res['n_neighbors'] == n_neigh]
    plt.plot(sub['n_clusters'], sub['Silhouette'], marker='o', label=f'Vizinhos={n_neigh}')

plt.title("Otimização de Clusters (Análise de Silhouette)")
plt.xlabel("Número de Clusters (K)")
plt.ylabel("Silhouette Score")
plt.legend()
plt.grid(True)
plt.savefig(f"{dir_graficos}/otimizacao_silhouette.png", bbox_inches='tight')
plt.close()

# 4. Relatório LaTeX
with open(f"{dir_relatorios}/otimizacao_clustering.tex", "w", encoding="utf-8") as f:
    f.write("% Tabela de Resultados da Otimização de Clustering\n")
    f.write(df_res.sort_values("Silhouette", ascending=False).to_latex(index=False, caption="Resultados da Otimização de Hiperparâmetros (UMAP + K-Means)", label="tab:otimizacao_clustering"))

print(f"Otimização concluída. Resultados salvos em {dir_relatorios}/otimizacao_clustering.tex")
