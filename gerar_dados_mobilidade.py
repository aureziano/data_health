import pandas as pd
import geopandas as gpd
import networkx as nx
from pathlib import Path
import matplotlib.pyplot as plt
import warnings
from unidecode import unidecode
import re

warnings.simplefilter(action='ignore', category=FutureWarning)

# =============================================================================
# FASE 0: CONFIGURAÇÃO DOS CAMINHOS DOS ARQUIVOS
# =============================================================================
print("--- FASE 0: CONFIGURANDO CAMINHOS ---")
base_path = Path('.')
paths = {
    'populacao': base_path / 'data' / 'IBGE' / 'populacao_municipios.csv',
    'hanceniase': base_path / 'data' / 'HANSENIASE' / 'HANSENIASE_TOTAL_28_02_2025.csv',
    'antt': base_path / 'data' / 'MOBILIDADE' / 'dados_rodoviarios_ibge.csv',
    'ibge_2016': base_path / 'data' / 'MOBILIDADE' / 'dados_rodoviarias_hidroviarias_2016.csv',
    'anac': base_path / 'data' / 'MOBILIDADE' / 'dados_aereos_consolidados.csv',
    'malha': base_path / 'data' / 'MOBILIDADE' / 'BR_Municipios_2024.shp'
}
for name, path in paths.items():
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}.")
print("Todos os arquivos foram encontrados com sucesso.")

# =============================================================================
# FASE 1: CARREGAMENTO E ANÁLISE TEMPORAL
# =============================================================================
print("\n--- FASE 1: CARREGAMENTO E ANÁLISE TEMPORAL ---")
dfs = {}
print("Carregando datasets...")
# CORREÇÃO: Carregar e já converter todos os IDs para 6 dígitos
dfs['populacao'] = pd.read_csv(paths['populacao'])
dfs['populacao']['id_municipio'] = dfs['populacao']['id_municipio'] // 10

dfs['hanceniase'] = pd.read_csv(paths['hanceniase'], usecols=['ID_MN_RESI', 'DT_NOTIFIC'], parse_dates=['DT_NOTIFIC'], low_memory=False)
# ID da hanseníase já é 6 dígitos, apenas garantimos o tipo
dfs['hanceniase'].rename(columns={'ID_MN_RESI': 'id_municipio'}, inplace=True)
dfs['hanceniase'].dropna(subset=['id_municipio'], inplace=True)
dfs['hanceniase']['id_municipio'] = dfs['hanceniase']['id_municipio'].astype(int)

dfs['antt'] = pd.read_csv(paths['antt'])
dfs['antt']['id_municipio_origem'] = dfs['antt']['id_municipio_origem'] // 10
dfs['antt']['id_municipio_destino'] = dfs['antt']['id_municipio_destino'] // 10

dfs['anac'] = pd.read_csv(paths['anac'], usecols=['nr_ano_partida_real', 'nm_municipio_origem', 'sg_uf_origem', 'nm_municipio_destino', 'sg_uf_destino', 'nr_passag_pagos'])
dfs['ibge_2016'] = pd.read_csv(paths['ibge_2016'], sep=';', encoding='latin-1')

dfs['hanceniase']['ano'] = dfs['hanceniase']['DT_NOTIFIC'].dt.year
dfs['anac']['ano'] = dfs['anac']['nr_ano_partida_real']

ranges = {}
time_series_datasets = ['populacao', 'hanceniase', 'antt', 'anac']
for name in time_series_datasets:
    # Ignorar anos inválidos que possam ter sido lidos
    anos_validos = dfs[name]['ano'].dropna().astype(int)
    if not anos_validos.empty:
        ranges[name] = (anos_validos.min(), anos_validos.max())

print("\nFaixa temporal dos datasets de série temporal:")
for name, (min_yr, max_yr) in ranges.items():
    print(f"- {name.capitalize()}: {int(min_yr)} - {int(max_yr)}")

ano_minimo_comum = max(r[0] for r in ranges.values())
ano_maximo_comum = min(r[1] for r in ranges.values())

if ano_minimo_comum > ano_maximo_comum:
    raise ValueError(f"Não há sobreposição temporal nos seus dados. Mínimo comum: {ano_minimo_comum}, Máximo comum: {ano_maximo_comum}")
print(f"\nFAIXA TEMPORAL COMUM VÁLIDA: {int(ano_minimo_comum)} a {int(ano_maximo_comum)}")

# AJUSTE 1: FORÇANDO O ANO DA ANÁLISE PARA 2022
# -----------------------------------------------------------------------------
ano_analise = 2022
print(f"\nAJUSTE MANUAL: Focando a análise da rede no ano de {ano_analise}.")
# Garantir que o ano de análise está dentro do intervalo válido
if not (ano_minimo_comum <= ano_analise <= ano_maximo_comum):
    print(f"AVISO: O ano de análise {ano_analise} está fora da faixa temporal comum. Os resultados podem ser vazios.")
# -----------------------------------------------------------------------------


# =============================================================================
# FASE 2: PRÉ-PROCESSAMENTO E UNIFICAÇÃO
# =============================================================================
print("\n--- FASE 2: PRÉ-PROCESSAMENTO E UNIFICAÇÃO DOS DADOS ---")

def criar_mapa_ibge(df_pop):
    df_mapa = df_pop.sort_values('ano').drop_duplicates('id_municipio', keep='last')
    return {f"{unidecode(str(row['nome_municipio'])).upper().strip()}_{row['sigla_uf'].upper()}": row['id_municipio'] for _, row in df_mapa.iterrows()}

mapa_ibge = criar_mapa_ibge(dfs['populacao'])
print(f"Mapa de tradução Nome->Código IBGE criado com {len(mapa_ibge)} entradas.")

for name, df in dfs.items():
    if name != 'ibge_2016' and 'ano' in df.columns:
        dfs[name] = df[(df['ano'] >= ano_minimo_comum) & (df['ano'] <= ano_maximo_comum)].copy()
print(f"Datasets filtrados para o período de {int(ano_minimo_comum)} a {int(ano_maximo_comum)}.")

print("Processando e unificando as fontes de mobilidade...")
antt_fluxo = dfs['antt'].rename(columns={'id_municipio_origem': 'origem', 'id_municipio_destino': 'destino', 'fluxo_passageiros': 'fluxo'})
antt_fluxo = antt_fluxo.groupby(['ano', 'origem', 'destino'])['fluxo'].sum().reset_index()
antt_fluxo['modal'] = 'rodoviario_antt'

df_anac = dfs['anac']
def criar_chave_anac(row, tipo):
    try:
        nome = unidecode(str(row[f'nm_municipio_{tipo}'])).upper().strip()
        uf = str(row[f'sg_uf_{tipo}']).upper().strip()
        return f"{nome}_{uf}"
    except: return None
df_anac['chave_origem'] = df_anac.apply(criar_chave_anac, axis=1, tipo='origem')
df_anac['chave_destino'] = df_anac.apply(criar_chave_anac, axis=1, tipo='destino')
df_anac['origem'] = df_anac['chave_origem'].map(mapa_ibge)
df_anac['destino'] = df_anac['chave_destino'].map(mapa_ibge)
anac_fluxo = df_anac.rename(columns={'nr_passag_pagos': 'fluxo'})
anac_fluxo = anac_fluxo.groupby(['ano', 'origem', 'destino'])['fluxo'].sum().reset_index()
anac_fluxo['modal'] = 'aereo'

fluxos = [antt_fluxo, anac_fluxo]

if 2016 >= ano_minimo_comum and 2016 <= ano_maximo_comum:
    print("O ano de 2016 está no intervalo, adicionando dados estruturais do IBGE.")
    colunas_ibge = ['Cod_Mun_Origem', 'Cod_Mun_Destino']
    if all(col in dfs['ibge_2016'].columns for col in colunas_ibge):
        ibge_fluxo = dfs['ibge_2016'][colunas_ibge].copy()
        ibge_fluxo.rename(columns={'Cod_Mun_Origem': 'origem', 'Cod_Mun_Destino': 'destino'}, inplace=True)
        ibge_fluxo['origem'] = ibge_fluxo['origem'] // 10
        ibge_fluxo['destino'] = ibge_fluxo['destino'] // 10
        ibge_fluxo['ano'], ibge_fluxo['fluxo'], ibge_fluxo['modal'] = 2016, 1, 'rodoviario_hidro_ibge'
        ibge_fluxo = ibge_fluxo.drop_duplicates()
        fluxos.append(ibge_fluxo)
    else:
        print(f"AVISO: As colunas esperadas {colunas_ibge} não foram encontradas no arquivo ibge_2016. Pulando esta fonte de dados.")
else:
    print("O ano de 2016 está fora do intervalo, os dados estruturais do IBGE não serão adicionados.")

fluxo_total = pd.concat(fluxos, ignore_index=True)
fluxo_total.dropna(subset=['origem', 'destino'], inplace=True)
fluxo_total[['origem', 'destino']] = fluxo_total[['origem', 'destino']].astype(int)
fluxo_agregado = fluxo_total.groupby(['ano', 'origem', 'destino'])['fluxo'].sum().reset_index()
print(f"Fontes de mobilidade unificadas. Total de {len(fluxo_agregado)} conexões anuais (arestas).")

print("Processando dados dos municípios (população e hanseníase)...")
casos_hanceniase = dfs['hanceniase'].rename(columns={'ID_MN_RESI': 'id_municipio'})
casos_hanceniase = casos_hanceniase.groupby(['ano', 'id_municipio']).size().reset_index(name='casos_hanseniase')
populacao = dfs['populacao'][['ano', 'id_municipio', 'nome_municipio', 'sigla_uf', 'pessoas']].rename(columns={'pessoas': 'populacao'})
atributos_nos = pd.merge(populacao, casos_hanceniase, on=['ano', 'id_municipio'], how='left')
atributos_nos['casos_hanseniase'].fillna(0, inplace=True)
atributos_nos['casos_hanseniase'] = atributos_nos['casos_hanseniase'].astype(int)

# =============================================================================
# FASE 3: CONSTRUÇÃO DA REDE COM NETWORKX
# =============================================================================
print("\n--- FASE 3: CONSTRUINDO A REDE COM NETWORKX ---")
G = nx.MultiDiGraph()
print("Adicionando municípios (nós) ao grafo...")
# Usar 'ano_analise' para selecionar os nós
nos_unicos = atributos_nos[atributos_nos['ano'] == ano_analise]
for _, row in nos_unicos.iterrows():
    G.add_node(row['id_municipio'], nome=row['nome_municipio'], uf=row['sigla_uf'])

for _, row in atributos_nos.iterrows():
    if G.has_node(row['id_municipio']):
        G.nodes[row['id_municipio']][f'pop_{row["ano"]}'] = row['populacao']
        G.nodes[row['id_municipio']][f'casos_{row["ano"]}'] = row['casos_hanseniase']
print(f"Grafo criado com {G.number_of_nodes()} nós.")

print("Adicionando conexões de mobilidade (arestas) ao grafo...")
for _, row in fluxo_agregado.iterrows():
    if G.has_node(row['origem']) and G.has_node(row['destino']):
        G.add_edge(row['origem'], row['destino'], key=row['ano'], weight=row['fluxo'])
print(f"Grafo finalizado com {G.number_of_edges()} arestas anuais.")

# =============================================================================
# FASE 4: ANÁLISE DA REDE E IDENTIFICAÇÃO DE CIDADES SENTINELA
# =============================================================================
print("\n--- FASE 4: ANÁLISE DA REDE ---")
# Usar 'ano_analise' para a análise de centralidade
print(f"Analisando a rede para o ano de {int(ano_analise)}...")
G_ano = nx.DiGraph()

for u, v, key, data in G.edges(data=True, keys=True):
    if key == ano_analise:
        G_ano.add_edge(u, v, weight=data['weight'])

print("Calculando métricas de centralidade para identificar cidades sentinela...")
grau = dict(G_ano.degree(weight='weight'))
print("Calculando centralidade de intermediação (pode levar vários minutos)...")
intermediacao = nx.betweenness_centrality(G_ano, weight='weight', normalized=True)
print("Cálculo finalizado.")

cidades_sentinela = pd.DataFrame(index=G_ano.nodes())
cidades_sentinela['centralidade_grau'] = pd.Series(grau)
cidades_sentinela['centralidade_intermediacao'] = pd.Series(intermediacao)
cidades_sentinela['nome_municipio'] = pd.Series(nx.get_node_attributes(G, 'nome'))
cidades_sentinela['uf'] = pd.Series(nx.get_node_attributes(G, 'uf'))

cidades_sentinela['grau_normalizado'] = (cidades_sentinela['centralidade_grau'] - cidades_sentinela['centralidade_grau'].min()) / (cidades_sentinela['centralidade_grau'].max() - cidades_sentinela['centralidade_grau'].min())
cidades_sentinela['intermediacao_normalizada'] = (cidades_sentinela['centralidade_intermediacao'] - cidades_sentinela['centralidade_intermediacao'].min()) / (cidades_sentinela['centralidade_intermediacao'].max() - cidades_sentinela['centralidade_intermediacao'].min())
cidades_sentinela['score_sentinela'] = cidades_sentinela['grau_normalizado'] + cidades_sentinela['intermediacao_normalizada']
cidades_sentinela.sort_values('score_sentinela', ascending=False, inplace=True)

print(f"\n--- TOP 20 CIDADES SENTINELA (ANO {int(ano_analise)}) ---")
print(cidades_sentinela[['nome_municipio', 'uf', 'score_sentinela', 'centralidade_grau', 'centralidade_intermediacao']].head(20))

# AJUSTE 2: SALVAR O ARQUIVO EM UMA PASTA 'results' COM NOME DINÂMICO
# -----------------------------------------------------------------------------
# Criar a pasta 'results' se ela não existir
output_dir = Path('results')
output_dir.mkdir(exist_ok=True)

# Criar o nome do arquivo dinamicamente com o ano da análise
output_filename = output_dir / f"resultado_cidades_sentinela_{int(ano_analise)}.csv"

cidades_sentinela.to_csv(output_filename)
print(f"\nResultado completo salvo em '{output_filename}'")
# -----------------------------------------------------------------------------

print("\nNota sobre o algoritmo de Fluxo Máximo (Ford-Fulkerson):")
print("Para identificar as cidades mais importantes na rede como um todo, as métricas de centralidade (grau, intermediação, etc.) são as ferramentas mais indicadas e foram as utilizadas nesta análise.")