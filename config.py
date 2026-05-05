# config.py
from pathlib import Path

# --- Período de Análise ---
# Com base nos seus dados, o intervalo com sobreposição é 2019-2024.
# O último ano completo e confiável para teste é 2022 ou 2023 (dependendo da população).
# Vamos usar 2022 como o ano final de teste.
ANO_INICIAL_ANALISE = 2019
ANO_FINAL_ANALISE = 2022 # Usaremos este como nosso ano de teste

# --- Caminhos Base ---
BASE_PATH = Path('.')
DATA_PATH = BASE_PATH / 'data'
RESULTS_PATH = BASE_PATH / 'results'

def _get_latest_hanseniase(data_path: Path) -> Path:
    """Retorna o arquivo HANSENIASE_TOTAL_*.csv mais recente em data/HANSENIASE/."""
    from datetime import datetime
    hanseniase_dir = data_path / 'HANSENIASE'
    candidatos = list(hanseniase_dir.glob('HANSENIASE_TOTAL_*.csv'))
    if not candidatos:
        raise FileNotFoundError(
            f"Nenhum arquivo HANSENIASE_TOTAL_*.csv encontrado em {hanseniase_dir}\n"
            "Execute: python -m convert_dbc"
        )
    
    def extrair_data(p):
        try:
            # Pega dd_mm_yyyy do nome do arquivo
            parts = p.stem.split('_')
            date_str = f"{parts[-3]}_{parts[-2]}_{parts[-1]}"
            return datetime.strptime(date_str, '%d_%m_%Y')
        except:
            return datetime.min

    candidatos.sort(key=extrair_data, reverse=True)
    arquivo = candidatos[0]
    print(f"[config] Arquivo de hanseníase detectado: {arquivo.name}")
    return arquivo

# --- Caminhos dos Arquivos de Entrada ---
PATHS = {
    'populacao': DATA_PATH / 'IBGE' / 'populacao_municipios.csv',
    'hanceniase': _get_latest_hanseniase(DATA_PATH),
    'antt': DATA_PATH / 'MOBILIDADE' / 'dados_rodoviarios_ibge.csv',
    'ibge_2016': DATA_PATH / 'MOBILIDADE' / 'dados_rodoviarias_hidroviarias_2016.csv',
    'anac': DATA_PATH / 'MOBILIDADE' / 'dados_aereos_consolidados.csv',
}

# --- Caminhos dos Arquivos de Saída (Gerados) ---
OUTPUT_PATHS = {
    'full_graph': RESULTS_PATH / 'rede_mobilidade_completa.gpickle',
    'centrality_yearly': RESULTS_PATH / 'centralidade_anual.csv',
    'ml_dataset': RESULTS_PATH / 'dataset_ml_hanseniase.csv',
    'model_results': RESULTS_PATH / 'resultados_predicao.csv',
    'feature_importance_plot': RESULTS_PATH / 'feature_importance.png',
    'prediction_plot': RESULTS_PATH / 'predicoes_vs_real.png',
    'strategic_classification': RESULTS_PATH / 'analise_estrategica_sentinela_{year}.csv',
    'strategic_plot': RESULTS_PATH / 'plot_perfis_estrategicos_{year}.png'
}

# Garante que a pasta de resultados exista
RESULTS_PATH.mkdir(exist_ok=True)