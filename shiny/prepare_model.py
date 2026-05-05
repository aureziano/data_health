"""
Script de preparação para o Shiny App (Versão Revisada).
1. Treina e salva o modelo LightGBM para o preditor de risco (G2D).
2. Gera e salva os dados de séries temporais para o dashboard.
"""
import os
import sys
sys.path.append(os.getcwd())
import config
import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
import joblib
import config

def extrair_idade(valor):
    try:
        valor_str = str(int(float(valor))).zfill(4)
        unidade = int(valor_str[0])
        quantidade = int(valor_str[1:])
        if unidade == 4: return quantidade
        return 0
    except: return 0

def prepare():
    print("--- Iniciando Preparação de Modelos para Shiny (Refinado para G2D) ---")
    os.makedirs("shiny", exist_ok=True)

    # 1. Carregar Dados Brutos (Contém AVALIA_N e variáveis clínicas originais)
    path_data = str(config.PATHS['hanceniase'])
    if not os.path.exists(path_data):
        print(f"Erro: Arquivo {path_data} não encontrado.")
        return

    df_bruto = pd.read_csv(path_data, low_memory=False)
    
    # 2. Preparar Features e Target (G2D)
    # Lógica baseada em analise_incapacidade.py e Capítulo 5
    df_model = df_bruto[['NU_IDADE_N', 'AVALIA_N', 'NU_LESOES', 'NERVOSAFET', 'CLASSOPERA', 'CS_SEXO']].copy()
    
    # Conversões numéricas
    for col in ['NU_IDADE_N', 'AVALIA_N', 'NU_LESOES', 'NERVOSAFET']:
        df_model[col] = pd.to_numeric(df_model[col], errors='coerce')
    
    # Limpeza e Target (G2D == Grau 2)
    df_model = df_model.dropna(subset=['AVALIA_N'])
    y = (df_model['AVALIA_N'] == 2).astype(int)
    
    # Feature Engineering
    df_model['Idade'] = df_model['NU_IDADE_N'].apply(extrair_idade)
    df_model['Sexo_Masc'] = df_model['CS_SEXO'].map({'M': 1, 'F': 0, 1: 1, 0: 0, '1': 1, '0': 0}).fillna(0)
    df_model['Class_MB'] = df_model['CLASSOPERA'].map({'1': 0, '2': 1, 1: 0, 2: 1}).fillna(0)
    
    features = ['Idade', 'NU_LESOES', 'NERVOSAFET', 'Class_MB', 'Sexo_Masc']
    X = df_model[features].fillna(0)
    
    print(f"Treinando LightGBM para G2D com {len(X)} registros...")
    model = lgb.LGBMClassifier(n_estimators=100, learning_rate=0.05, random_state=42, verbose=-1)
    model.fit(X, y)
    
    # Salvar Modelo e Metadados
    joblib.dump({
        'model': model,
        'features': features,
        'feature_labels': {
            'Idade': 'Idade (Anos)',
            'NU_LESOES': 'Número de Lesões',
            'NERVOSAFET': 'Nervos Afetados',
            'Class_MB': 'Classificação Multibacilar (MB=1)',
            'Sexo_Masc': 'Sexo Masculino (Sim=1)'
        }
    }, "shiny/model_risk.joblib")
    print("✓ Modelo de Risco G2D salvo em shiny/model_risk.joblib")

    # 3. Preparar Dados do Dashboard (Gap Pandêmico)
    # Replicando a lógica de séries temporais da dissertação (SARIMA/Gap)
    df_bruto['DT_NOTIFIC'] = pd.to_datetime(df_bruto['DT_NOTIFIC'], errors='coerce')
    ts = df_bruto.dropna(subset=['DT_NOTIFIC']).set_index('DT_NOTIFIC').resample('M').size()
    ts = ts[ts.index >= '2019-01-01'] # Focar na janela da dissertação

    # Para o dashboard "Copia e Cola", vamos salvar uma versão agregada simplificada
    # que mostre o Gap Pandêmico real observado
    try:
        # Vamos usar o SARIMA simplificado para gerar o 'Esperado'
        from statsmodels.tsa.statespace.sarimax import SARIMAX
        
        train = ts[ts.index < '2020-03-01']
        model_s = SARIMAX(train, order=(1,1,1), seasonal_order=(1,1,1,12))
        res_s = model_s.fit(disp=False)
        forecast = res_s.forecast(steps=len(ts) - len(train))
        
        expected = pd.concat([train, forecast])
        
        df_dash = pd.DataFrame({
            'Data': ts.index,
            'Real': ts.values,
            'Esperado': expected.values
        })
        df_dash.to_csv("shiny/dashboard_data.csv", index=False)
        print("✓ Dados do Dashboard (gap real) salvos em shiny/dashboard_data.csv")
    except Exception as e:
        print(f"Erro ao gerar dashboard data: {e}")

if __name__ == "__main__":
    prepare()
