import os
import sys
import pandas as pd
import numpy as np
import lightgbm as lgb
import joblib
from statsmodels.tsa.statespace.sarimax import SARIMAX

# Garantir que o diretório raiz está no path para importar config
sys.path.append(os.getcwd())
try:
    import config
except ImportError:
    # Fallback caso rode de dentro do diretório shiny
    sys.path.append("..")
    import config

def extrair_idade(valor):
    try:
        valor_str = str(int(float(valor))).zfill(4)
        unidade = int(valor_str[0])
        quantidade = int(valor_str[1:])
        if unidade == 4: return quantidade
        return 0
    except: return 0

def prepare_shiny_data():
    print("🚀 Iniciando Consolidação de Dados para Shiny Dashboard...")
    os.makedirs("shiny", exist_ok=True)

    # 1. Carregamento de Dados
    path_data = str(config.PATHS['hanceniase'])
    if not os.path.exists(path_data):
        print(f"❌ Erro: Arquivo {path_data} não encontrado.")
        return

    df = pd.read_csv(path_data, low_memory=False)
    
    # 2. Preparação do Modelo de Risco (G2D)
    print("🧠 Treinando Modelo LightGBM para Calculadora de Risco...")
    
    # Colunas necessárias
    cols_needed = ['NU_IDADE_N', 'AVALIA_N', 'NU_LESOES', 'NERVOSAFET', 'CLASSOPERA', 'CS_SEXO', 'DOSE_RECEB']
    df_model = df[cols_needed].copy()
    
    # Conversões e Limpeza
    for col in ['NU_IDADE_N', 'AVALIA_N', 'NU_LESOES', 'NERVOSAFET', 'DOSE_RECEB']:
        df_model[col] = pd.to_numeric(df_model[col], errors='coerce')
    
    df_model = df_model.dropna(subset=['AVALIA_N'])
    
    # FIX: G2D é Grau 2, que no SINAN é codificado como 3
    # 1=Grau 0, 2=Grau 1, 3=Grau 2
    y = (df_model['AVALIA_N'] == 3).astype(int)
    
    # Feature Engineering
    df_model['Idade'] = df_model['NU_IDADE_N'].apply(extrair_idade)
    df_model['Sexo_Masc'] = df_model['CS_SEXO'].map({'M': 1, 'F': 0, '1': 1, '0': 0, 1: 1, 0: 0}).fillna(0)
    df_model['Class_MB'] = df_model['CLASSOPERA'].map({'1': 0, '2': 1, 1: 0, 2: 1}).fillna(0)
    
    features = ['Idade', 'NU_LESOES', 'NERVOSAFET', 'Class_MB', 'Sexo_Masc', 'DOSE_RECEB']
    X = df_model[features].fillna(0)
    
    # Treino de Múltiplos Modelos para Comparação
    print("🤖 Treinando Modelos (LGBM, RF, XGB) para G2D...")
    from sklearn.ensemble import RandomForestClassifier
    import xgboost as xgb

    # LightGBM (Gradient Boosting)
    model_lgbm = lgb.LGBMClassifier(n_estimators=200, learning_rate=0.03, random_state=42, verbose=-1, importance_type='gain', class_weight='balanced')
    model_lgbm.fit(X, y)
    
    # Random Forest (Bagging)
    model_rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1, class_weight='balanced')
    model_rf.fit(X, y)
    
    # XGBoost (Gradient Boosting)
    # XGB usa scale_pos_weight em vez de class_weight='balanced'
    scale_pos_weight = (len(y) - sum(y)) / sum(y)
    model_xgb = xgb.XGBClassifier(n_estimators=100, learning_rate=0.05, random_state=42, use_label_encoder=False, eval_metric='logloss', scale_pos_weight=scale_pos_weight)
    model_xgb.fit(X, y)
    
    # Exportar Bundle de Modelos
    joblib.dump({
        'models': {
            'lgbm': model_lgbm,
            'rf': model_rf,
            'xgb': model_xgb
        },
        'features': features,
        'feature_labels': {
            'Idade': 'Idade (Anos)',
            'NU_LESOES': 'Número de Lesões',
            'NERVOSAFET': 'Nervos Afetados',
            'Class_MB': 'Classificação Multibacilar (MB=1)',
            'Sexo_Masc': 'Sexo Masculino (Sim=1)',
            'DOSE_RECEB': 'Doses Recebidas'
        }
    }, "shiny/model_risk.joblib")
    print("✅ Modelos de Risco (G2D) salvos em shiny/model_risk.joblib")

    # 3. Preparação das Séries Temporais (2012-2024)
    print("📈 Processando Séries Temporais (Histórica + Pandemia)...")
    df['DT_NOTIFIC'] = pd.to_datetime(df['DT_NOTIFIC'], errors='coerce')
    ts = df.dropna(subset=['DT_NOTIFIC']).set_index('DT_NOTIFIC').resample('ME').size()
    ts = ts[ts.index >= '2012-01-01']
    
    # Gerar Cenário Contra-factual (SARIMA) baseado no pré-pandemia
    train = ts[ts.index < '2020-03-01']
    try:
        model_s = SARIMAX(train, order=(1,1,1), seasonal_order=(1,1,1,12))
        res_s = model_s.fit(disp=False)
        forecast = res_s.forecast(steps=len(ts) - len(train))
        expected = pd.concat([train, forecast])
        
        df_dash = pd.DataFrame({
            'Data': ts.index,
            'Real': ts.values,
            'Esperado': expected.values
        })
        
        # Adicionar coluna de Fase
        df_dash['Fase'] = 'Histórico'
        df_dash.loc[df_dash['Data'] >= '2020-03-01', 'Fase'] = 'Pandemia'
        df_dash.loc[df_dash['Data'] > '2022-04-22', 'Fase'] = 'Recuperação'
        
        df_dash.to_csv("shiny/dashboard_data.csv", index=False)
        print("✅ Dados do Dashboard salvos em shiny/dashboard_data.csv")
    except Exception as e:
        print(f"⚠️ Erro ao gerar SARIMA: {e}. Salvando apenas dados reais.")
        df_dash = pd.DataFrame({'Data': ts.index, 'Real': ts.values})
        df_dash.to_csv("shiny/dashboard_data.csv", index=False)

    # 4. Copiar Imagens da Dissertação para uma pasta local (www) para o Shiny
    print("🖼️ Copiando imagens da dissertação para o dashboard...")
    www_dir = "shiny/www"
    os.makedirs(www_dir, exist_ok=True)
    
    import shutil
    fig_names = [
        "comparativo_projecoes.png", "analise_silhueta_k2_k3.png", "importancia_features_clusters.png",
        "shap_beeswarm.png", "shap_waterfall.png", "shap_bar_global.png",
        "mapa_microrregioes_v3.png", "painel_socio_clinico.png", "paradoxo_gravidade_stacked.png"
    ]
    
    # Procurar em overleaf/fig e overleaf/fig/incapacidade
    source_dirs = ["overleaf/fig", "overleaf/fig/incapacidade"]
    
    for fig in fig_names:
        found = False
        for sdir in source_dirs:
            src = os.path.join(sdir, fig)
            if os.path.exists(src):
                shutil.copy(src, os.path.join(www_dir, fig))
                found = True
                break
        if not found:
            print(f"⚠️ Aviso: Imagem {fig} não encontrada.")

    # 5. Gerar Dados Dinâmicos Adicionais (Clustering, SHAP, Socio-Clínicos)
    print("🔄 Chamando prepare_dynamic_data para assets dinâmicos...")
    try:
        from shiny.prepare_dynamic_data import prepare_dynamic_data
    except ImportError:
        from prepare_dynamic_data import prepare_dynamic_data
    
    prepare_dynamic_data()

    print("✨ Preparação concluída com sucesso!")

if __name__ == "__main__":
    prepare_shiny_data()
