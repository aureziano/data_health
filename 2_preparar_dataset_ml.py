# 2_preparar_dataset_ml.py (VERSÃO COM FEATURES DE SÉRIE TEMPORAL)
import pandas as pd
import networkx as nx
from tqdm import tqdm
import pickle
import config

def run():
    print("--- INICIANDO SCRIPT 2: PREPARAÇÃO DO DATASET ENRIQUECIDO PARA ML ---")
    
    # Carregar dados processados e de origem
    print("Carregando dados de centralidade, população e série histórica de hanseníase...")
    df_centrality = pd.read_csv(config.OUTPUT_PATHS['centrality_yearly'])
    
    df_pop = pd.read_csv(config.PATHS['populacao'])
    df_pop['id_municipio'] = df_pop['id_municipio'] // 10
    df_pop.rename(columns={'pessoas': 'populacao'}, inplace=True)
    
    # Carregar a série histórica COMPLETA de hanseníase
    df_hans_full = pd.read_csv(config.PATHS['hanceniase'], usecols=['ID_MN_RESI', 'DT_NOTIFIC'], low_memory=False)
    df_hans_full['DT_NOTIFIC'] = pd.to_datetime(df_hans_full['DT_NOTIFIC'], errors='coerce')
    df_hans_full['ano'] = df_hans_full['DT_NOTIFIC'].dt.year
    df_hans_full.rename(columns={'ID_MN_RESI': 'id_municipio'}, inplace=True)
    df_hans_full.dropna(subset=['id_municipio', 'ano'], inplace=True)
    df_hans_full['id_municipio'] = df_hans_full['id_municipio'].astype(int)
    casos_por_ano = df_hans_full.groupby(['ano', 'id_municipio']).size().reset_index(name='casos_hanseniase')

    # --- NOVO: Criação de Features de Série Temporal ---
    print("Criando features de média móvel e tendência a partir do histórico de casos...")
    casos_por_ano = casos_por_ano.sort_values(['id_municipio', 'ano'])
    
    # Criar a média móvel de casos dos 3 anos anteriores
    # .shift(1) garante que estamos olhando apenas para o passado
    casos_por_ano['media_movel_3a'] = casos_por_ano.groupby('id_municipio')['casos_hanseniase'].shift(1).rolling(3, min_periods=1).mean()
    
    # Criar a tendência de casos nos 2 anos anteriores
    casos_por_ano['tendencia_2a'] = casos_por_ano.groupby('id_municipio')['casos_hanseniase'].shift(1).rolling(2, min_periods=1).apply(lambda x: x.iloc[-1] - x.iloc[0] if len(x) > 1 else 0.0, raw=False)
    
    casos_por_ano.fillna(0, inplace=True)
    # --- Fim da nova seção ---

    # Juntar centralidade, população e agora os casos ENRIQUECIDOS
    # Usamos 'inner' join para manter apenas os anos e municípios onde temos TODOS os dados (mobilidade, pop, etc)
    master_df = pd.merge(df_centrality, df_pop, on=['ano', 'id_municipio'], how='inner')
    master_df = pd.merge(master_df, casos_por_ano, on=['ano', 'id_municipio'], how='left')
    
    # Preencher NaNs restantes após o merge
    fill_cols = ['casos_hanseniase', 'media_movel_3a', 'tendencia_2a']
    for col in fill_cols:
        master_df[col] = master_df[col].fillna(0)

    # Criar feature de "casos no ano anterior" (lag)
    master_df = master_df.sort_values(by=['id_municipio', 'ano'])
    master_df['casos_ano_anterior'] = master_df.groupby('id_municipio')['casos_hanseniase'].shift(1)
    
    # Calcular "Risco Importado"
    print("Calculando feature de 'Risco Importado' (pode levar tempo)...")
    with open(config.OUTPUT_PATHS['full_graph'], 'rb') as f:
        G = pickle.load(f)
        
    master_df['risco_importado'] = 0.0

    for year in tqdm(range(config.ANO_INICIAL_ANALISE + 1, config.ANO_FINAL_ANALISE + 1), desc="Calculando Risco Importado"):
        ano_anterior = year - 1
        G_anterior = nx.DiGraph()
        for u, v, key, data in G.edges(data=True, keys=True):
            if key == ano_anterior:
                G_anterior.add_edge(u, v, weight=data.get('weight', 1))

        casos_map = master_df[master_df['ano'] == ano_anterior].set_index('id_municipio')['casos_hanseniase'].to_dict()
        
        risco_ano = {}
        for municipio in G_anterior.nodes():
            risco = 0
            for vizinho, _ in G_anterior.in_edges(municipio):
                fluxo = G_anterior.get_edge_data(vizinho, municipio).get('weight', 0)
                casos_vizinho = casos_map.get(vizinho, 0)
                risco += fluxo * casos_vizinho
            risco_ano[municipio] = risco
            
        master_df.loc[master_df['ano'] == year, 'risco_importado'] = master_df['id_municipio'].map(risco_ano).fillna(0)

    # Limpar NaNs gerados pelo lag (remove o primeiro ano da série) e salvar
    master_df.dropna(subset=['casos_ano_anterior'], inplace=True)
    master_df.to_csv(config.OUTPUT_PATHS['ml_dataset'], index=False)
    print(f"Dataset final para Machine Learning salvo em: {config.OUTPUT_PATHS['ml_dataset']}")
    print("--- SCRIPT 2 CONCLUÍDO ---")

if __name__ == '__main__':
    run()