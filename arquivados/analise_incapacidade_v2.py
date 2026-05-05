import pandas as pd
import numpy as np
from pathlib import Path
import config
import os
import geopandas as gpd

def clean_uf(val):
    s = str(val).split('.')[0].strip()
    return s.zfill(2) if s.isdigit() else s

def processar_analise_v2():
    print("--- INICIANDO PROCESSAMENTO: ANÁLISE PROFUNDA DE INCAPACIDADE (V2.2) ---")
    
    path_hansi = config.PATHS['hanceniase']
    cols_hansi = ['NU_ANO', 'SG_UF_NOT', 'ID_MN_RESI', 'AVALIA_N', 'AVAL_ATU_N', 'CLASSOPERA']
    
    print(f"Lendo dados de hanseníase: {path_hansi}")
    df = pd.read_csv(path_hansi, usecols=cols_hansi, low_memory=False)
    
    # 1. Limpeza e Tipagem
    df['NU_ANO'] = pd.to_numeric(df['NU_ANO'], errors='coerce')
    df['AVALIA_N'] = pd.to_numeric(df['AVALIA_N'], errors='coerce')
    df['AVAL_ATU_N'] = pd.to_numeric(df['AVAL_ATU_N'], errors='coerce')
    df['ID_MN_RESI'] = df['ID_MN_RESI'].astype(str).str.split('.').str[0].str.zfill(6)
    
    # Mapeamento UF
    uf_nome_map = {
        '11': 'RO', '12': 'AC', '13': 'AM', '14': 'RR', '15': 'PA', '16': 'AP', '17': 'TO',
        '21': 'MA', '22': 'PI', '23': 'CE', '24': 'RN', '25': 'PB', '26': 'PE', '27': 'AL', '28': 'SE', '29': 'BA',
        '31': 'MG', '32': 'ES', '33': 'RJ', '35': 'SP',
        '41': 'PR', '42': 'SC', '43': 'RS',
        '50': 'MS', '51': 'MT', '52': 'GO', '53': 'DF'
    }
    df['uf_code'] = df['SG_UF_NOT'].apply(clean_uf)
    df['uf_sigla'] = df['uf_code'].map(uf_nome_map).fillna('??')

    # 2. Análise de Qualidade (Compleitude)
    print("Analisando qualidade dos dados (Série Completa)...")
    qualidade_anual = df.groupby('NU_ANO').agg(
        total_casos=('NU_ANO', 'count'),
        missing_diag=('AVALIA_N', lambda x: x.isna().sum()),
        missing_cura=('AVAL_ATU_N', lambda x: x.isna().sum()),
        valid_pairs=('NU_ANO', lambda x: ((df.loc[x.index, 'AVALIA_N'].isin([0,1,2])) & (df.loc[x.index, 'AVAL_ATU_N'].isin([0,1,2]))).sum())
    )
    qualidade_anual['pct_completude_cura'] = (1 - (qualidade_anual['missing_cura'] / qualidade_anual['total_casos'])) * 100
    qualidade_anual['pct_pares_validos'] = (qualidade_anual['valid_pairs'] / qualidade_anual['total_casos']) * 100
    
    # Filtrar apenas pares válidos para análise de evolução
    df_valid = df[df['AVALIA_N'].isin([0, 1, 2]) & df['AVAL_ATU_N'].isin([0, 1, 2])].copy()
    
    # 3. Estatística Descritiva por Ano (Série Completa)
    print("Calculando estatísticas descritivas (Mean, Var, Mode, Skew)...")
    from scipy.stats import skew, kurtosis

    stats_list = []
    for ano, group in df_valid.groupby('NU_ANO'):
        stats_list.append({
            'NU_ANO': ano,
            'mean_diag': group['AVALIA_N'].mean(),
            'var_diag': group['AVALIA_N'].var(),
            'skew_diag': skew(group['AVALIA_N']),
            'mean_cura': group['AVAL_ATU_N'].mean(),
            'var_cura': group['AVAL_ATU_N'].var(),
            'skew_cura': skew(group['AVAL_ATU_N']),
            'n_casos': len(group)
        })
    stats_long = pd.DataFrame(stats_list).set_index('NU_ANO')
    
    # 4. Taxa de Melhora e Piora Temporal
    print("Calculando taxas de evolução temporal...")
    df_valid['evolucao'] = 'Estável'
    df_valid.loc[df_valid['AVAL_ATU_N'] < df_valid['AVALIA_N'], 'evolucao'] = 'Melhora'
    df_valid.loc[df_valid['AVAL_ATU_N'] > df_valid['AVALIA_N'], 'evolucao'] = 'Piora'
    
    evol_anual = df_valid.groupby(['NU_ANO', 'evolucao']).size().unstack(fill_value=0)
    evol_anual_pct = evol_anual.div(evol_anual.sum(axis=1), axis=0) * 100
    
    # 5. Geográfico: Município -> Microregião (Usando mapas 2022)
    print("Processando mapeamento microrregional...")
    try:
        mun_shp = gpd.read_file('data/MAPAS/BR_Municipios_2022/BR_Municipios_2022.shp')
        mic_shp = gpd.read_file('data/MAPAS/BR_Microrregioes_2022/BR_Microrregioes_2022.shp')
        
        # Mapping via spatial join (safer since we have centroids)
        mun_shp['code_6'] = mun_shp['CD_MUN'].astype(str).str[:6]
        mun_centroids = mun_shp.copy()
        mun_centroids['geometry'] = mun_centroids.geometry.centroid
        
        mun_to_mic = gpd.sjoin(mun_centroids, mic_shp[['CD_MICRO', 'NM_MICRO', 'geometry']], how='left', predicate='within')
        mapping_df = mun_to_mic.drop_duplicates(subset='code_6').set_index('code_6')[['CD_MICRO', 'NM_MICRO']]
        mapping_dict = mapping_df.to_dict('index')
    except Exception as e:
        print(f"Erro no mapeamento geográfico: {e}")
        mapping_dict = {}

    df_valid['CD_MICRO'] = df_valid['ID_MN_RESI'].map(lambda x: mapping_dict.get(x, {}).get('CD_MICRO', '99999'))
    df_valid['NM_MICRO'] = df_valid['ID_MN_RESI'].map(lambda x: mapping_dict.get(x, {}).get('NM_MICRO', 'Desconhecido'))
    
    # Agregações para Visualização (Recorte 2018-2022 para mapas recentes)
    df_foco = df_valid[df_valid['NU_ANO'].between(2018, 2022)].copy()
    
    # Microregiões
    mic_evol = df_foco.groupby(['CD_MICRO', 'NM_MICRO', 'evolucao']).size().unstack(fill_value=0).reset_index()
    if not mic_evol.empty:
        mic_evol['total'] = mic_evol.get('Melhora',0) + mic_evol.get('Estável',0) + mic_evol.get('Piora',0)
        mic_evol['taxa_melhora'] = (mic_evol.get('Melhora',0) / mic_evol['total']) * 100
    
    # UF
    uf_evol = df_foco.groupby(['uf_sigla', 'evolucao']).size().unstack(fill_value=0).reset_index()
    if not uf_evol.empty:
        uf_evol['total'] = uf_evol.get('Melhora',0) + uf_evol.get('Estável',0) + uf_evol.get('Piora',0)
        uf_evol['taxa_melhora'] = (uf_evol.get('Melhora',0) / uf_evol['total']) * 100
    
    # 6. Salvar
    results_dir = Path('results/incapacidade_v2')
    results_dir.mkdir(parents=True, exist_ok=True)
    
    qualidade_anual.to_csv(results_dir / 'qualidade_dados.csv')
    stats_long.to_csv(results_dir / 'estatisticas_longitudinais.csv')
    evol_anual_pct.to_csv(results_dir / 'evolucao_temporal_pct.csv')
    mic_evol.to_csv(results_dir / 'evolucao_microrregioes.csv', index=False)
    uf_evol.to_csv(results_dir / 'evolucao_uf.csv', index=False)
    
    print(f"Processamento concluído. Resultados salvos em {results_dir}")

if __name__ == "__main__":
    processar_analise_v2()
