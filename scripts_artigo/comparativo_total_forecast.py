import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from prophet import Prophet
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings("ignore")

# Configurações
DIR_RELATORIOS = "./overleaf/tabs"
DIR_GRAFICOS = "./overleaf/fig"
os.makedirs(DIR_RELATORIOS, exist_ok=True)

def main():
    print("Iniciando Comparativo Multi-Modelo de Forecasting...")
    
    # 1. Preparação dos Dados
    df = pd.read_csv(str(config.PATHS['hanceniase']), low_memory=False)
    df['DT_NOTIFIC'] = pd.to_datetime(df['DT_NOTIFIC'])
    ts = df.set_index('DT_NOTIFIC').resample('M').size()
    
    # Divisão Treino (até 2019) e Teste (Pandemia 2020-2022)
    train = ts[ts.index < '2020-01-01']
    test = ts[(ts.index >= '2020-01-01') & (ts.index <= '2022-12-31')]
    
    previsoes = pd.DataFrame(index=test.index)
    previsoes['Real'] = test.values
    
    # 2. Modelagem
    
    # 2.1 Naive Baseline (Sazonal)
    print("Rodando Naive Baseline...")
    previsoes['Naive'] = ts.shift(12)[test.index].values
    
    # 2.2 SARIMA (Ajustado)
    print("Rodando SARIMA...")
    model_sarima = SARIMAX(train, order=(1,1,1), seasonal_order=(1,1,1,12))
    res_sarima = model_sarima.fit(disp=False)
    previsoes['SARIMA'] = res_sarima.forecast(steps=len(test)).values
    
    # 2.3 Holt-Winters
    print("Rodando Holt-Winters...")
    model_hw = ExponentialSmoothing(train, trend='add', seasonal='add', seasonal_periods=12)
    res_hw = model_hw.fit()
    previsoes['Holt-Winters'] = res_hw.forecast(steps=len(test)).values
    
    # 2.4 Prophet
    print("Rodando Prophet...")
    df_prophet = train.reset_index().rename(columns={'DT_NOTIFIC': 'ds', 0: 'y'})
    m = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
    m.fit(df_prophet)
    future = m.make_future_dataframe(periods=len(test), freq='M')
    forecast = m.predict(future)
    previsoes['Prophet'] = forecast.set_index('ds')['yhat'][test.index].values
    
    # 2.5 XGBoost (Sliding Window)
    print("Rodando XGBoost...")
    def create_features(series):
        df_feat = pd.DataFrame(series)
        df_feat.columns = ['y']
        for i in range(1, 13):
            df_feat[f'lag_{i}'] = df_feat['y'].shift(i)
        return df_feat.dropna()
    
    X_train_df = create_features(ts[ts.index < '2020-01-01'])
    X_train, y_train = X_train_df.drop('y', axis=1), X_train_df['y']
    
    xgb = XGBRegressor(n_estimators=100, learning_rate=0.05)
    xgb.fit(X_train, y_train)
    
    # Previsão iterativa para XGBoost
    curr_data = list(ts[ts.index < '2020-01-01'].values[-12:])
    xgb_preds = []
    for _ in range(len(test)):
        pred = xgb.predict(np.array(curr_data).reshape(1, -1))[0]
        xgb_preds.append(pred)
        curr_data.pop(0)
        curr_data.append(pred)
    previsoes['XGBoost'] = xgb_preds

    # 3. Métricas
    metrics = []
    for model in ['Naive', 'SARIMA', 'Holt-Winters', 'Prophet', 'XGBoost']:
        mae = mean_absolute_error(test, previsoes[model])
        rmse = np.sqrt(mean_squared_error(test, previsoes[model]))
        metrics.append({"Modelo": model, "MAE": mae, "RMSE": rmse})
        
    df_metrics = pd.DataFrame(metrics).sort_values("MAE")
    
    # Exportar Tabelas
    with open(f"{DIR_RELATORIOS}/tabela_comparativo_modelos.tex", "w") as f:
        f.write(df_metrics.to_latex(index=False, float_format="%.2f", 
                caption="Acurácia de Previsão por Modelo (Testset Pandemia - 2020-2022)", label="tab:comparativo_all"))
        
    # 4. Gráfico de Comparatitvo Total
    plt.figure(figsize=(15, 8))
    plt.plot(ts[ts.index > '2017-01-01'], label='Histórico Real', color='black', linewidth=2)
    plt.plot(previsoes['SARIMA'], label='SARIMA', linestyle='--')
    plt.plot(previsoes['Holt-Winters'], label='Holt-Winters', linestyle='--')
    plt.plot(previsoes['Prophet'], label='Prophet', linestyle='-', linewidth=2)
    plt.plot(previsoes['XGBoost'], label='XGBoost', linestyle='-.')
    plt.plot(previsoes['Naive'], label='Naive Baseline (Sazonal)', color='gray', alpha=0.5)
    
    plt.axvline(pd.Timestamp("2020-03-01"), color='red', linestyle=':', label='Início da Pandemia')
    plt.title("Grande Comparativo de Forecasting: Detecção de Hanseníase vs Cenários Contra-factuais")
    plt.ylabel("Notificações Mensais")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.savefig(f"{DIR_GRAFICOS}/comparativo_forecast_completo.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Comparativo multi-modelo concluído.")

if __name__ == "__main__":
    main()
