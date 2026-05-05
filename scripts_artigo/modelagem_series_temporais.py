import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_squared_error, mean_absolute_error
import os

# Configurações
dir_graficos = "./scripts_artigo/graficos/series_temporais"
dir_relatorios = "./scripts_artigo/relatorios"
os.makedirs(dir_graficos, exist_ok=True)
os.makedirs(dir_relatorios, exist_ok=True)

print("Carregando dados brutos para análise de séries temporais...")
caminho_arquivo = str(config.PATHS['hanceniase'])

try:
    df = pd.read_csv(caminho_arquivo, encoding="utf-8", low_memory=False)
except FileNotFoundError:
    print("Arquivo não encontrado.")
    exit()

# 1. Preparação da Série Temporal (Notificações Mensais)
df['DT_NOTIFIC'] = pd.to_datetime(df['DT_NOTIFIC'])
ts = df.set_index('DT_NOTIFIC').resample('M').size()

# Dividir em Pré-Pandemia (Treino) e Pandemia (Teste/Comparativo)
ts_treino = ts[ts.index < '2020-03-01']
ts_teste = ts[ts.index >= '2020-03-01']

from statsmodels.tsa.statespace.sarimax import SARIMAX

# 2. Modelagem SARIMA (Sazonal)
print("Treinando modelo SARIMA (5,1,0)x(1,1,1,12)...")
# Usamos SARIMA para capturar a sazonalidade anual da hanseníase
model_sarima = SARIMAX(ts_treino, order=(5,1,0), seasonal_order=(1,1,1,12))
model_sarima_fit = model_sarima.fit(disp=False)
pred_sarima = model_sarima_fit.forecast(steps=len(ts_teste))

# 3. Modelagem Holt-Winters
print("Treinando modelo Holt-Winters...")
model_hw = ExponentialSmoothing(ts_treino, trend='add', seasonal='add', seasonal_periods=12)
model_hw_fit = model_hw.fit()
pred_hw = model_hw_fit.forecast(steps=len(ts_teste))

# 4. Carregar resultados GRU (se disponíveis)
try:
    df_gru = pd.read_csv(f"{dir_relatorios}/predicoes_gru.csv")
    pred_gru = df_gru['GRU_Pred'].values
    has_gru = True
except:
    print("Aviso: Resultados GRU não encontrados. Execute modelagem_gru.py primeiro.")
    has_gru = False

# 5. Cálculo de Subnotificação
gap_sarima = pred_sarima.sum() - ts_teste.sum()
print(f"Subnotificação Estimada (SARIMA): {gap_sarima:.0f} casos")

# 6. Gráfico Real vs Predito (Melhorado)
plt.figure(figsize=(15, 8))
plt.plot(ts_treino, label='Observado (Histórico)', color='black', alpha=0.6)
plt.plot(ts_teste, label='Observado (Real Pandemia)', color='blue', linewidth=2)
plt.plot(ts_teste.index, pred_sarima, label='Predito (SARIMA - Cenário Sem Pandemia)', color='red', linestyle='--')
plt.plot(ts_teste.index, pred_hw, label='Predito (Holt-Winters)', color='green', linestyle=':')
if has_gru:
    plt.plot(ts_teste.index, pred_gru, label='Predito (Deep Learning GRU)', color='purple', linestyle='-.')

plt.axvline(pd.Timestamp('2020-03-01'), color='red', linestyle='-', alpha=0.3)
plt.fill_between(ts_teste.index, ts_teste, pred_sarima, color='red', alpha=0.1, label='Gap de Subnotificação')

plt.title("Vigilância de Precisão: Impacto da COVID-19 na Detecção de Hanseníase", fontsize=14)
plt.xlabel("Ano")
plt.ylabel("Nº de Notificações Mensais")
plt.legend(loc='upper left')
plt.grid(True, alpha=0.2)
plt.savefig(f"{dir_graficos}/comparativo_ts_pandemia.png", dpi=300, bbox_inches='tight')
plt.close()

# 7. Tabela comparativa de Métricas (Table 5.2)
modelos = ["SARIMA", "Holt-Winters"]
maes = [mean_absolute_error(ts_teste, pred_sarima), mean_absolute_error(ts_teste, pred_hw)]
rmses = [np.sqrt(mean_squared_error(ts_teste, pred_sarima)), np.sqrt(mean_squared_error(ts_teste, pred_hw))]
gaps = [gap_sarima, pred_hw.sum() - ts_teste.sum()]

if has_gru:
    modelos.append("GRU (Neural Network)")
    maes.append(mean_absolute_error(ts_teste, pred_gru))
    rmses.append(np.sqrt(mean_squared_error(ts_teste, pred_gru)))
    gaps.append(pred_gru.sum() - ts_teste.sum())

df_metricas = pd.DataFrame({
    "Modelo": modelos,
    "MAE": maes,
    "RMSE": rmses,
    "Subnotificação Estimada": gaps
})

with open(f"{dir_relatorios}/metricas_series_temporais.tex", "w", encoding="utf-8") as f:
    f.write("% Tabela de Comparação de Modelos de Séries Temporais (Full)\n")
    f.write(df_metricas.to_latex(index=False, caption="Avaliação Multimodelo de Forecasting e Estimativa de Subnotificação", label="tab:metricas_ts", float_format="%.2f"))

print(f"Análise de séries temporais concluída. Resultados salvos em {dir_relatorios}/metricas_series_temporais.tex")
