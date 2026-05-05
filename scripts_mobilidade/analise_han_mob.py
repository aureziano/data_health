import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

print("--- FASE 0: CARREGANDO E HARMONIZANDO DADOS PARA A ANÁLISE EPIDEMIOLÓGICA ---")

try:
    ano_analise = 2022
    base_path = Path('.')
    
    # 1. Carregar centralidade (com IDs de 6 dígitos)
    caminho_sentinela = base_path / 'results' / f'resultado_cidades_sentinela_{ano_analise}.csv'
    print(f"Carregando e harmonizando: {caminho_sentinela}")
    cidades_sentinela = pd.read_csv(caminho_sentinela)
    cidades_sentinela.rename(columns={'Unnamed: 0': 'id_municipio'}, inplace=True)
    cidades_sentinela['id_municipio'] = cidades_sentinela['id_municipio'].astype(int)

    # 2. Carregar população, harmonizar e renomear
    path_pop = base_path / 'data' / 'IBGE' / 'populacao_municipios.csv'
    print(f"Carregando e harmonizando: {path_pop.name}")
    df_pop = pd.read_csv(path_pop)
    df_pop['id_municipio'] = df_pop['id_municipio'] // 10
    
    # A CORREÇÃO FINAL ESTÁ AQUI:
    # Selecionamos apenas as colunas necessárias E renomeamos 'pessoas' para 'populacao'
    populacao_ano = df_pop[df_pop['ano'] == ano_analise][['id_municipio', 'pessoas']].rename(columns={'pessoas': 'populacao'})

    # 3. Carregar hanseníase (que já está em 6 dígitos)
    path_hans = base_path / 'data' / 'HANSENIASE' / 'HANSENIASE_TOTAL_28_02_2025.csv'
    print(f"Carregando e processando: {path_hans.name}")
    df_hans = pd.read_csv(path_hans, usecols=['ID_MN_RESI', 'DT_NOTIFIC'], low_memory=False)
    df_hans['DT_NOTIFIC'] = pd.to_datetime(df_hans['DT_NOTIFIC'], errors='coerce')
    df_hans['ano'] = df_hans['DT_NOTIFIC'].dt.year
    casos_hanseniase_ano = df_hans[df_hans['ano'] == ano_analise].rename(columns={'ID_MN_RESI': 'id_municipio'})
    casos_hanseniase_ano.dropna(subset=['id_municipio'], inplace=True)
    casos_hanseniase_ano['id_municipio'] = casos_hanseniase_ano['id_municipio'].astype(int)
    casos_hanseniase_ano = casos_hanseniase_ano.groupby('id_municipio').size().reset_index(name='casos_hanseniase')

    print(f"\nDados carregados e harmonizados para IDs de 6 dígitos (ano {ano_analise}).")

except Exception as e:
    print(f"Ocorreu um erro: {e}")
    exit()

# =============================================================================
# FASE 5: JUNÇÃO FINAL E ANÁLISE
# =============================================================================
print(f"\n--- FASE 5: ANÁLISE PARA O ANO DE {ano_analise} ---")

df_analise = pd.merge(cidades_sentinela, populacao_ano, on='id_municipio', how='left')
df_analise = pd.merge(df_analise, casos_hanseniase_ano, on='id_municipio', how='left')
df_analise['casos_hanseniase'] = df_analise['casos_hanseniase'].fillna(0)

# Agora esta linha funcionará, pois a coluna 'populacao' existe
df_analise.dropna(subset=['populacao'], inplace=True)

print("\n--- Verificação após as junções ---")
print("Análise da coluna 'casos_hanseniase' no DataFrame final:")
print(df_analise['casos_hanseniase'].describe())

df_analise['taxa_incidencia'] = (df_analise['casos_hanseniase'] / (df_analise['populacao'] + 1)) * 100000

print("\n--- Correlação entre Mobilidade e Taxa de Incidência ---")
matriz_correlacao = df_analise[['score_sentinela', 'centralidade_grau', 'centralidade_intermediacao', 'taxa_incidencia']].corr()
print("Matriz de Correlação:")
print(matriz_correlacao)

plt.figure(figsize=(10, 8))
sns.heatmap(matriz_correlacao, annot=True, cmap='coolwarm', fmt=".2f", vmin=-1, vmax=1)
plt.title(f'Correlação entre Métricas de Mobilidade e Incidência de Hanseníase ({ano_analise})')
plt.show()

sns.jointplot(data=df_analise, x='score_sentinela', y='taxa_incidencia', kind='reg', height=8)
plt.suptitle(f'Score Sentinela vs. Taxa de Incidência ({ano_analise})', y=1.02)
plt.show()

print(f"\n--- Ranking de Cidades Sentinela com Dados de Hanseníase ({ano_analise}) ---")
resultado_final = df_analise[['nome_municipio', 'uf', 'populacao', 'casos_hanseniase', 'taxa_incidencia', 'score_sentinela', 'centralidade_grau', 'centralidade_intermediacao']].copy()
resultado_final = resultado_final.sort_values('score_sentinela', ascending=False)
print(resultado_final.head(20))

output_dir = Path('results')
output_dir.mkdir(exist_ok=True)
output_filename = output_dir / f'resultado_final_mobilidade_hanseniase_{ano_analise}.csv'
resultado_final.to_csv(output_filename, index=False)
print(f"\nResultado completo da análise salvo em '{output_filename}'")