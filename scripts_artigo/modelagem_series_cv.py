import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings("ignore")

# Configurações
dir_relatorios = "./scripts_artigo/relatorios"
os.makedirs(dir_relatorios, exist_ok=True)

print("Iniciando Validação Cruzada por Janela Deslizante (Walk-forward)...")

# 1. Carregamento e Preparação
df = pd.read_csv(str(config.PATHS['hanceniase']), low_memory=False)
df['DT_NOTIFIC'] = pd.to_datetime(df['DT_NOTIFIC'])
ts = df.set_index('DT_NOTIFIC').resample('M').size()

# Usar apenas dados Pré-Pandemia para a Validação Cruzada (2012-2019)
ts_cv = ts[ts.index < '2020-01-01']

# Parâmetros do Sliding Window
n_train_init = 48  # 4 anos de dados iniciais
test_size = 12     # Prever os próximos 12 meses em cada passo
steps = 5          # Aumentando para 5 janelas (mais volume)

modelos_mae = {"SARIMA": [], "Holt-Winters": []}

for i in range(steps):
    train_end = n_train_init + (i * test_size)
    train = ts_cv.iloc[:train_end]
    test = ts_cv.iloc[train_end:train_end + test_size]
    
    if len(test) < test_size:
        break
        
    print(f"Janela {i+1}: Treinando até {train.index[-1].date()} | Testando {test.index[0].year}")
    
    # SARIMA
    model_sarima = SARIMAX(train, order=(5,1,0), seasonal_order=(1,1,1,12))
    res_sarima = model_sarima.fit(disp=False)
    pred_sarima = res_sarima.forecast(steps=len(test))
    modelos_mae["SARIMA"].append(mean_absolute_error(test, pred_sarima))
    
    # Holt-Winters
    model_hw = ExponentialSmoothing(train, trend='add', seasonal='add', seasonal_periods=12)
    res_hw = model_hw.fit()
    pred_hw = res_hw.forecast(steps=len(test))
    modelos_mae["Holt-Winters"].append(mean_absolute_error(test, pred_hw))

# Calcular Médias e Desvios
resultados_cv = []
for mod, maes in modelos_mae.items():
    resultados_cv.append({
        "Modelo": mod,
        "MAE_Médio": np.mean(maes),
        "MAE_STD": np.std(maes),
        "Vol_Meses": len(maes) * test_size
    })

df_cv = pd.DataFrame(resultados_cv)
print("\nResultados Finais CV:")
print(df_cv)

# Exportação LaTeX (Garantir fechamento do arquivo)
with open(f"{dir_relatorios}/validacao_cruzada_series.tex", "w", encoding="utf-8") as f:
    f.write("% Tabela de Validação Cruzada (Sliding Window)\n")
    f.write(df_cv.to_latex(index=False, caption="Resultados da Validação Cruzada Walk-forward (Volume de Experimentos)", label="tab:cv_series"))

print(f"Validação concluída. Relatório salvo em {dir_relatorios}/validacao_cruzada_series.tex")
