import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
from pathlib import Path
import os

# Configurações de estilo
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300

def gerar_visualizacoes_v2():
    print("--- INICIANDO GERAÇÃO DE VISUALIZAÇÕES (V2.2) ---")
    
    # Caminhos
    results_dir = Path('results/incapacidade_v2')
    output_dir = Path('graficos_analise/incapacidade_v2')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Carregar Dados de Análise
    stats_long = pd.read_csv(results_dir / 'estatisticas_longitudinais.csv', index_col=0)
    qualidade = pd.read_csv(results_dir / 'qualidade_dados.csv', index_col=0)
    # evol_anual = pd.read_csv(results_dir / 'evolucao_temporal_pct.csv', index_col=0) # Not used in plots yet
    uf_data = pd.read_csv(results_dir / 'evolucao_uf.csv')
    mic_data = pd.read_csv(results_dir / 'evolucao_microrregioes.csv')
    
    # 2. Gráfico de Tendências Estatísticas (Média e Variância)
    print("Gerando gráfico de tendências estatísticas...")
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Médias
    ax1.plot(stats_long.index, stats_long['mean_diag'], label='Média GIF (Diagnóstico)', marker='o', color='#3498db', linewidth=2)
    ax1.plot(stats_long.index, stats_long['mean_cura'], label='Média GIF (Cura)', marker='s', color='#2ecc71', linewidth=2)
    ax1.set_xlabel('Ano de Notificação', fontsize=12)
    ax1.set_ylabel('Grau Médio (0-2)', fontsize=12)
    ax1.legend(loc='upper left', frameon=True)
    
    # Variância (Eixo secundário)
    ax2 = ax1.twinx()
    ax2.plot(stats_long.index, stats_long['var_diag'], '--', alpha=0.6, color='#e74c3c', label='Variância (Diagnóstico)')
    ax2.set_ylabel('Variância', fontsize=12, color='#e74c3c')
    ax2.tick_params(axis='y', labelcolor='#e74c3c')
    ax2.legend(loc='upper right', frameon=True)
    
    plt.title('Tendências do Grau de Incapacidade Física na Hanseníase (2001-2024)', fontsize=14, pad=20)
    plt.savefig(output_dir / 'tendencia_stats_long.png', bbox_inches='tight')
    plt.close()
    
    # 3. Gráfico de Qualidade (Completude)
    print("Gerando gráfico de completude de dados...")
    plt.figure(figsize=(12, 5))
    plt.bar(qualidade.index, qualidade['pct_completude_cura'], color='#34495e', alpha=0.7, label='% Avaliação na Alta')
    plt.bar(qualidade.index, qualidade['pct_pares_validos'], color='#e67e22', alpha=0.5, label='% Pares Válidos (Diag & Cura)')
    plt.axhline(y=75, color='red', linestyle='--', label='Meta OMS (75%)')
    plt.xlabel('Ano')
    plt.ylabel('Percentual (%)')
    plt.title('Qualidade do Preenchimento no SINAN: Avaliações de Incapacidade')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.savefig(output_dir / 'qualidade_completude_long.png', bbox_inches='tight')
    plt.close()
    
    # 4. Mapas Geográficos
    print("Gerando mapas geográficos...")
    
    try:
        # Mapa UF
        uf_shp = gpd.read_file('data/MAPAS/BR_UF_2022/BR_UF_2022.shp')
        uf_shp['SIGLA_UF'] = uf_shp['SIGLA_UF'].astype(str)
        uf_data['uf_sigla'] = uf_data['uf_sigla'].astype(str)
        
        uf_map_data = uf_shp.merge(uf_data, left_on='SIGLA_UF', right_on='uf_sigla', how='left')
        
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))
        uf_map_data.plot(column='taxa_melhora', cmap='RdYlGn', legend=True, 
                         legend_kwds={'label': "Taxa de Melhora (%)", 'orientation': "horizontal", 'pad': 0.05},
                         ax=ax, missing_kwds={'color': 'lightgrey'})
        ax.set_title('Taxa de Melhora do GIF por Estado (2018-2022)')
        ax.axis('off')
        plt.savefig(output_dir / 'mapa_uf_melhora_v2.png', bbox_inches='tight')
        plt.close()
        
        # Mapa Microrregiões
        print("Mapeando Microrregiões (isso pode levar algum tempo)...")
        mic_shp = gpd.read_file('data/MAPAS/BR_Microrregioes_2022/BR_Microrregioes_2022.shp')
        mic_shp['CD_MICRO'] = mic_shp['CD_MICRO'].astype(str)
        mic_data['CD_MICRO'] = mic_data['CD_MICRO'].astype(str)
        
        mic_map_data = mic_shp.merge(mic_data, on='CD_MICRO', how='left')
        
        fig, ax = plt.subplots(1, 1, figsize=(12, 12))
        mic_map_data.plot(column='taxa_melhora', cmap='RdYlGn', legend=True,
                          legend_kwds={'label': "Taxa de Melhora (%)", 'orientation': "horizontal", 'pad': 0.02},
                          ax=ax, missing_kwds={'color': 'lightgrey'}, linewidth=0.05, edgecolor='0.8')
        ax.set_title('Taxa de Melhora do GIF por Microrregião (2018-2022)')
        ax.axis('off')
        plt.savefig(output_dir / 'mapa_micro_melhora_v2.png', bbox_inches='tight')
        plt.close()
        
    except Exception as e:
        print(f"Erro ao gerar mapas: {e}")

    print(f"Visualizações concluídas. Salvas em {output_dir}")

if __name__ == "__main__":
    gerar_visualizacoes_v2()
