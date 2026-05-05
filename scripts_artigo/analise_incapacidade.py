import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import umap
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from scipy.stats import kruskal
import os
import config

# Configurações de diretórios
DIR_GRAFICOS = "./overleaf/fig"
DIR_RELATORIOS = "./overleaf/tabs"
os.makedirs(DIR_GRAFICOS, exist_ok=True)
os.makedirs(DIR_RELATORIOS, exist_ok=True)

def extrair_idade(valor):
    """Lógica de extração de idade conforme padrão SINAN (prefixo 4 = anos)."""
    try:
        valor_str = str(int(float(valor))).zfill(4)
        unidade = int(valor_str[0])
        quantidade = int(valor_str[1:])
        if unidade == 4: return quantidade
        return 0
    except: return 0

def main():
    print("Iniciando Análise de Incapacidade e Clusterização (Dados Corrigidos)...")
    
    # 1. Carregamento dos dados
    # Tenta carregar o arquivo mais recente
    path_data = str(config.PATHS['hanceniase'])
    if not os.path.exists(path_data):
        print(f"Erro: Arquivo {path_data} não encontrado.")
        return

    df_bruto = pd.read_csv(path_data, low_memory=False)
    
    # 2. Definição do Escopo e Tratamento
    features_raw = ['NU_IDADE_N', 'AVALIA_N', 'NU_LESOES', 'NERVOSAFET', 'CLASSOPERA', 'CS_SEXO']
    df_cluster = df_bruto[features_raw].copy()
    
    # Conversão de Tipos
    for col in ['NU_IDADE_N', 'AVALIA_N', 'NU_LESOES', 'NERVOSAFET']:
        df_cluster[col] = pd.to_numeric(df_cluster[col], errors='coerce')
    
    # Extração de Idade Real
    df_cluster['Idade_Real'] = df_cluster['NU_IDADE_N'].apply(extrair_idade)
    
    # Codificação para Modelagem (Escalonável)
    # Sexo: 0=F, 1=M, Outros -> NaN -> 0
    df_cluster['CS_SEXO_BIN'] = df_cluster['CS_SEXO'].map({'M': 1, 'F': 0, 1: 1, 0: 0, '1': 1, '0': 0}).fillna(0)
    # Classificação Operacional: 0=PB, 1=MB
    df_cluster['CLASSOP_BIN'] = df_cluster['CLASSOPERA'].map({'1': 0, '2': 1, 1: 0, 2: 1}).fillna(0)
    
    # Limpeza final de NaNs para o modelo
    features_model = ['Idade_Real', 'AVALIA_N', 'NU_LESOES', 'NERVOSAFET', 'CLASSOP_BIN', 'CS_SEXO_BIN']
    df_cluster = df_cluster.dropna(subset=features_model)
    
    # Amostragem
    if len(df_cluster) > 20000:
        df_cluster = df_cluster.sample(20000, random_state=42)

    X = df_cluster[features_model].values
    X_scaled = StandardScaler().fit_transform(X)

    # 3. UMAP e K-Means
    print("Reduzindo dimensionalidade via UMAP...")
    reducer = umap.UMAP(n_neighbors=30, min_dist=0.1, n_components=2, random_state=42)
    embedding = reducer.fit_transform(X_scaled)

    print("Calculando clusters via K-Means...")
    kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
    df_cluster['cluster'] = kmeans.fit_predict(X_scaled)

    # 4. Importância de Variáveis para os Clusters
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X, df_cluster['cluster'])
    importancia = pd.DataFrame({'Feature': features_model, 'Importance': rf.feature_importances_}).sort_values('Importance', ascending=False)

    plt.figure(figsize=(10, 6))
    sns.barplot(x='Importance', y='Feature', data=importancia, palette='magma')
    plt.title("Importância das Variáveis na Definição dos Clusters (Dados Corrigidos)")
    plt.savefig(f"{DIR_GRAFICOS}/importancia_features_clusters.png", dpi=300, bbox_inches='tight')
    plt.close()

    # 5. Justificativa Estatística (Kruskal-Wallis)
    results_stats = []
    for col in ['AVALIA_N', 'NERVOSAFET', 'NU_LESOES']:
        groups = [df_cluster[df_cluster['cluster'] == i][col] for i in range(2)]
        stat, p = kruskal(*groups)
        results_stats.append({'Variável': col, 'H-stat': stat, 'p-value': p})
    
    df_stats = pd.DataFrame(results_stats)
    df_stats.to_latex(f"{DIR_RELATORIOS}/validacao_estatistica_clusters.tex", index=False)

    # 6. Perfil dos Clusters (Consolidado com dados ORIGINAIS interpretáveis)
    # Vamos renomear para ficar claro na tabela LaTeX
    perfil_cols = {
        'Idade_Real': 'Idade (Anos)',
        'AVALIA_N': 'Grau Incap. (0-2)',
        'NU_LESOES': 'Nº Lesões',
        'NERVOSAFET': 'Nervos Afetados',
        'CLASSOP_BIN': 'Proporção MB',
        'CS_SEXO_BIN': 'Proporção Masc.'
    }
    perfil = df_cluster.groupby('cluster')[list(perfil_cols.keys())].mean()
    perfil = perfil.rename(columns=perfil_cols)
    
    print("\nPerfil Médio dos Clusters:")
    print(perfil)
    
    perfil.to_latex(f"{DIR_RELATORIOS}/perfil_clusters_incapacidade.tex", float_format="%.2f")

    # 7. Gráfico de Justificativa (REFORMULADO: Stacked Bar Plot para clareza total)
    print("Gerando gráfico de barras empilhadas para composição de GIF por cluster...")
    df_pivot = df_cluster.groupby(['cluster', 'AVALIA_N']).size().unstack(fill_value=0)
    df_pct = df_pivot.div(df_pivot.sum(axis=1), axis=0) * 100
    
    # Renomear labels para o gráfico
    df_pct.columns = [f'Grau {int(c)}' for c in df_pct.columns]
    
    ax = df_pct.plot(kind='bar', stacked=True, figsize=(10, 6), color=['#2ecc71', '#f1c40f', '#e74c3c'], alpha=0.85)
    plt.title("Composição do Grau de Incapacidade por Cluster", fontsize=14, fontweight='bold')
    plt.xlabel("Cluster", fontsize=12)
    plt.ylabel("Porcentagem (%)", fontsize=12)
    plt.xticks(rotation=0)
    plt.legend(title="Avaliação (GIF)", bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Adicionar anotações de porcentagem
    for p in ax.patches:
        width, height = p.get_width(), p.get_height()
        if height > 5: # Só mostrar se for maior que 5% para evitar poluição
            x, y = p.get_xy() 
            ax.text(x+width/2, y+height/2, f'{height:.1f}%', ha='center', va='center', fontweight='bold', color='white')

    plt.tight_layout()
    plt.savefig(f"{DIR_GRAFICOS}/justificativa_alta_gravidade.png", dpi=300, bbox_inches='tight')
    plt.close()

    print("Análise de incapacidade (corrigida e simplificada) concluída com sucesso.")

if __name__ == "__main__":
    main()
