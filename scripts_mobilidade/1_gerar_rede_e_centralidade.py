# 1_gerar_rede_e_centralidade.py
import pandas as pd
import networkx as nx
from unidecode import unidecode
import pickle # Importar a biblioteca pickle
import config

def run():
    print("--- INICIANDO SCRIPT 1: GERAÇÃO DA REDE E CÁLCULO DE CENTRALIDADE ---")
    
    # ... (Todo o código de carregamento e processamento de dados permanece o mesmo) ...
    print("Carregando e harmonizando dados de origem...")
    dfs = {}
    dfs['populacao'] = pd.read_csv(config.PATHS['populacao'])
    dfs['populacao']['id_municipio'] = dfs['populacao']['id_municipio'] // 10

    dfs['antt'] = pd.read_csv(config.PATHS['antt'])
    dfs['antt']['id_municipio_origem'] = dfs['antt']['id_municipio_origem'] // 10
    dfs['antt']['id_municipio_destino'] = dfs['antt']['id_municipio_destino'] // 10

    dfs['anac'] = pd.read_csv(config.PATHS['anac'], usecols=['nr_ano_partida_real', 'nm_municipio_origem', 'sg_uf_origem', 'nm_municipio_destino', 'sg_uf_destino', 'nr_passag_pagos'])
    dfs['anac']['ano'] = dfs['anac']['nr_ano_partida_real']
    
    for name in ['populacao', 'antt', 'anac']:
        dfs[name] = dfs[name][(dfs[name]['ano'] >= config.ANO_INICIAL_ANALISE) & (dfs[name]['ano'] <= config.ANO_FINAL_ANALISE)].copy()

    mapa_ibge = {f"{unidecode(str(row['nome_municipio'])).upper().strip()}_{row['sigla_uf'].upper()}": row['id_municipio'] for _, row in dfs['populacao'].drop_duplicates('id_municipio').iterrows()}

    antt_fluxo = dfs['antt'].rename(columns={'id_municipio_origem': 'origem', 'id_municipio_destino': 'destino', 'fluxo_passageiros': 'fluxo'})
    anac_fluxo_df = dfs['anac']
    anac_fluxo_df['chave_origem'] = anac_fluxo_df.apply(lambda row: f"{unidecode(str(row['nm_municipio_origem'])).upper().strip()}_{str(row['sg_uf_origem']).upper().strip()}", axis=1)
    anac_fluxo_df['chave_destino'] = anac_fluxo_df.apply(lambda row: f"{unidecode(str(row['nm_municipio_destino'])).upper().strip()}_{str(row['sg_uf_destino']).upper().strip()}", axis=1)
    anac_fluxo_df['origem'] = anac_fluxo_df['chave_origem'].map(mapa_ibge)
    anac_fluxo_df['destino'] = anac_fluxo_df['chave_destino'].map(mapa_ibge)
    anac_fluxo = anac_fluxo_df.rename(columns={'nr_passag_pagos': 'fluxo'})
    
    fluxo_total = pd.concat([
        antt_fluxo[['ano', 'origem', 'destino', 'fluxo']],
        anac_fluxo[['ano', 'origem', 'destino', 'fluxo']]
    ], ignore_index=True)
    
    fluxo_total.dropna(subset=['origem', 'destino'], inplace=True)
    fluxo_total[['origem', 'destino']] = fluxo_total[['origem', 'destino']].astype(int)
    fluxo_agregado = fluxo_total.groupby(['ano', 'origem', 'destino'])['fluxo'].sum().reset_index()

    print("Construindo o grafo de mobilidade...")
    G = nx.MultiDiGraph()
    nodes = set(fluxo_agregado['origem']).union(set(fluxo_agregado['destino']))
    G.add_nodes_from(nodes)

    for _, row in fluxo_agregado.iterrows():
        G.add_edge(row['origem'], row['destino'], key=row['ano'], weight=row['fluxo'])
    
    # CORREÇÃO APLICADA AQUI: Usando pickle para salvar o grafo
    print("Salvando o objeto do grafo...")
    with open(config.OUTPUT_PATHS['full_graph'], 'wb') as f:
        pickle.dump(G, f, pickle.HIGHEST_PROTOCOL)
    print(f"Grafo de mobilidade salvo em: {config.OUTPUT_PATHS['full_graph']}")

    # ... (O resto do script para calcular centralidade permanece o mesmo) ...
    print("Calculando centralidade para cada ano da série histórica...")
    yearly_centrality = []
    for year in range(config.ANO_INICIAL_ANALISE, config.ANO_FINAL_ANALISE + 1):
        G_year = nx.DiGraph()
        for u, v, key, data in G.edges(data=True, keys=True):
            if key == year:
                G_year.add_edge(u, v, weight=data.get('weight', 1))
        
        if G_year.number_of_edges() == 0: continue

        print(f"  - Processando ano {year}...")
        grau = dict(G_year.degree(weight='weight'))
        intermediacao = nx.betweenness_centrality(G_year, weight='weight', normalized=True)
        
        df_year = pd.DataFrame(index=G_year.nodes())
        df_year['ano'] = year
        df_year['centralidade_grau'] = pd.Series(grau)
        df_year['centralidade_intermediacao'] = pd.Series(intermediacao)
        yearly_centrality.append(df_year)

    df_centrality = pd.concat(yearly_centrality).reset_index().rename(columns={'index': 'id_municipio'})
    df_centrality.to_csv(config.OUTPUT_PATHS['centrality_yearly'], index=False)
    print(f"Métricas de centralidade anuais salvas em: {config.OUTPUT_PATHS['centrality_yearly']}")
    print("--- SCRIPT 1 CONCLUÍDO ---")

if __name__ == '__main__':
    run()