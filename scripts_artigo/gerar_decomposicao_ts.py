import os
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
import config
import matplotlib.dates as mdates

def main():
    print("Gerando grafico de decomposicao sazonal para o Apendice C...")
    path_data = str(config.PATHS['hanceniase'])
    df = pd.read_csv(path_data, encoding='utf-8', low_memory=False)
    
    # Processar Data de Diagnostico e criar agregacao mensal
    df['DT_DIAG'] = pd.to_datetime(df['DT_DIAG'], errors='coerce')
    df = df.dropna(subset=['DT_DIAG'])
    df = df[(df['DT_DIAG'].dt.year >= 2012) & (df['DT_DIAG'].dt.year <= 2024)]
    
    ts = df.set_index('DT_DIAG').resample('ME').size()
    
    # Decomposicao sazonal
    # Usando periodo 12 para meses
    decomposition = seasonal_decompose(ts, model='additive', period=12)
    
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(14, 10), sharex=True)
    
    ax1.plot(ts.index, ts.values, label='Observado', color='#1f77b4')
    ax1.set_ylabel('Casos Mensais')
    ax1.set_title('Decomposição de Série Temporal: Hanseníase no Brasil (2012-2024)', fontsize=14, fontweight='bold')
    ax1.grid(True, linestyle='--', alpha=0.5)
    
    ax2.plot(ts.index, decomposition.trend, label='Tendência', color='#ff7f0e')
    ax2.set_ylabel('Tendência')
    ax2.grid(True, linestyle='--', alpha=0.5)
    
    ax3.plot(ts.index, decomposition.seasonal, label='Sazonalidade', color='#2ca02c')
    ax3.set_ylabel('Sazonalidade')
    ax3.grid(True, linestyle='--', alpha=0.5)
    
    ax4.scatter(ts.index, decomposition.resid, label='Ruído/Resíduo', color='#d62728', s=10)
    ax4.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    ax4.set_ylabel('Ruído Alatório')
    ax4.grid(True, linestyle='--', alpha=0.5)
    
    # Formatação de Datas
    ax4.xaxis.set_major_locator(mdates.YearLocator())
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Salvar na pasta do LaTeX
    out_dir = './overleaf/fig'
    os.makedirs(out_dir, exist_ok=True)
    plt.savefig(os.path.join(out_dir, 'decomposicao_sazonalidade.png'), dpi=300, bbox_inches='tight')
    print("Grafico salvo em overleaf/fig/decomposicao_sazonalidade.png")

if __name__ == "__main__":
    main()
