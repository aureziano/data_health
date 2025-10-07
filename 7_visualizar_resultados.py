# 7_visualizar_resultados.py (VERSÃO APRIMORADA)
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import config

def plotar_serie_temporal_comparativa(df_historico_full, df_pred_rf, df_pred_gru, id_municipio):
    """
    Plota a série temporal completa de casos reais e compara as predições
    dos modelos RandomForest e GRU para um município específico.
    """
    # Usar o df_historico_full para ter a série temporal completa
    dados_municipio = df_historico_full[df_historico_full['id_municipio'] == id_municipio].sort_values('ano')
    predicao_rf = df_pred_rf[df_pred_rf['id_municipio'] == id_municipio]
    predicao_gru = df_pred_gru[df_pred_gru['id_municipio'] == id_municipio]
    
    if dados_municipio.empty:
        print(f"AVISO: Não há dados históricos para plotar o município com ID {id_municipio}.")
        return

    nome_municipio = dados_municipio['nome_municipio'].iloc[0]
    ano_predicao = config.ANO_FINAL_ANALISE
    
    plt.figure(figsize=(12, 7))
    
    # Plotar dados históricos completos
    plt.plot(dados_municipio['ano'], dados_municipio['casos_hanseniase'], 'o-', label='Casos Reais (Histórico)', color='royalblue', alpha=0.7)
    
    # Isolar o valor real do ano de teste
    real_teste = dados_municipio[dados_municipio['ano'] == ano_predicao]
    if not real_teste.empty:
        plt.plot(real_teste['ano'], real_teste['casos_hanseniase'], 'o', markersize=12, color='green', label=f'Valor Real ({ano_predicao})')

    # Plotar a predição do RandomForest
    if not predicao_rf.empty:
        plt.plot(ano_predicao, predicao_rf['casos_previstos'], 'X', markersize=12, color='darkorange', label=f'Previsto - RandomForest ({ano_predicao})')
        
    # Plotar a predição do GRU
    if not predicao_gru.empty:
        plt.plot(ano_predicao, predicao_gru['casos_previstos'], '*', markersize=15, color='red', label=f'Previsto - GRU ({ano_predicao})')
    
    plt.title(f'Hanseníase: Série Temporal e Previsões - {nome_municipio}', fontsize=16)
    plt.xlabel('Ano')
    plt.ylabel('Número de Casos')
    plt.legend()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.show()

def run():
    print("--- INICIANDO SCRIPT 7: VISUALIZAÇÃO COMPARATIVA DOS RESULTADOS ---")
    
    ano_predicao = config.ANO_FINAL_ANALISE

    try:
        # Carregar o dataset histórico completo (gerado pelo script 2)
        df_historico = pd.read_csv(config.OUTPUT_PATHS['ml_dataset'])
        
        # Carregar as previsões dos dois modelos
        caminho_pred_rf = config.OUTPUT_PATHS['model_results'] # RandomForest
        caminho_pred_gru = config.RESULTS_PATH / f"resultados_predicao_gru_{ano_predicao}.csv" # GRU
        
        df_pred_rf = pd.read_csv(caminho_pred_rf)
        df_pred_gru = pd.read_csv(caminho_pred_gru)

    except FileNotFoundError as e:
        print(f"ERRO: Arquivo não encontrado: {e.filename}")
        print("Certifique-se de que os scripts 2, 3 e 4 foram executados com sucesso.")
        return

    # Unir as previsões dos dois modelos em um único DataFrame para análise
    df_comparacao = pd.merge(
        df_pred_rf.rename(columns={'casos_previstos': 'previsto_rf'}),
        df_pred_gru.rename(columns={'casos_previstos': 'previsto_gru'}),
        on=['id_municipio', 'nome_municipio', 'casos_reais']
    )
    df_comparacao['erro_rf'] = abs(df_comparacao['casos_reais'] - df_comparacao['previsto_rf'])
    df_comparacao['erro_gru'] = abs(df_comparacao['casos_reais'] - df_comparacao['previsto_gru'])

    # --- SELEÇÃO AUTOMÁTICA DE MUNICÍPIOS PARA VISUALIZAR ---
    
    # 1. Municípios com maior número de casos em 2022
    top_casos = df_comparacao.sort_values('casos_reais', ascending=False).head(3)
    # 2. Municípios onde o modelo GRU teve o maior erro
    pior_predicao_gru = df_comparacao.sort_values('erro_gru', ascending=False).head(2)
    # 3. Municípios onde o modelo GRU foi mais preciso (menor erro)
    melhor_predicao_gru = df_comparacao.sort_values('erro_gru', ascending=True).head(2)
    
    ids_para_plotar = pd.concat([
        top_casos['id_municipio'],
        pior_predicao_gru['id_municipio'],
        melhor_predicao_gru['id_municipio']
    ]).unique()
    
    print(f"\nGerando gráficos de série temporal para {len(ids_para_plotar)} municípios selecionados automaticamente...")
    for id_mun in ids_para_plotar:
        plotar_serie_temporal_comparativa(df_historico, df_pred_rf, df_pred_gru, id_mun)
        
    # Gráfico Agregado: Comparar o total de casos no Brasil
    total_real_por_ano = df_historico.groupby('ano')['casos_hanseniase'].sum()
    total_previsto_rf = df_pred_rf['casos_previstos'].sum()
    total_previsto_gru = df_pred_gru['casos_previstos'].sum()
    
    plt.figure(figsize=(12, 7))
    total_real_por_ano.plot(kind='bar', color='skyblue', label='Total de Casos Reais no Brasil', zorder=2)
    
    # Posições para as barras de previsão
    bar_positions = range(len(total_real_por_ano.index))
    ano_index = list(total_real_por_ano.index).index(ano_predicao)
    
    plt.bar(ano_index, total_previsto_rf, color='darkorange', width=0.3, align='edge', label=f'Total Previsto - RF ({ano_predicao})', zorder=3)
    plt.bar(ano_index, total_previsto_gru, color='red', width=-0.3, align='edge', label=f'Total Previsto - GRU ({ano_predicao})', zorder=3)
    
    plt.title('Total de Casos de Hanseníase no Brasil: Real vs. Previsto', fontsize=16)
    plt.xlabel('Ano')
    plt.ylabel('Número Total de Casos')
    plt.xticks(ticks=bar_positions, labels=total_real_por_ano.index, rotation=0)
    plt.legend()
    plt.grid(axis='y', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.show()
    
    print("--- SCRIPT 7 CONCLUÍDO ---")

if __name__ == '__main__':
    run()