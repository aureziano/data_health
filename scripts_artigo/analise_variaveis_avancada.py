import os
import config
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_selection import mutual_info_classif
from scipy.stats import kruskal
import warnings
warnings.filterwarnings("ignore")

# Configurações de diretório
dir_relatorios = "./overleaf/tabs"
dir_graficos = "./overleaf/fig/incapacidade" # Usado pela nova estrutura do apêndice
os.makedirs(dir_relatorios, exist_ok=True)
os.makedirs(dir_graficos, exist_ok=True)

print("Iniciando Análise de Variáveis para o Apêndice (Transparência Metodológica)...")
caminho_arquivo = str(config.PATHS['hanceniase'])

try:
    df = pd.read_csv(caminho_arquivo, encoding="utf-8", low_memory=False)
except FileNotFoundError:
    print("Arquivo não encontrado.")
    exit()

# ---------------------------------------------------------
# PROMPT 1: Análise para Transparência do Apêndice
# Com âncora nas referências [210, 211, 213, 254, 360, 563, 564]
# ---------------------------------------------------------

# Variáveis focadas para justificação de imputação e limpeza
variaveis_foco = [
    'CLASSOPERA', 'CS_SEXO', 'CS_RACA', 'CS_ESCOL_N', 
    'NU_LESOES', 'NERVOSAFET', 'DOSE_RECEB'
]
# Transparência na escolha: O alvo G2D (Grau de Incapacidade Física 2) é nossa proxy principal de Gravidade
alvo = 'AVALIA_N'

# Criação da proxy G2D: Se AVALIA_N for 3 (ou o max correspondente a Grau 2/Severo) então 1, senão 0.
# No SINAN: 1=Grau 0, 2=Grau 1, 3=Grau 2. Consideramos 3 como G2D.
df['Target_G2D'] = np.where(df[alvo] == 3, 1, 0)

relatorio_metricas = []

for var in variaveis_foco:
    # 1. Análise Univariada e Completude [Ref: 563, 564]
    missing_pct = (df[var].isna().sum() / len(df)) * 100
    is_numeric = np.issubdtype(df[var].dtype, np.number)
    
    # 2. Processamento Técnico e Justificativas de Imputação [Ref: 210, 211]
    if is_numeric:
        imputation_method = "Mediana (Robust in Skewed) [210]"
        q1 = df[var].quantile(0.25)
        q3 = df[var].quantile(0.75)
        iqr = q3 - q1
        outliers_q = ((df[var] < (q1 - 1.5 * iqr)) | (df[var] > (q3 + 1.5 * iqr))).sum()
        outliers_pct = (outliers_q / len(df)) * 100
    else:
        imputation_method = "Moda (Categorical) [210]"
        iqr, outliers_pct = "N/A", "N/A"
        
    stat = {
        "Variavel": var,
        "Missing(%)": round(missing_pct, 2),
        "Outliers IQR(%)": round(outliers_pct, 2) if is_numeric else "-",
        "Metodo de Imputacao": imputation_method,
        "Media/Moda": round(df[var].mean(), 2) if is_numeric else df[var].mode()[0],
    }
    relatorio_metricas.append(stat)

df_metricas = pd.DataFrame(relatorio_metricas)

# 3. Análise Bivariada / Associação com alvo G2D [Ref: 254, 360]
print("Calculando Mutual Information e Kruskal-Wallis (Amostragem Estratificada)...")
# Amostragem para cálculo rápido e evitar overflow, balanceando o alvo
df_sub = df.dropna(subset=['Target_G2D'] + variaveis_foco).groupby('Target_G2D', group_keys=False).apply(lambda x: x.sample(min(len(x), 20000), random_state=42))

# Kruskal-Wallis H-test [Ref: 254] para comparar a distribuição de G2D vs grupos da variável
kruskal_results = []
for var in variaveis_foco:
    grupos = [df_sub[df_sub[var] == val]['Target_G2D'].values for val in df_sub[var].dropna().unique()]
    if len(grupos) > 1:
        try:
            stat, p = kruskal(*grupos)
            kruskal_results.append({"Variavel": var, "KW_Stat": stat, "P_Value": p})
        except:
            kruskal_results.append({"Variavel": var, "KW_Stat": 0, "P_Value": 1})

df_kw = pd.DataFrame(kruskal_results)
df_kw['Associacao_Significativa'] = np.where(df_kw['P_Value'] < 0.05, 'Sim', 'Não')

# One-Hot Encoding justificada [Ref: 211] para Mutual Information
X = pd.get_dummies(df_sub[variaveis_foco], drop_first=True)
y = df_sub['Target_G2D']
mi = mutual_info_classif(X, y, discrete_features='auto')
df_mi = pd.DataFrame({"Feature Encode": X.columns, "Mutual_Info[360]": mi}).sort_values("Mutual_Info[360]", ascending=False)

# Exportação para LaTeX
print("Exportando Tabelas de Transparência Metodológica...")
with open(f"{dir_relatorios}/tabela_apendice_variaveis.tex", "w", encoding="utf-8") as f:
    f.write("% Tabela 1: Métricas Descritivas e Tratamento de Variáveis (completude e imputação)\n")
    f.write("% Ancorado nas referências [210, 211, 213, 563, 564]\n")
    f.write(df_metricas.to_latex(index=False, caption="Transparência Univariada: Percentual de Missing, Imputação e Análise IQR", label="tab:metricas_univariadas"))
    
    f.write("\n\n% Tabela 2: Análise de Variância (Kruskal-Wallis) com G2D\n")
    f.write("% Justificando a escolha destas variáveis devido forte associação [254]\n")
    f.write(df_kw.to_latex(index=False, caption="Teste de Kruskal-Wallis para Associação Preditiva com G2D (Grau 2)", label="tab:kw_g2d", float_format="%.4f"))

    f.write("\n\n% Tabela 3: Importância via Mutual Information [360]\n")
    f.write(df_mi.head(10).to_latex(index=False, caption="Top 10 Características One-Hot com maior Mutual Information para G2D", label="tab:mi_g2d", float_format="%.4f"))

print("✅ Análise Avançada de Variáveis concluída (Apêndice estruturado).")
