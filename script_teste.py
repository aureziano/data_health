import pandas as pd
from pathlib import Path

# =============================================================================
# SCRIPT DE DIAGNÓSTICO FINAL: "MOSTRE-ME OS DADOS"
# =============================================================================
print("--- INICIANDO DIAGNÓSTICO PROFUNDO DAS FONTES DE DADOS ---")

try:
    ano_analise = 2022
    base_path = Path('.')

    # --- 1. Análise de 'cidades_sentinela' ---
    print("\n--- 1. Analisando 'resultado_cidades_sentinela_2022.csv' ---")
    caminho_sentinela = base_path / 'results' / f'resultado_cidades_sentinela_{ano_analise}.csv'
    df_sentinela = pd.read_csv(caminho_sentinela)
    df_sentinela.rename(columns={'Unnamed: 0': 'id_municipio'}, inplace=True)
    df_sentinela['id_municipio'] = pd.to_numeric(df_sentinela['id_municipio'], errors='coerce').astype('Int64')
    
    print(f"Shape: {df_sentinela.shape}")
    print(f"Tipo de dado da coluna 'id_municipio': {df_sentinela['id_municipio'].dtype}")
    print("5 exemplos de 'id_municipio':", df_sentinela['id_municipio'].dropna().unique()[:5])
    # Guardar o conjunto de IDs para comparação
    ids_sentinela = set(df_sentinela['id_municipio'].dropna())

    # --- 2. Análise de 'populacao_municipios.csv' ---
    print("\n--- 2. Analisando 'populacao_municipios.csv' para 2022 ---")
    path_pop = base_path / 'data' / 'IBGE' / 'populacao_municipios.csv'
    df_pop = pd.read_csv(path_pop)
    df_pop_ano = df_pop[df_pop['ano'] == ano_analise].copy()
    df_pop_ano['id_municipio'] = pd.to_numeric(df_pop_ano['id_municipio'], errors='coerce').astype('Int64')

    print(f"Shape: {df_pop_ano.shape}")
    print(f"Tipo de dado da coluna 'id_municipio': {df_pop_ano['id_municipio'].dtype}")
    print("5 exemplos de 'id_municipio':", df_pop_ano['id_municipio'].dropna().unique()[:5])
    
    # --- 3. Análise de 'HANSENIASE_TOTAL_28_02_2025.csv' ---
    print("\n--- 3. Analisando 'HANSENIASE_TOTAL_28_02_2025.csv' para 2022 ---")
    path_hans = base_path / 'data' / 'HANSENIASE' / 'HANSENIASE_TOTAL_28_02_2025.csv'
    df_hans = pd.read_csv(path_hans, usecols=['ID_MN_RESI', 'DT_NOTIFIC'], low_memory=False)
    df_hans['DT_NOTIFIC'] = pd.to_datetime(df_hans['DT_NOTIFIC'], errors='coerce')
    df_hans['ano'] = df_hans['DT_NOTIFIC'].dt.year
    df_hans_ano = df_hans[df_hans['ano'] == ano_analise].copy()
    
    # Renomeia e agrupa
    df_hans_ano.rename(columns={'ID_MN_RESI': 'id_municipio'}, inplace=True)
    df_casos_agrupado = df_hans_ano.groupby('id_municipio').size().reset_index(name='casos_hanseniase')
    
    # Força a conversão do tipo de dado, removendo nulos ANTES
    df_casos_agrupado.dropna(subset=['id_municipio'], inplace=True)
    df_casos_agrupado['id_municipio'] = df_casos_agrupado['id_municipio'].astype(int)
    
    print(f"Shape após agrupar: {df_casos_agrupado.shape}")
    print(f"Soma total de casos: {df_casos_agrupado['casos_hanseniase'].sum()}")
    print(f"Tipo de dado da coluna 'id_municipio': {df_casos_agrupado['id_municipio'].dtype}")
    print("5 exemplos de 'id_municipio' com casos:", df_casos_agrupado['id_municipio'].dropna().unique()[:5])
    # Guardar o conjunto de IDs para comparação
    ids_hanseniase = set(df_casos_agrupado['id_municipio'].dropna())

    # --- 4. A Prova Final: Intersecção dos Conjuntos de IDs ---
    print("\n--- 4. VERIFICAÇÃO FINAL DA SOBREPOSIÇÃO DE MUNICÍPIOS ---")
    
    intersecao = ids_sentinela.intersection(ids_hanseniase)
    
    print(f"Municípios na rede de mobilidade ('sentinela'): {len(ids_sentinela)}")
    print(f"Municípios com casos de hanseníase em 2022: {len(ids_hanseniase)}")
    print(f"Número de municípios EM COMUM entre os dois conjuntos: {len(intersecao)}")
    
    if len(intersecao) == 0:
        print("\nCONCLUSÃO: A intersecção é ZERO. Nenhum município com caso de hanseníase está presente na sua lista de cidades da rede.")
        print("Isso indica um problema fundamental de incompatibilidade nos códigos dos municípios entre os arquivos de origem, apesar de parecerem iguais.")
        print("Possível causa: os códigos de municípios nos arquivos de saúde e de mobilidade não se referem à mesma base (ex: um pode ter 6 dígitos e outro 7).")
    else:
        print("\nCONCLUSÃO: Existem municípios em comum! O problema é mais sutil e pode estar na lógica do merge do script principal.")
        print("Exemplos de municípios em comum:", list(intersecao)[:5])

except Exception as e:
    print(f"\nOcorreu um erro inesperado durante o diagnóstico: {e}")