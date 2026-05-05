import pandas as pd
import numpy as np
import umap
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
import os
import config

# Configurações
dir_graficos = "./overleaf/fig"
dir_relatorios = "./overleaf/tabs"
os.makedirs(dir_graficos, exist_ok=True)
os.makedirs(dir_relatorios, exist_ok=True)

def extrair_idade(valor):
    """Lógica de extração de idade conforme padrão SINAN."""
    try:
        valor_str = str(int(float(valor))).zfill(4)
        unidade = int(valor_str[0])
        quantidade = int(valor_str[1:])
        if unidade == 4: return quantidade
        return 0
    except: return 0

def main():
    print("Carregando dados para cruzamento de perfis de cluster (Dados Corrigidos)...")
    df_bruto = pd.read_csv(str(config.PATHS['hanceniase']), low_memory=False)
    
    # Seleção de variáveis para perfil expandido
    cols_perfil = ['NU_IDADE_N', 'CLASSOPERA', 'AVALIA_N', 'DOSE_RECEB', 'NERVOSAFET', 'NU_ANO']
    df = df_bruto[cols_perfil].copy()
    
    # Tratamento
    df['Idade_Real'] = df['NU_IDADE_N'].apply(extrair_idade)
    df['CLASSOP_BIN'] = df['CLASSOPERA'].map({'1': 0, '2': 1, 1: 0, 2: 1}).fillna(0)
    
    for col in ['AVALIA_N', 'DOSE_RECEB', 'NERVOSAFET', 'NU_ANO']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna()

    # Amostragem para consistência
    df_sample = df.sample(n=min(5000, len(df)), random_state=42)

    # 1. Reproduzir a melhor clusterização (K=2)
    print("Gerando clusters (UMAP + K-Means)...")
    from sklearn.preprocessing import StandardScaler
    X_model = df_sample[['Idade_Real', 'AVALIA_N', 'DOSE_RECEB', 'NERVOSAFET', 'CLASSOP_BIN']]
    X_scaled = StandardScaler().fit_transform(X_model.values)
    
    reducer = umap.UMAP(n_neighbors=30, min_dist=0.1, n_components=2, random_state=42)
    embedding = reducer.fit_transform(X_scaled)
    
    kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
    df_sample['Cluster'] = kmeans.fit_predict(X_scaled)
    
    # 2. Análise Comparativa (Perfis Reais)
    perfis = df_sample.groupby('Cluster').agg({
        'CLASSOP_BIN': 'mean',
        'AVALIA_N': 'mean',
        'DOSE_RECEB': 'mean',
        'NERVOSAFET': 'mean',
        'Idade_Real': 'mean',
        'NU_ANO': 'mean'
    }).reset_index()
    
    # Renomear para clareza
    perfis.columns = ['Cluster', 'Freq_Multibacilar', 'Freq_Incapacidade', 'Doses_Medias', 'Nervos_Afetados', 'Idade_Media', 'Ano_Medio']
    
    print("\nPerfis Identificados (Corrigidos):")
    print(perfis)
    
    # 3. Gráfico de Barras Comparativo
    plt.figure(figsize=(12, 6))
    perfis_norm = perfis.copy()
    for col in perfis.columns[1:]:
        perfis_norm[col] = (perfis[col] - perfis[col].min()) / (perfis[col].max() - perfis[col].min() + 1e-6)
    
    perfis_melted = perfis_norm.melt(id_vars='Cluster', var_name='Indicador', value_name='Valor_Normalizado')
    sns.barplot(data=perfis_melted, x='Indicador', y='Valor_Normalizado', hue='Cluster', palette='viridis')
    plt.title("Comparativo de Perfis Epidemiológicos (Dados Corrigidos)")
    plt.xticks(rotation=45)
    plt.savefig(f"{dir_graficos}/heatmap_perfil_clusters.png", bbox_inches='tight')
    plt.close()
    
    # 4. Tabela LaTeX
    with open(f"{dir_relatorios}/perfil_comparativo_clusters.tex", "w", encoding="utf-8") as f:
        f.write(perfis.to_latex(index=False, caption="Caracterização Clínica e Social dos Clusters Identificados (Dados Corrigidos)", label="tab:perfil_clusters", float_format="%.2f"))
    
    print(f"Análise de perfil concluída. Resultados salvos em {dir_relatorios}/perfil_comparativo_clusters.tex")

if __name__ == "__main__":
    main()
