"""
Geração do SHAP Beeswarm Summary Plot para Capítulo 5
Complementa o Waterfall Plot com visão da distribuição global de impacto.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shap
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE
import os, warnings
warnings.filterwarnings('ignore')

dir_graficos = "./overleaf/fig"
os.makedirs(dir_graficos, exist_ok=True)

def gerar_beeswarm():
    print("--- Gerando SHAP Beeswarm Summary Plot ---")

    # 1. Carregar dados tratados
    try:
        df = pd.read_csv("./tratamento/dados_tratados.csv")
    except FileNotFoundError:
        print("ERRO: dados_tratados.csv não encontrado. Tentando dados brutos...")
        import config
        df = pd.read_csv(config.PATHS['hanceniase'], low_memory=False)
        df = df.dropna(subset=['AVALIA_N'])

    # 2. Preparar alvo G2D
    if 'AVALIA_N' in df.columns:
        target_col = 'AVALIA_N'
        df[target_col] = pd.to_numeric(df[target_col], errors='coerce')
        df = df.dropna(subset=[target_col])
        y = (df[target_col] == 2).astype(int)
    else:
        # Tentar coluna alternativa
        available = [c for c in df.columns if 'target' in c.lower() or 'g2' in c.lower()]
        if not available:
            print("AVISO: Usando primeira coluna numérica como target.")
            target_col = df.select_dtypes(include=np.number).columns[0]
            y = df[target_col]
        else:
            target_col = available[0]
            y = df[target_col]

    X = df.drop(columns=[target_col], errors='ignore')

    # 3. Manter apenas numéricas + encoding categóricas simples
    for col in X.select_dtypes(include='object').columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
    X = X.select_dtypes(include=[np.number]).fillna(0)

    # 4. Split com corte temporal (sem shuffle) — anti-leakage
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    # 5. SMOTE apenas no treino
    print(f"Balanceamento SMOTE — antes: {y_train.value_counts().to_dict()}")
    sm = SMOTE(random_state=42, k_neighbors=3)
    X_res, y_res = sm.fit_resample(X_train, y_train)
    print(f"Balanceamento SMOTE — depois: {pd.Series(y_res).value_counts().to_dict()}")

    # 6. Treinar LightGBM
    print("Treinando LightGBM...")
    model = lgb.LGBMClassifier(n_estimators=300, learning_rate=0.05,
                                num_leaves=31, random_state=42, verbose=-1)
    model.fit(X_res, y_res)

    # 7. Calcular SHAP Values
    print("Calculando SHAP Values...")
    sample_size = min(2000, len(X_test))
    X_sample = X_test.sample(n=sample_size, random_state=42)

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)

    # Para classificação binária, shap_values é lista [neg, pos]
    sv = shap_values[1] if isinstance(shap_values, list) else shap_values

    # 8. Beeswarm Summary Plot
    print("Gerando Beeswarm Summary Plot...")
    plt.figure(figsize=(10, 8))
    shap.summary_plot(
        sv,
        X_sample,
        plot_type="dot",
        max_display=12,
        show=False,
        plot_size=None
    )
    plt.title("Distribuição do Impacto das Variáveis (SHAP Beeswarm)\nModelo LightGBM — Predição de Grau 2 de Incapacidade Física",
              fontsize=12, pad=25)
    plt.xlabel("Valor SHAP (Impacto na Predição de G2D)", fontsize=11)
    # Aumentando o espaço do topo para o título longo e para evitar sobreposição nos eixos:
    plt.tight_layout(rect=[0, 0, 1, 0.92]) 
    plt.savefig(f"{dir_graficos}/shap_beeswarm.png", dpi=300, bbox_inches='tight')
    plt.close()

    # 9. Bar Plot (Global Importance)
    print("Gerando SHAP Bar Plot...")
    plt.figure(figsize=(10, 6))
    shap.plots.bar(explainer(X_sample)[:,:,1] if len(explainer(X_sample).shape) > 2 else explainer(X_sample), show=False)
    plt.savefig(f"{dir_graficos}/shap_bar_global.png", dpi=300, bbox_inches='tight')
    plt.close()

    # 10. Waterfall Plot (Individual Case)
    print("Gerando SHAP Waterfall Plot...")
    # Pega um caso de alto risco (y_pred alto)
    y_prob = model.predict_proba(X_sample)[:, 1]
    idx_alto_risco = np.argmax(y_prob)
    
    # Recalcula SHAP para o caso específico usando o explainer correto para waterfall
    # (Para waterfall precisamos do objeto Explanation)
    explanation = explainer(X_sample)
    if len(explanation.shape) > 2: # Se for multiclasse/binário com 2 saídas
        explanation = explanation[:,:,1]

    plt.figure(figsize=(12, 6))
    shap.plots.waterfall(explanation[idx_alto_risco], show=False)
    plt.savefig(f"{dir_graficos}/shap_waterfall.png", dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✓ Gráficos SHAP (Beeswarm, Bar, Waterfall) salvos em {dir_graficos}/")

if __name__ == "__main__":
    gerar_beeswarm()
