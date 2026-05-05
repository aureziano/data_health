import os
import config
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.formula.api as smf
import warnings
warnings.filterwarnings("ignore")

# Configurações de diretório
dir_graficos = "./overleaf/fig"
dir_relatorios = "./overleaf/tabs"
os.makedirs(dir_graficos, exist_ok=True)
os.makedirs(dir_relatorios, exist_ok=True)

print("Iniciando Análise do Paradoxo de Gravidade Pandêmica [Ref: 72]...")

path_data = str(config.PATHS['hanceniase'])
df = pd.read_csv(path_data, encoding="utf-8", low_memory=False)

# Converter data e extrair o período
df['DT_DIAG'] = pd.to_datetime(df['DT_DIAG'], errors='coerce')
df = df.dropna(subset=['DT_DIAG', 'AVALIA_N'])
# Filtrar entre 2012 e 2024
df = df[(df['DT_DIAG'].dt.year >= 2012) & (df['DT_DIAG'].dt.year <= 2024)]

# Padronizar AVALIA_N (1=0, 2=1, 3=2). No caso do SINAN bruto pode ser 1, 2, 3 ou 0, 1, 2, 8, 9.
# Vamos focar na severidade. Tratamento conservador com base nas métricas:
# Consideramos 3 ou 2 como Grau 2 dependendo do dataset, mas como estamos olhando pra evolução, vamos categorizar.
# Grau Oculto ou Indeterminado são filtrados para essa análise.
df = df[df['AVALIA_N'].isin([1, 2, 3])]
df['GIF'] = df['AVALIA_N'] - 1 # De 1,2,3 para 0,1,2
df['G2D_Flag'] = np.where(df['GIF'] == 2, 1, 0)

# Criando a linha do tempo trimestral
df['Periodo'] = df['DT_DIAG'].dt.to_period('Q')
df['Periodo_Str'] = df['Periodo'].astype(str)

# ---------------------------------------------------------
# 1/2. Interrupted Time Series (ITS) [Ref: 69]
# ---------------------------------------------------------
# Agregando por trimestre
ts_df = df.groupby('Periodo').agg(
    Total_Casos=('ID_AGRAVO', 'count'),
    Casos_G2D=('G2D_Flag', 'sum'),
    GIF_Medio=('GIF', 'mean')
).reset_index()

ts_df['G2D_Ratio'] = ts_df['Casos_G2D'] / ts_df['Total_Casos']
ts_df['Time'] = np.arange(1, len(ts_df) + 1)
# Intervenção a partir de Q2 2020 (março 2020) [Ref: 222-224]
ts_df['Covid_Intervention'] = np.where(ts_df['Periodo'].dt.year >= 2020, 1, 0)
# Ajustando para pós Q1 2020 se aprofundarmos, vamos colocar >= 2020Q2
ts_df['Covid_Intervention'] = np.where(ts_df['Periodo'].astype(str) >= '2020Q2', 1, 0)
ts_df['Time_Post_Intervention'] = np.where(ts_df['Covid_Intervention'] == 1, ts_df['Time'] - ts_df[ts_df['Periodo'].astype(str) == '2020Q2']['Time'].values[0], 0)

print("Ajustando Modelo OLS para ITS (G2D_Ratio vs Tempo)...")
model = smf.ols('G2D_Ratio ~ Time + Covid_Intervention + Time_Post_Intervention', data=ts_df).fit()

# Pega a tabela de coeficientes diretamente como pandas DataFrame usando summary2, evitando dependencia lxml
its_df = model.summary2().tables[1]

# ---------------------------------------------------------
# 3. Comparação Diagnóstico vs. Cura (A Falsa Cura) [Ref: 522-527]
# ---------------------------------------------------------
# AVALIA_CURA
falsa_cura_stats = []
periodos_dict = {
    "Pre-Pand (2012-2019)": (2012, 2019),
    "Pandemia (2020-2022)": (2020, 2022),
    "Recuperacao (2023-2024)": (2023, 2024)
}

for name, (start, end) in periodos_dict.items():
    df_period = df[(df['DT_DIAG'].dt.year >= start) & (df['DT_DIAG'].dt.year <= end)]
    avaliados_diag = len(df_period)
    # Pessoas que possuem AVAL_ATU_N missing ou não avaliado/ignorado
    # Presumindo que NaN, 0, 9 significam falta de avaliação na alta
    avaliados_alta = df_period['AVAL_ATU_N'].notna().sum() if 'AVAL_ATU_N' in df_period.columns else df_period['AVALIA_N'].notna().sum()
    
    # Tratando Falsa Cura (Missing evaluation at discharge)
    if 'AVAL_ATU_N' in df_period.columns:
        cura_av = df_period['AVAL_ATU_N'].isin([1, 2, 3]).sum()
    else:
        cura_av, avaliados_diag = 0, 1

    pct_avaliado = (cura_av / avaliados_diag) * 100 if avaliados_diag > 0 else 0
    falsa_cura_stats.append({
        "Cenario": name,
        "Gap Diagnostico": f"{df_period['G2D_Flag'].mean()*100:.1f}% com G2D",
        "Avaliados na Cura (%)": f"{pct_avaliado:.1f}% [Falsa Cura -> 562-564]" if pct_avaliado > 0 else "Dados Faltantes"
    })

df_falsa_cura = pd.DataFrame(falsa_cura_stats)

# ---------------------------------------------------------
# 4. Visualização: Stacked Area Chart (Gap Negativo e Gap Positivo) [Ref: 494, 519]
# ---------------------------------------------------------
area_df = df.groupby(['Periodo_Str', 'GIF']).size().unstack(fill_value=0)
area_df = area_df.div(area_df.sum(axis=1), axis=0) * 100 # Em porcentagem

plt.figure(figsize=(14, 7))
# Reindexando para garantir que o plot seja continuo se faltar algum trimestre
trimestres = pd.period_range(start='2012Q1', end='2024Q4', freq='Q').astype(str)
area_df = area_df.reindex(trimestres).fillna(0)

x = np.arange(len(area_df))
plt.stackplot(x, area_df[0], area_df[1], area_df[2], 
              labels=['Grau 0 (G0) - Baixa Gravidade', 'Grau 1 (G1) - Risco', 'Grau 2 (G2D) - Deficiência Irreversível'],
              colors=['#2ecc71', '#f1c40f', '#e74c3c'], alpha=0.85)

# Areas Pandemica e Gap [Ref: 72]
plt.axvspan(x[trimestres == '2020Q2'][0], x[trimestres == '2022Q4'][0], color='black', alpha=0.1, label='Fase Aguda Pandêmica (Subnotificação)')
plt.axvspan(x[trimestres == '2023Q1'][0], len(area_df)-1, color='blue', alpha=0.1, label='Gap Positivo / Recuperação (Teto de Supernotificação)')

plt.xticks(ticks=x[::4], labels=trimestres[::4], rotation=45)
plt.title("Evolução Percentual da Gravidade da Hanseníase (Paradoxo Pandêmico)\nEvidência Visual do Aumento Relativo de G2D [Ref: 72, 494]", fontsize=14, pad=15)
plt.ylabel("Composição (%)", fontsize=12)
plt.xlabel("Trimestre", fontsize=12)
plt.legend(loc='lower left')
plt.margins(x=0, y=0)
plt.grid(True, linestyle='--', alpha=0.5)

# Adicionando predição ITS na tela
plt.plot(x, model.predict(ts_df) * 100, color='darkred', linewidth=3, linestyle='--', label='Tendência ITS (G2D_Ratio)')
plt.legend(loc='best')

plt.savefig(f"{dir_graficos}/paradoxo_gravidade_stacked.png", dpi=300, bbox_inches='tight')
plt.close()

# ---------------------------------------------------------
# Exportando Resultados (LaTeX)
# ---------------------------------------------------------
with open(f"{dir_relatorios}/resultados_paradoxo.tex", "w", encoding="utf-8") as f:
    f.write("% Paradoxo de Gravidade Pandêmica: Efeito da subnotificação na severidade\n")
    f.write("% Reference Quotes: [69] Interrupted Time Series, [72] Mello et al.\n\n")
    f.write("\\subsection*{Interrupted Time Series (ITS) OLS Model}\n")
    f.write(its_df.to_latex(label="tab:its_results", caption="Coeficientes OLS para a proporção de G2D antes e depois do início da COVID-19 [Ref: 69]"))
    f.write("\n\n\\subsection*{Tracking da Falsa Cura e Gap Positivo}\n")
    f.write("% Ref: Falsa Cura [562-564]; Teto de Supernotificacao [522-527]\n")
    f.write(df_falsa_cura.to_latex(index=False, label="tab:falsa_cura", caption="Aumento do Diagnóstico de Gravidade e Queda na Avaliação de Cura Pós-Pandemia"))

print("✅ Análise do Paradoxo Pandêmico concluída. Arquivos gerados.")
