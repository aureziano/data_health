import pandas as pd
import numpy as np
from pathlib import Path
import config

def processar_analise():
    print("--- INICIANDO PROCESSAMENTO: ANÁLISE DE INCAPACIDADE (DEBUG V3) ---")
    
    # Caminhos
    path_hansi = config.PATHS['hanceniase']
    path_pop = config.PATHS['populacao']
    
    # Colunas de interesse
    cols_hansi = ['NU_ANO', 'SG_UF_NOT', 'AVALIA_N', 'AVAL_ATU_N']
    
    print(f"Lendo dados: {path_hansi}")
    df = pd.read_csv(path_hansi, usecols=cols_hansi, low_memory=False)
    
    # Limpeza
    df['NU_ANO'] = pd.to_numeric(df['NU_ANO'], errors='coerce')
    df['AVALIA_N'] = pd.to_numeric(df['AVALIA_N'], errors='coerce')
    df['AVAL_ATU_N'] = pd.to_numeric(df['AVAL_ATU_N'], errors='coerce')
    
    # Filtrar válidos
    df_valid = df[df['AVALIA_N'].isin([0, 1, 2]) & df['AVAL_ATU_N'].isin([0, 1, 2])].copy()
    
    # Mapeamentos
    regioes_map = {
        '11': 'Norte', '12': 'Norte', '13': 'Norte', '14': 'Norte', '15': 'Norte', '16': 'Norte', '17': 'Norte',
        '21': 'Nordeste', '22': 'Nordeste', '23': 'Nordeste', '24': 'Nordeste', '25': 'Nordeste', '26': 'Nordeste', '27': 'Nordeste', '28': 'Nordeste', '29': 'Nordeste',
        '31': 'Sudeste', '32': 'Sudeste', '33': 'Sudeste', '35': 'Sudeste',
        '41': 'Sul', '42': 'Sul', '43': 'Sul',
        '50': 'Centro-Oeste', '51': 'Centro-Oeste', '52': 'Centro-Oeste', '53': 'Centro-Oeste'
    }
    
    uf_nome_map = {
        '11': 'RO', '12': 'AC', '13': 'AM', '14': 'RR', '15': 'PA', '16': 'AP', '17': 'TO',
        '21': 'MA', '22': 'PI', '23': 'CE', '24': 'RN', '25': 'PB', '26': 'PE', '27': 'AL', '28': 'SE', '29': 'BA',
        '31': 'MG', '32': 'ES', '33': 'RJ', '35': 'SP',
        '41': 'PR', '42': 'SC', '43': 'RS',
        '50': 'MS', '51': 'MT', '52': 'GO', '53': 'DF'
    }
    
    # Processar UF_NOT
    # Convertemos para string, pegamos o que vem antes do ponto (se houver) e preenchemos com zero à esquerda
    def clean_uf(val):
        s = str(val).split('.')[0].strip()
        return s.zfill(2) if s.isdigit() else s

    df_valid['uf_code'] = df_valid['SG_UF_NOT'].apply(clean_uf)
    df_valid['regiao'] = df_valid['uf_code'].map(regioes_map).fillna('Desconhecido')
    df_valid['uf_sigla'] = df_valid['uf_code'].map(uf_nome_map).fillna('??')
    
    print("\nExemplo de mapeamento:")
    print(df_valid[['SG_UF_NOT', 'uf_code', 'regiao', 'uf_sigla']].head(10))
    print("\nContagem de Regiões:")
    print(df_valid['regiao'].value_counts())

    # Cálculo da Evolução
    df_valid['evolucao'] = 'Estável'
    df_valid.loc[df_valid['AVAL_ATU_N'] < df_valid['AVALIA_N'], 'evolucao'] = 'Melhora'
    df_valid.loc[df_valid['AVAL_ATU_N'] > df_valid['AVALIA_N'], 'evolucao'] = 'Piora'
    
    # Salvar parciais
    results_dir = Path('results/incapacidade')
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Históricos
    df_valid.groupby(['NU_ANO', 'evolucao']).size().unstack(fill_value=0).div(df_valid.groupby('NU_ANO').size(), axis=0).to_csv(results_dir / 'historico_evolucao_pct.csv')
    df_valid.groupby('NU_ANO')[['AVALIA_N', 'AVAL_ATU_N']].mean().to_csv(results_dir / 'historico_graus_media.csv')
    
    # Foco 2019-2022
    df_foco = df_valid[df_valid['NU_ANO'].between(2019, 2022)].copy()
    analise_estatal = df_foco.groupby(['regiao', 'uf_sigla', 'evolucao']).size().unstack(fill_value=0).reset_index()
    
    # Merge com IBGE
    df_pop = pd.read_csv(path_pop)
    pop_uf = df_pop[df_pop['ano'].between(2019, 2022)].groupby('sigla_uf')['pessoas'].mean().reset_index()
    
    final_df = analise_estatal.merge(pop_uf, left_on='uf_sigla', right_on='sigla_uf', how='left')
    final_df['casos_validos'] = final_df[['Melhora', 'Estável', 'Piora']].sum(axis=1)
    final_df['casos_100k'] = (final_df['casos_validos'] / final_df['pessoas']) * 100000
    
    final_df.to_csv(results_dir / 'analise_uf_regiao.csv', index=False)
    
    # Matriz de Transição
    pd.crosstab(df_foco['AVALIA_N'], df_foco['AVAL_ATU_N'], normalize='index').to_csv(results_dir / 'matriz_transicao_2019_2022.csv')
    
    print("\nProcessamento finalizado. Resultados salvos.")

if __name__ == "__main__":
    processar_analise()
