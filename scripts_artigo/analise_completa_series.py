import os
import config
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from prophet import Prophet
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings("ignore")

# Configurações
dir_graficos = "./overleaf/fig"
dir_relatorios = "./overleaf/tabs"
os.makedirs(dir_graficos, exist_ok=True)
os.makedirs(dir_relatorios, exist_ok=True)

# Marcos Temporais (Validados via OMS e MS)
START_PANDEMIA = '2020-03-11' # OMS declara Pandemia
END_ESPIN_BR = '2022-04-22'   # Brasil Portaria 913 (Fim da ESPIN)
END_PHEIC_WHO = '2023-05-05'  # OMS declara fim da emergência internacional

print("Iniciando Análise Multimodelo de Séries Temporais...")

# 1. Carregamento e Preparação
df = pd.read_csv(str(config.PATHS['hanceniase']), low_memory=False)
df['DT_NOTIFIC'] = pd.to_datetime(df['DT_NOTIFIC'])
ts = df.set_index('DT_NOTIFIC').resample('M').size()

# Filtrar para período de interesse (2012-2024) para evitar ruído de dados muito antigos
ts = ts[ts.index >= '2012-01-01']

# Dados de Treino (Pré-Pandemia)
ts_train = ts[ts.index < '2020-03-01']
# Dados de Teste (Durante e Pós Pandemia)
ts_test = ts[ts.index >= '2020-03-01']

# --- DEFINIÇÃO DOS MODELOS ---

# 1. Naive (Sazonal: Repete o ano anterior)
last_year = ts_train[-12:]
pred_naive = np.tile(last_year.values, (len(ts_test) // 12) + 1)[:len(ts_test)]
pred_naive = pd.Series(pred_naive, index=ts_test.index)

# 2. SARIMA (5,1,0)x(1,1,1,12)
model_sarima = SARIMAX(ts_train, order=(5,1,0), seasonal_order=(1,1,1,12))
res_sarima = model_sarima.fit(disp=False)
pred_sarima = res_sarima.forecast(steps=len(ts_test))

# 3. Holt-Winters
model_hw = ExponentialSmoothing(ts_train, trend='add', seasonal='add', seasonal_periods=12)
res_hw = model_hw.fit()
pred_hw = res_hw.forecast(steps=len(ts_test))

# 4. Prophet
df_prophet = ts_train.reset_index().rename(columns={'DT_NOTIFIC': 'ds', 0: 'y'})
m = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
m.fit(df_prophet)
future = m.make_future_dataframe(periods=len(ts_test), freq='M')
pred_prophet_full = m.predict(future)
pred_prophet = pred_prophet_full.tail(len(ts_test))['yhat'].values
pred_prophet = pd.Series(pred_prophet, index=ts_test.index)

# 5. XGBoost (com Lags)
def create_features(series, lags=[1, 12]):
    df_feat = pd.DataFrame(series)
    df_feat.columns = ['y']
    for lag in lags:
        df_feat[f'lag_{lag}'] = df_feat['y'].shift(lag)
    df_feat['month'] = df_feat.index.month
    return df_feat.dropna()

train_feat = create_features(ts_train)
X_train = train_feat.drop('y', axis=1)
y_train = train_feat['y']

model_xgb = xgb.XGBRegressor(n_estimators=100, learning_rate=0.05)
model_xgb.fit(X_train, y_train)

# Predição recursiva simplificada (apenas para o gap)
X_test_init = create_features(ts).tail(len(ts_test)).drop('y', axis=1)
pred_xgb = model_xgb.predict(X_test_init)
pred_xgb = pd.Series(pred_xgb, index=ts_test.index)

# --- MÉTRICAS ---

def get_metrics(real, pred):
    mae = mean_absolute_error(real, pred)
    rmse = np.sqrt(mean_squared_error(real, pred))
    mape = np.mean(np.abs((real - pred) / real)) * 100
    return mae, rmse, mape

modelos = {
    "Naive Seasonal": pred_naive,
    "SARIMA": pred_sarima,
    "Holt-Winters": pred_hw,
    "Prophet": pred_prophet,
    "XGBoost": pred_xgb
}

results = []
for name, pred in modelos.items():
    # Período Pandêmico Estrito (Mar 2020 - Abr 2022)
    mask_pandemia = (ts_test.index >= '2020-03-01') & (ts_test.index <= END_ESPIN_BR)
    # Período de Recuperação/Backlog (Mai 2022 - Dez 2024)
    mask_recup = (ts_test.index > END_ESPIN_BR)
    
    real_pand = ts_test[mask_pandemia]
    pred_pand = pred[mask_pandemia]
    gap_pand = pred_pand.sum() - real_pand.sum()
    
    real_recup = ts_test[mask_recup]
    pred_recup = pred[mask_recup]
    gap_recup = pred_recup.sum() - real_recup.sum() # Se Negativo, significa casos ACIMA do esperado (Backlog)
    
    # Período Total (2020-2024)
    mae, rmse, mape = get_metrics(ts_test, pred)
    gap_total = pred.sum() - ts_test.sum()
    
    results.append({
        "Modelo": name,
        "Gap Pandemia (Num)": int(gap_pand),
        "Gap Recuperação (Num)": int(gap_recup),
        "Gap Total (2020-2024)": int(gap_total),
        "MAE (Validação)": mae
    })

df_results = pd.DataFrame(results)
print("\nComparativo de Modelos (Impacto Pandêmico vs Total):")
print(df_results)

# Exportar Tabela 5.3 Expandida
with open(f"{dir_relatorios}/tabela_comparativo_modelos_full.tex", "w", encoding="utf-8") as f:
    f.write(df_results.to_latex(index=False, caption="Comparativo de Acurácia e Estimativa de Subnotificação (2020-2024)", label="tab:metricas_full", float_format="%.2f"))

# --- GRÁFICOS ---

# Gráfico 1: Design do Estudo (Timeline 2012-2024)
plt.figure(figsize=(15, 6))
plt.plot(ts, color='gray', alpha=0.5, label='Série Histórica Total')
plt.axvline(pd.to_datetime(START_PANDEMIA), color='red', linestyle='--', label='Início Pandemia (OMS)')
plt.axvline(pd.to_datetime(END_ESPIN_BR), color='blue', linestyle='-.', label='Fim ESPIN (Brasil)')
plt.axvline(pd.to_datetime(END_PHEIC_WHO), color='green', linestyle=':', label='Fim Emergência (OMS)')
plt.title("Figura 3.1: Design do Estudo - Linha do Tempo e Marcos Pandêmicos", fontsize=12)
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig(f"{dir_graficos}/design_estudo_timeline.png", dpi=300, bbox_inches='tight')

# Gráfico 2: Projeções Focadas (2019-2024)
plt.figure(figsize=(15, 8))
focal_start = '2019-01-01'
mask_pandemia = (ts_test.index >= '2020-03-01') & (ts_test.index <= END_ESPIN_BR)
mask_recup = (ts_test.index > END_ESPIN_BR)

plt.plot(ts[ts.index >= focal_start], color='black', label='Observado (Real)', linewidth=2)
plt.plot(pred_sarima[pred_sarima.index >= focal_start], label='SARIMA', linestyle='--', alpha=0.8)
plt.plot(pred_prophet[pred_prophet.index >= focal_start], label='Prophet', linestyle='-.', alpha=0.8)
plt.plot(pred_xgb[pred_xgb.index >= focal_start], label='XGBoost', linestyle=':', alpha=0.8)

plt.axvspan(pd.to_datetime('2020-03-01'), pd.to_datetime(END_ESPIN_BR), color='red', alpha=0.05, label='Período Pandêmico')
plt.axvspan(pd.to_datetime(END_ESPIN_BR), ts.index[-1], color='cyan', alpha=0.05, label='Fase de Recuperação (Backlog)')

# Sombreamento dos Gaps
# Gap Pandemia (Geralmente Subnotificação)
plt.fill_between(ts_test.index[mask_pandemia], ts_test[mask_pandemia], pred_sarima[mask_pandemia], 
                 where=(pred_sarima[mask_pandemia] >= ts_test[mask_pandemia]), color='red', alpha=0.2, label='Subnotificação (Gap -)')

# Gap Recuperação (Pode ser Positivo ou Negativo)
plt.fill_between(ts_test.index[mask_recup], ts_test[mask_recup], pred_sarima[mask_recup], 
                 where=(ts_test[mask_recup] >= pred_sarima[mask_recup]), color='green', alpha=0.3, label='Reabsorção (Gap +)')
plt.fill_between(ts_test.index[mask_recup], ts_test[mask_recup], pred_sarima[mask_recup], 
                 where=(ts_test[mask_recup] < pred_sarima[mask_recup]), color='red', alpha=0.1)

plt.xlim(pd.to_datetime(focal_start), ts.index[-1])
plt.title("Figura 5.2: Dinâmica de Gaps Epidemiológicos - Subnotificação vs. Recuperação do Backlog", fontsize=14)
# Mover legenda para fora da área crítica dos dados (inferior esquerdo)
plt.legend(loc='lower left', fontsize=10, frameon=True, framealpha=0.9)
plt.grid(True, alpha=0.2)
plt.savefig(f"{dir_graficos}/comparativo_focado_ts.png", dpi=300, bbox_inches='tight')

print("Análise concluída. Gráficos e tabelas gerados.")
