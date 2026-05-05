import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_selection import SelectKBest, f_classif, RFE, mutual_info_classif, SelectFromModel
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression, LassoCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config

# Configurações gerais
dir_analise = "./analise"
dir_graficos = "./graficos_analise"
dir_relatorios = "./relatorios_analise"
os.makedirs(dir_analise, exist_ok=True)
os.makedirs(dir_graficos, exist_ok=True)
os.makedirs(dir_relatorios, exist_ok=True)

print("Carregando dados tratados...")

# 1. Carregamento dos dados tratados
df_X = pd.read_csv("./tratamento/dados_tratados.csv")
df_y = pd.read_csv("./tratamento/alvo_tratado.csv")

print("Dados tratados carregados com sucesso.")

# 2. Carregamento dos dados brutos para obter colunas de data/hora
caminho_arquivo = str(config.PATHS['hanceniase'])
try:
    df_bruto = pd.read_csv(caminho_arquivo, encoding="utf-8", low_memory=False)
    print("Dados brutos carregados com sucesso.")
except FileNotFoundError:
    print(f"Arquivo {caminho_arquivo} não encontrado.")
    exit()

# 3. Seleção de variáveis relevantes
# CORREÇÃO: Removido TPALTA_N das features (DATA LEAKAGE)
# Target correto: AVAL_ATU_N (Grau de Incapacidade Física - G2D)
variaveis_preditoras = [
    'CLASSOPERA', 'BACILOSCOP', 'ESQ_INI_N', 'CONTREG', 'NERVOSAFET', 'ESQ_ATU_N',
    'DOSE_RECEB', 'CONTEXAM', 'CS_SEXO', 'CS_RACA', 'CS_ESCOL_N',
    'NU_ANO'
]
variaveis_alvo = ['AVAL_ATU_N']  # Grau de Incapacidade Física (G2D)

# 4. Remover linhas com missing no alvo
df_bruto = df_bruto.dropna(subset=variaveis_alvo + variaveis_preditoras)
print("Linhas com missing removidas.")

# 5. Preparação dos dados
X = df_X.values
y = df_y.values.ravel()
print("Dados preparados para análise.")

# 6. Ensemble Feature Selection
# a) RFE com Random Forest
print("Aplicando RFE com Random Forest...")
estimator = RandomForestClassifier(n_estimators=100, random_state=42)
selector = RFE(estimator, n_features_to_select=10)
selector.fit(X, y)
selected_features = df_X.columns[selector.support_].tolist()
print("RFE concluído.")

# b) Seleção por f_classif (univariate)
print("Aplicando seleção univariada (f_classif)...")
selector_uni = SelectKBest(f_classif, k=10)
selector_uni.fit(X, y)
selected_features_uni = df_X.columns[selector_uni.get_support()].tolist()
print("Seleção univariada concluída.")

# c) Mutual Information (Captura relações não lineares)
print("Aplicando Mutual Information...")
selector_mi = SelectKBest(mutual_info_classif, k=10)
selector_mi.fit(X, y)
selected_features_mi = df_X.columns[selector_mi.get_support()].tolist()

# d) LASSO (Regularização L1)
print("Aplicando LASSO para Feature Selection (Regularização em Saúde)...")
lasso = LogisticRegression(penalty='l1', solver='liblinear', C=0.1, random_state=42)
selector_lasso = SelectFromModel(lasso)
selector_lasso.fit(X, y)
selected_features_lasso = df_X.columns[selector_lasso.get_support()].tolist()

# 7. Relatório de seleção
with open(f"{dir_relatorios}/selecao_features_dissertacao.txt", "w", encoding="utf-8") as f:
    f.write("RELATÓRIO DE AVALIAÇÃO DE FEATURES PARA DISSERTAÇÃO DE MESTRADO\n")
    f.write("===============================================================\n\n")
    f.write("A seleção de atributos desempenha papel crucial preditivo em prontuários eletrônicos de saúde.\n")
    f.write("Features selecionadas por RFE (Random Forest) - (Modelagem Não-Linear Robusta):\n")
    f.write("\n".join(selected_features))
    f.write("\n\nFeatures selecionadas por f_classif (Teste Estatístico Linear ANOVA):\n")
    f.write("\n".join(selected_features_uni))
    f.write("\n\nFeatures selecionadas por Mutual Information (Captura dependência não-linear complexa - ref: Vergara et al. 2014):\n")
    f.write("\n".join(selected_features_mi))
    f.write("\n\nFeatures selecionadas por LASSO / L1 (Redução de Coeficientes Esparsos para explicabilidade clínica - ref: Tibshirani 1996):\n")
    f.write("\n".join(selected_features_lasso))

print("Relatório de seleção de features expandido para dissertação salvo.")

# 8. Propensity Score Matching (PSM) - para subpopulações
# Exemplo: comparar pacientes pré e durante pandemia
print("Calculando propensity score...")
df_bruto['ano_notificacao'] = pd.to_datetime(df_bruto['DT_NOTIFIC']).dt.year
df_bruto['grupo'] = (df_bruto['ano_notificacao'] >= 2020).astype(int)

# PSM simples: regressão logística para estimar propensity score
X_psm = df_X.values
y_psm = df_bruto['grupo'].values

# Escalonar os dados para a regressão logística
scaler = StandardScaler()
X_psm_scaled = scaler.fit_transform(X_psm)

model_psm = LogisticRegression(max_iter=1000)
model_psm.fit(X_psm_scaled, y_psm)
propensity_scores = model_psm.predict_proba(X_psm_scaled)[:, 1]

df_bruto['propensity_score'] = propensity_scores
print("Propensity score calculado.")

# 9. Gráficos comparativos
print("Gerando gráfico de propensity score...")
plt.figure(figsize=(12, 6))
sns.histplot(df_bruto, x='propensity_score', hue='grupo', bins=50)
plt.title("Propensity Score Distribution (pré vs durante pandemia)")
plt.savefig(f"{dir_graficos}/propensity_score.png", bbox_inches='tight')
plt.close()
print("Gráfico de propensity score salvo.")

# 10. Relatório de técnicas
with open(f"{dir_relatorios}/tecnicas_aplicadas.txt", "w", encoding="utf-8") as f:
    f.write("Técnicas aplicadas:\n")
    f.write("- Ensemble Feature Selection: RFE (Random Forest) e f_classif (univariate)\n")
    f.write("- Propensity Score Matching: regressão logística para estimar propensity score\n")
    f.write("- Referências:\n")
    f.write("  - Ensemble Feature Selection: Saeys et al. (2007), Abeel et al. (2010), Song et al. (2018)\n")
    f.write("  - Propensity Score Matching: Rosenbaum & Rubin (1983), Stürmer et al. (2005)\n")

print("Relatório de técnicas salvo.")

print("Análise e modelagem concluída. Gráficos e relatórios salvos em ./graficos_analise e ./relatorios_analise.")
