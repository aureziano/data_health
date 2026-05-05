import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.metrics import classification_report, roc_auc_score, accuracy_score
import shap
import matplotlib.pyplot as plt
import os

# Configurações
dir_graficos = "./overleaf/fig"
dir_relatorios = "./overleaf/tabs"
os.makedirs(dir_graficos, exist_ok=True)
os.makedirs(dir_relatorios, exist_ok=True)

print("Carregando dados para modelagem avançada...")
df_X = pd.read_csv("./tratamento/dados_tratados.csv")
df_y = pd.read_csv("./tratamento/alvo_tratado.csv")

X = df_X
y = df_y.iloc[:, 0]  # Pegar a primeira coluna como Series

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

from imblearn.over_sampling import SMOTE
from collections import Counter

# 1. Tuning de Hiperparâmetros (LightGBM com SMOTE)
param_grid = {
    'n_estimators': [100, 200],
    'learning_rate': [0.05, 0.1],
    'num_leaves': [31, 64],
}

print("Iniciando Tuning de Hiperparâmetros (LightGBM + SMOTE)...")
# Amostragem para tuning
df_X_train = pd.DataFrame(X_train, index=X_train.index if hasattr(X_train, 'index') else range(len(X_train)))
X_train_sub = df_X_train.sample(n=min(10000, len(df_X_train)), random_state=42)
y_train_sub = y_train[X_train_sub.index]

# Verificar se há amostras suficientes para SMOTE
counts = Counter(y_train_sub)
min_samples = min(counts.values())
if min_samples > 1:
    k_neigh = min(5, min_samples - 1)
    smote = SMOTE(random_state=42, k_neighbors=k_neigh)
    X_res, y_res = smote.fit_resample(X_train_sub, y_train_sub)
else:
    print("Aviso: Amostras insuficientes para SMOTE. Prosseguindo sem SMOTE.")
    X_res, y_res = X_train_sub, y_train_sub

model = lgb.LGBMClassifier(random_state=42)
search = RandomizedSearchCV(model, param_grid, n_iter=2, cv=2, scoring='f1_weighted', random_state=42)
search.fit(X_res, y_res)

best_model = search.best_estimator_
print(f"Melhores parâmetros: {search.best_params_}")

# 2. Avaliação
y_pred = best_model.predict(X_test)
y_prob = best_model.predict_proba(X_test)

report = classification_report(y_test, y_pred, output_dict=True)
df_report = pd.DataFrame(report).transpose()

# 3. Explicabilidade (SHAP) - Versão Expandida
print("Gerando SHAP Values refinados...")
explainer = shap.TreeExplainer(best_model)
X_test_sub = X_test.sample(n=min(500, len(X_test)), random_state=42)
shap_values = explainer.shap_values(X_test_sub)

# Plot 1: SHAP Bar Plot (Importância Global)
plt.figure(figsize=(16, 10))
shap.summary_plot(shap_values, X_test_sub, plot_type="bar", show=False)
plt.title("Magnitude Global de Importância das Variáveis (SHAP Bar Plot)", fontsize=14)
plt.savefig(f"{dir_graficos}/shap_bar.png", dpi=300, bbox_inches='tight')
plt.close()

# Plot 2: SHAP Waterfall Plot (Explicabilidade Individual de um Caso de Alto Risco)
print("Gerando SHAP Waterfall Plot...")
# Usar TreeExplainer para LightGBM e converter para objeto Explanation
explainer_tree = shap.TreeExplainer(best_model)
# Obter SHAP values para o subset de teste
shap_values_test = explainer_tree(X_test_sub)

# Selecionar o caso com a MAIOR contribuição para a classe de risco (G2D)
# Em problemas multiclasse, shap_values tem dimensões (amostras, features, classes)
# Vamos focar na classe de maior interesse clínico se houver
if len(shap_values_test.shape) == 3:
    # Caso multiclasse: pegamos a classe com maior impacto (geralmente a última ou a média)
    # Aqui selecionamos o paciente com maior impacto SHAP absoluto total
    idx_caso = np.argmax(np.abs(shap_values_test.values[:, :, 0]).sum(1)) 
    sv_caso = shap_values_test[idx_caso, :, 0] # Foco na classe 0 (ou a que for de risco)
else:
    idx_caso = np.argmax(shap_values_test.values.sum(1))
    sv_caso = shap_values_test[idx_caso]

plt.figure(figsize=(12, 8))
plt.subplots_adjust(left=0.35, right=0.9, top=0.9, bottom=0.1)
shap.plots.waterfall(sv_caso, max_display=10, show=False)
plt.title(f"Decomposição de Decisão do Modelo: Caso de Maior Risco Identificado", fontsize=14, pad=20)
plt.savefig(f"{dir_graficos}/shap_waterfall.png", dpi=300, bbox_inches='tight')
plt.close()

# Plot 3: SHAP Bar Plot Global (Simples e Direto)
plt.figure(figsize=(12, 6))
shap.plots.bar(shap_values_test if len(shap_values_test.shape)==2 else shap_values_test[:,:,0], max_display=10, show=False)
plt.title("Ranking Global de Importância das Variáveis", fontsize=14)
plt.savefig(f"{dir_graficos}/shap_bar_global.png", dpi=300, bbox_inches='tight')
plt.close()

# 4. Exportação de Tabela SHAP (Novo)
print(f"Dimensões de X_test_sub: {X_test_sub.shape}")
print(f"Dimensões de shap_values: {np.shape(shap_values)}")
print("Calculando importância média SHAP...")

# Garantir que shap_values seja processado corretamente
if isinstance(shap_values, list):
    # Lista de (n_samples, n_features) -> Média sobre classes e amostras
    importancia_por_classe = [np.abs(sv).mean(0) for sv in shap_values]
    mean_shap = np.mean(importancia_por_classe, axis=0)
else:
    # Array (n_samples, n_features) ou (n_samples, n_features, n_classes)
    if len(shap_values.shape) == 3:
        # Caso (n_samples, n_features, n_classes) -> média sobre amostras (0) e classes (2)
        mean_shap = np.abs(shap_values).mean(axis=(0, 2))
    else:
        # Caso (n_samples, n_features)
        mean_shap = np.abs(shap_values).mean(0)

print(f"Dimensão final de mean_shap: {mean_shap.shape}")

# Criar DataFrame garantindo que os comprimentos coincidem
if len(mean_shap) == len(X_test_sub.columns):
    df_shap = pd.DataFrame({
        'Atributo': X_test_sub.columns,
        'Impacto_Medio_SHAP': mean_shap
    }).sort_values('Impacto_Medio_SHAP', ascending=False).head(10)
    
    # Escapar nomes para LaTeX
    df_shap['Atributo'] = df_shap['Atributo'].str.replace('_', '\\_')

    with open(f"{dir_relatorios}/tabela_importancia_shap.tex", "w", encoding="utf-8") as f:
        f.write(df_shap.to_latex(index=False, caption="Ranking de Importância das Variáveis (SHAP Values)", label="tab:shap_importance", float_format="%.4f", escape=False))
else:
    print(f"Erro Crítico: Comprimento de mean_shap ({len(mean_shap)}) não coincide com colunas ({len(X_test_sub.columns)})")
    # Fallback: tentar usar apenas os primeiros N elementos se houver discrepância por encoding interno
    n_feat = len(X_test_sub.columns)
    df_shap = pd.DataFrame({
        'Atributo': X_test_sub.columns,
        'Impacto_Medio_SHAP': mean_shap[:n_feat]
    }).sort_values('Impacto_Medio_SHAP', ascending=False).head(10)
    df_shap['Atributo'] = df_shap['Atributo'].str.replace('_', '\\_')
    with open(f"{dir_relatorios}/tabela_importancia_shap.tex", "w", encoding="utf-8") as f:
        f.write(df_shap.to_latex(index=False, caption="Ranking de Importância das Variáveis (SHAP Values)", label="tab:shap_importance", float_format="%.4f", escape=False))

# 5. Exportação para LaTeX (Saneada e Consolidada)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

with open(f"{dir_relatorios}/resultados_modelagem.tex", "w", encoding="utf-8") as f:
    f.write("% Tabela 1: Hiperparâmetros\n")
    f.write("\\begin{table}[H]\n\\centering\n")
    f.write("\\caption{Hiperparâmetros Ótimos Selecionados (LightGBM + SMOTE)}\n")
    f.write("\\label{tab:lgbm_params}\n")
    f.write("\\small\n")
    df_params = pd.DataFrame.from_dict(search.best_params_, orient='index', columns=['Valor'])
    f.write(df_params.to_latex())
    f.write("\\end{table}\n\n")
    
    f.write("% Tabela 2: Métricas\n")
    f.write("\\begin{table}[H]\n\\centering\n")
    f.write("\\caption{Métricas de Avaliação Detalhadas por Classe (LightGBM + SMOTE)}\n")
    f.write("\\label{tab:lgbm_metrics}\n")
    f.write("\\small\n")
    df_clean = df_report.drop(index=['accuracy'], errors='ignore')
    f.write(df_clean.to_latex(float_format="%.3f"))
    f.write("\\end{table}\n")

print(f"Modelagem concluída. Relatórios em {dir_relatorios}")
