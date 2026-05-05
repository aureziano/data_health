import pandas as pd
import numpy as np
from scipy.stats import skew, kurtosis
from pathlib import Path
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config
import geopandas as gpd

def clean_uf(val):
    s = str(val).split('.')[0].strip()
    return s.zfill(2) if s.isdigit() else s

def extrair_idade(valor):
    try:
        v = float(valor)
        if np.isnan(v): return np.nan
        s = str(int(v)).zfill(4)
        prefixo = s[0]
        quant = int(s[1:])
        if prefixo == '4': return quant 
        elif prefixo == '3': return quant / 12 
        elif prefixo == '2': return quant / 365 
        elif prefixo == '1': return quant / (365 * 24) 
        return np.nan
    except: return np.nan

def categeorizar_idade(idade):
    if pd.isna(idade): return "Não Informado"
    if idade < 15: return "Crianças (<15)"
    if idade < 30: return "Jovens (15-29)"
    if idade < 60: return "Adultos (30-59)"
    return "Idosos (60+)"

def categorizar_escolaridade(esc):
    if pd.isna(esc) or esc == 9: return "Ignorado"
    if esc == 0: return "Analfabeto"
    if esc in [1, 2, 3]: return "Fundamental I"
    if esc in [4, 5]: return "Fundamental II"
    if esc == 6: return "Médio"
    if esc in [7, 8]: return "Superior"
    return "Outros"

def processar_analise_v3():
    print("--- INICIANDO PROCESSAMENTO: ANÁLISE SOCIO-CLÍNICA PROFUNDA (V3.2) ---")
    
    path_hansi = config.PATHS['hanceniase']
    cols_hansi = ['NU_ANO', 'SG_UF_NOT', 'ID_MN_RESI', 'AVALIA_N', 'AVAL_ATU_N', 
                  'NU_IDADE_N', 'CS_SEXO', 'CLASSOPERA', 'TPALTA_N', 'CS_RACA', 'CS_ESCOL_N']
    
    print(f"Lendo dados de hanseníase: {path_hansi}")
    df = pd.read_csv(path_hansi, usecols=cols_hansi, low_memory=False)
    
    # 1. Limpeza e Tipagem
    df['NU_ANO'] = pd.to_numeric(df['NU_ANO'], errors='coerce')
    df['AVALIA_N'] = pd.to_numeric(df['AVALIA_N'], errors='coerce')
    df['AVAL_ATU_N'] = pd.to_numeric(df['AVAL_ATU_N'], errors='coerce')
    df['TPALTA_N'] = pd.to_numeric(df['TPALTA_N'], errors='coerce')
    df['IDADE'] = df['NU_IDADE_N'].apply(extrair_idade)
    df['FAIXA_ETARIA'] = df['IDADE'].apply(categeorizar_idade)
    df['ESCOLARIDADE'] = pd.to_numeric(df['CS_ESCOL_N'], errors='coerce').apply(categorizar_escolaridade)
    df['ID_MN_RESI'] = df['ID_MN_RESI'].astype(str).str.split('.').str[0].str.zfill(6)
    
    # Sexo: Dados reais usam M/F
    df['SEXO'] = df['CS_SEXO'].map({'M': 'Masculino', 'F': 'Feminino'}).fillna('Ignorado')
    # Classe Operacional: 1=PB, 2=MB
    df['CLASSE'] = pd.to_numeric(df['CLASSOPERA'], errors='coerce').map({1: 'PB', 2: 'MB'}).fillna('Ignorado')

    # 2. Análise de Qualidade
    qualidade_anual = df.groupby('NU_ANO').agg(
        total_casos=('NU_ANO', 'count'),
        diag_avaliado=('AVALIA_N', lambda x: x.isin([0,1,2]).sum()),
        cura_avaliada=('AVAL_ATU_N', lambda x: x.isin([0,1,2]).sum())
    )
    qualidade_anual['pct_completude_cura'] = (qualidade_anual['cura_avaliada'] / qualidade_anual['total_casos']) * 100
    
    # 3. Estatísticas Descritivas
    df_valid = df[df['AVALIA_N'].isin([0, 1, 2]) & df['AVAL_ATU_N'].isin([0, 1, 2])].copy()
    df_valid['evolucao'] = 'Estável'
    df_valid.loc[df_valid['AVAL_ATU_N'] < df_valid['AVALIA_N'], 'evolucao'] = 'Melhora'
    df_valid.loc[df_valid['AVAL_ATU_N'] > df_valid['AVALIA_N'], 'evolucao'] = 'Piora'
    
    # 4. Taxa de Melhora por Determinantes (2018-2022)
    foco_period = df_valid[df_valid['NU_ANO'].between(2018, 2022)]
    
    def get_summary(df_sub, group_col):
        res = df_sub.groupby(group_col).agg(
            total=('NU_ANO', 'count'),
            melhora=('evolucao', lambda x: (x == 'Melhora').sum()),
            piora=('evolucao', lambda x: (x == 'Piora').sum())
        ).reset_index()
        res['Taxa_Melhora'] = (res['melhora'] / res['total']) * 100
        res['Taxa_Piora'] = (res['piora'] / res['total']) * 100
        return res

    social_sexo = get_summary(foco_period, 'SEXO')
    social_idade = get_summary(foco_period, 'FAIXA_ETARIA')
    social_classe = get_summary(foco_period, 'CLASSE')
    social_escol = get_summary(foco_period, 'ESCOLARIDADE')

    # 5. Geográfico - Microrregiões
    print("Mapeando Microrregiões...")
    try:
        mun_shp = gpd.read_file('data/MAPAS/BR_Municipios_2022/BR_Municipios_2022.shp')
        mic_shp = gpd.read_file('data/MAPAS/BR_Microrregioes_2022/BR_Microrregioes_2022.shp')
        mun_shp['code_6'] = mun_shp['CD_MUN'].astype(str).str[:6]
        mun_centroids = mun_shp.copy()
        mun_centroids['geometry'] = mun_centroids.geometry.centroid
        mun_to_mic = gpd.sjoin(mun_centroids, mic_shp[['CD_MICRO', 'NM_MICRO', 'geometry']], how='left', predicate='within')
        mapping_dict = mun_to_mic.drop_duplicates(subset='code_6').set_index('code_6')[['CD_MICRO', 'NM_MICRO']].to_dict('index')
        df_valid['CD_MICRO'] = df_valid['ID_MN_RESI'].map(lambda x: mapping_dict.get(x, {}).get('CD_MICRO', '99999'))
        mic_stats = foco_period.assign(
            CD_MICRO=lambda d: d['ID_MN_RESI'].map(lambda x: mapping_dict.get(x, {}).get('CD_MICRO', '99999'))
        ).groupby('CD_MICRO').agg(
            taxa_melhora=('evolucao', lambda x: (x == 'Melhora').mean() * 100),
            vol_casos=('NU_ANO', 'count')
        ).reset_index()
    except: mic_stats = pd.DataFrame()

    # 6. Estatísticas por Classe ( MB vs PB)
    print("Calculando estatísticas por classe operacional...")
    stats_socio = df.groupby(['NU_ANO', 'CLASSE']).agg(
        Média_Diag=('AVALIA_N', lambda x: x[x.isin([0,1,2])].mean())
    ).reset_index().rename(columns={'NU_ANO': 'Ano', 'CLASSE': 'Classe'})

    # Salvar
    results_dir = Path('results/incapacidade_v3')
    results_dir.mkdir(parents=True, exist_ok=True)
    qualidade_anual.to_csv(results_dir / 'qualidade_dados.csv')
    social_sexo.to_csv(results_dir / 'social_sexo.csv', index=False)
    social_idade.to_csv(results_dir / 'social_idade.csv', index=False)
    social_classe.to_csv(results_dir / 'social_classe.csv', index=False)
    social_escol.to_csv(results_dir / 'social_escolaridade.csv', index=False)
    if not mic_stats.empty:
        mic_stats.to_csv(results_dir / 'microrregioes_evolucao.csv', index=False)
    
    stats_socio.to_csv(results_dir / 'estatisticas_socio_clinicas.csv', index=False)
    
    print(f"Processamento V3.2 concluído em {results_dir}")

if __name__ == "__main__":
    processar_analise_v3()
