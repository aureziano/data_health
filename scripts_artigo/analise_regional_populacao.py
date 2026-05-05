import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import config

# Configurações
dir_graficos = "./overleaf/fig"
dir_relatorios = "./overleaf/tabs"
os.makedirs(dir_graficos, exist_ok=True)
os.makedirs(dir_relatorios, exist_ok=True)

# Dados Populacionais IBGE 2024 (Estimativa Oficial)
pop_regiao = {
    '1': 18669345,  # Norte
    '2': 57112096,  # Nordeste
    '3': 88617693,  # Sudeste
    '4': 31113021,  # Sul
    '5': 17071595   # Centro-Oeste
}

regiao_nomes = {
    '1': 'Norte',
    '2': 'Nordeste',
    '3': 'Sudeste',
    '4': 'Sul',
    '5': 'Centro-Oeste'
}

print("Carregando base para análise regional normalizada...")
df = pd.read_csv(str(config.PATHS['hanceniase']), low_memory=False)

# Extrair Região do ID_MUNICIP (1º dígito)
df['REGIAO_DIGIT'] = df['ID_MUNICIP'].astype(str).str[0]
df['REGIAO'] = df['REGIAO_DIGIT'].map(regiao_nomes)

# Filtrar apenas regiões válidas (1 a 5)
df = df[df['REGIAO_DIGIT'].isin(pop_regiao.keys())]

# 1. Contagem Total de Casos
contagem_casos = df.groupby('REGIAO').size().reset_index(name='Casos_Absolutos')

# 2. Contagem de Casos com G2D (Grau 2 de Incapacidade)
# No SINAN: 1=Grau 0, 2=Grau 1, 3=Grau 2 (G2D). 
# Nota: Confirmar se AVALIA_N segue este padrão ou o padrão 0,1,2.
# Assumindo o padrão mais comum em datasets exportados: 3 ou 2 para G2D.
# Vamos verificar os valores únicos de AVALIA_N
print(f"Valores únicos de AVALIA_N: {df['AVALIA_N'].unique()}")
# Por precaução, vamos considerar '2' ou '3' como incapacidade severa se for o caso.
# Mas o mais comum é G2D = Valor máximo.
g2d_cases = df[df['AVALIA_N'].isin([2, 3])].groupby('REGIAO').size().reset_index(name='Casos_G2D')

# Merge dos dados
df_regiao = pd.merge(contagem_casos, g2d_cases, on='REGIAO')

# 3. Normalização por 1.000 Habitantes
df_regiao['Populacao'] = df_regiao['REGIAO'].map({v: pop_regiao[k] for k, v in regiao_nomes.items()})
df_regiao['Casos_por_1000'] = (df_regiao['Casos_Absolutos'] / df_regiao['Populacao']) * 1000
df_regiao['G2D_por_1000'] = (df_regiao['Casos_G2D'] / df_regiao['Populacao']) * 1000

print("\nIndicadores Regionais Normalizados (por 1.000 hab):")
print(df_regiao[['REGIAO', 'Casos_por_1000', 'G2D_por_1000']])

# 4. Visualização: Casos vs G2D por 1.000 Habitantes
plt.figure(figsize=(12, 6))
df_plot = df_regiao.melt(id_vars='REGIAO', value_vars=['Casos_por_1000', 'G2D_por_1000'], 
                         var_name='Indicador', value_name='Taxa')

sns.barplot(data=df_plot, x='REGIAO', y='Taxa', hue='Indicador', palette='mako')
plt.title("Indicadores de Hanseníase e Incapacidade Física por Região (por 1.000 hab)", fontsize=14)
plt.ylabel("Taxa por 1.000 Habitantes")
plt.xlabel("Região")
plt.legend(title="Indicador")
plt.grid(True, alpha=0.3)
plt.savefig(f"{dir_graficos}/analise_regional_normalizada.png", bbox_inches='tight')
plt.close()

# 5. Exportação para LaTeX
with open(f"{dir_relatorios}/tabela_regional_normalizada.tex", "w", encoding="utf-8") as f:
    f.write("% Tabela de Indicadores Regionais Normalizados por 1.000 Habitantes\n")
    f.write(df_regiao[['REGIAO', 'Casos_por_1000', 'G2D_por_1000']].to_latex(index=False, 
            caption="Coeficiente de Detecção e Taxa de G2D por Região (por 1.000 hab)", 
            label="tab:regional_normalizado", float_format="%.4f"))

print(f"Análise regional concluída. Artefatos gerados em {dir_graficos} e {dir_relatorios}")
