# 5_validacao_covid19.py
import pandas as pd
import networkx as nx
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import config

def run():
    print("--- INICIANDO SCRIPT 5: VALIDAÇÃO DA REDE COM DADOS DA COVID-19 ---")

    # --- Carregar dados necessários ---
    print("Carregando grafo de mobilidade...")
    with open(config.OUTPUT_PATHS['full_graph'], 'rb') as f:
        G_full = pickle.load(f)

    # Extrair a rede de 2020, ano do início da pandemia
    ano_pandemia = 2020
    G_2020 = nx.DiGraph()
    for u, v, key, data in G_full.edges(data=True, keys=True):
        if key == ano_pandemia:
            # Inverter o peso: fluxo alto = distância curta
            fluxo = data.get('weight', 1)
            if fluxo > 0:
                G_2020.add_edge(u, v, weight=1.0 / fluxo)

    # --- Carregar dados de COVID-19 ---
    print("Carregando dados reais de primeiros casos de COVID-19...")
    caminho_covid = config.DATA_PATH / 'MOBILIDADE' / 'covid_primeiros_casos.csv'
    df_covid = pd.read_csv(caminho_covid, parse_dates=['data_primeiro_caso'])
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # --- Análise de Disseminação a partir de São Paulo ---
    id_sao_paulo = 355030 # Código IBGE de 6 dígitos para São Paulo
    data_inicio_sp = df_covid[df_covid['id_municipio'] == id_sao_paulo]['data_primeiro_caso'].min()

    if pd.isna(data_inicio_sp):
        print("ERRO: Município de origem (São Paulo) não encontrado nos dados de COVID-19.")
        return

    print(f"Calculando a 'distância de rede' de São Paulo (ID: {id_sao_paulo}) para outros municípios...")
    
    # Calcular o caminho mais curto (menor peso invertido = maior fluxo)
    # a partir de São Paulo para todos os outros nós alcançáveis
    distancias_rede = nx.shortest_path_length(G_2020, source=id_sao_paulo, weight='weight')
    
    df_dist_rede = pd.DataFrame(distancias_rede.items(), columns=['id_municipio', 'distancia_rede'])
    
    # Calcular a "distância temporal" em dias
    df_covid['distancia_dias'] = (df_covid['data_primeiro_caso'] - data_inicio_sp).dt.days
    
    # Juntar os dois tipos de distância
    df_validacao = pd.merge(df_dist_rede, df_covid, on='id_municipio')
    # Manter apenas os casos que ocorreram após o início em SP
    df_validacao = df_validacao[df_validacao['distancia_dias'] >= 0]
    
    if df_validacao.empty:
        print("Nenhuma correspondência encontrada entre os dados da rede e os dados de COVID-19.")
        return

    # --- Resultados da Validação ---
    print("\n--- RESULTADOS DA VALIDAÇÃO ---")
    correlacao = df_validacao[['distancia_rede', 'distancia_dias']].corr().iloc[0, 1]
    
    print(f"Correlação de Pearson entre a distância na rede de mobilidade e a distância em dias: {correlacao:.4f}")
    
    # Plotar o resultado
    plt.figure(figsize=(10, 8))
    sns.regplot(data=df_validacao, x='distancia_rede', y='distancia_dias')
    plt.title('Validação da Rede: Distância de Rede vs. Dias para Primeiro Caso de COVID-19')
    plt.xlabel('Distância na Rede de Mobilidade (a partir de SP)')
    plt.ylabel('Dias desde o Primeiro Caso em SP')
    plt.show()

    print("\nINTERPRETAÇÃO:")
    print("Uma correlação positiva sugere que a rede de mobilidade é um bom preditor da disseminação.")
    print("Isso significa que municípios 'mais distantes' na rede (menor fluxo a partir de SP) tenderam a registrar seus primeiros casos mais tarde.")
    print("--- SCRIPT 5 CONCLUÍDO ---")

if __name__ == '__main__':
    run()