# 6_classificar_cidades_sentinela.py (VERSÃO FINAL E DEFINITIVA)
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import config

def classify_city_definitivo(row, grau_q95, inter_q85, grau_q85):
    """
    Classifica uma cidade usando uma lógica hierárquica final baseada em proporção.
    q95 = Top 5%, q85 = Top 15%
    """
    # Regra 1: Nós de Infraestrutura (aeroportos fora da metrópole)
    if row['centralidade_grau'] > 4e6 and row['populacao'] < 400000:
        return "Nó de Infraestrutura"
    
    # Regra 2: Pontes Críticas
    # A importância como 'ponte' é pelo menos 10x maior que a importância como 'hub'
    # E a 'intermediação' está no top 15%
    if (row['intermediacao_normalizada'] > row['grau_normalizado'] * 10) and (row['centralidade_intermediacao'] >= inter_q85):
        return "Ponte Crítica"
        
    # Regra 3: Hubs Nacionais (Super-Conectores)
    # Volume de passageiros no top 5%
    if row['centralidade_grau'] >= grau_q95:
        return "Hub Nacional (Super-Conector)"
        
    # Regra 4: Hubs Regionais (Grandes Destinos)
    # Volume de passageiros no top 15%, mas não são Hubs Nacionais
    if row['centralidade_grau'] >= grau_q85:
        return "Hub Regional (Destino)"
        
    # Regra 5: Conectores Regionais
    # Não são hubs, mas têm importância de ponte acima da média (top 15%)
    if row['centralidade_intermediacao'] >= inter_q85:
        return "Conector Regional"

    return "Nó Local"

def run():
    print("--- INICIANDO SCRIPT 6: CLASSIFICAÇÃO ESTRATÉGICA (LÓGICA DEFINITIVA) ---")
    
    ano_analise = config.ANO_FINAL_ANALISE
    input_file = config.RESULTS_PATH / f'resultado_final_mobilidade_hanseniase_{ano_analise}.csv'
    if not input_file.exists():
        print(f"ERRO: Arquivo de entrada não encontrado: {input_file}")
        return
        
    df = pd.read_csv(input_file)
    
    # Calcular as colunas normalizadas que serão usadas na classificação
    df['grau_normalizado'] = (df['centralidade_grau'] - df['centralidade_grau'].min()) / (df['centralidade_grau'].max() - df['centralidade_grau'].min())
    df['intermediacao_normalizada'] = (df['centralidade_intermediacao'] - df['centralidade_intermediacao'].min()) / (df['centralidade_intermediacao'].max() - df['centralidade_intermediacao'].min())

    # Definir limiares
    grau_q95 = df['centralidade_grau'].quantile(0.95)
    inter_q85 = df['centralidade_intermediacao'].quantile(0.85)
    grau_q85 = df['centralidade_grau'].quantile(0.85)
    
    # Aplicar a nova função de classificação
    df['perfil_estrategico'] = df.apply(classify_city_definitivo, axis=1, args=(grau_q95, inter_q85, grau_q85))
    
    print("\n--- ANÁLISE DE PERFIS ESTRATÉGICOS (TOP 30) ---")
    colunas_display = ['nome_municipio', 'uf', 'perfil_estrategico', 'centralidade_grau', 'centralidade_intermediacao', 'taxa_incidencia']
    df_sorted = df.sort_values('score_sentinela', ascending=False)
    print(df_sorted[colunas_display].head(30).to_string())
    
    # Salvar e plotar (código idêntico ao anterior)
    output_csv = str(config.OUTPUT_PATHS['strategic_classification']).format(year=ano_analise)
    df_sorted.to_csv(output_csv, index=False)
    print(f"\nAnálise estratégica completa salva em: {output_csv}")

    print("\nGerando visualização gráfica dos perfis...")
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.figure(figsize=(14, 10))
    df_plot = df_sorted.copy()
    df_plot['log_grau'] = np.log10(df_plot['centralidade_grau'] + 1)
    df_plot['log_intermediacao'] = np.log10(df_plot['centralidade_intermediacao'] + 1)
    
    profile_order = sorted(df_plot['perfil_estrategico'].unique())
    sns.scatterplot(data=df_plot, x='log_grau', y='log_intermediacao', hue='perfil_estrategico', size='populacao', sizes=(50, 1500), alpha=0.7, palette='viridis', hue_order=profile_order)
    top_cities = df_plot.head(15)
    for i, city in top_cities.iterrows():
        plt.text(city['log_grau'], city['log_intermediacao'], city['nome_municipio'], fontsize=9, alpha=0.9)
    plt.title(f'Perfis Estratégicos de Cidades Sentinela ({ano_analise})', fontsize=18)
    plt.xlabel('Centralidade de Grau (Volume de "Hub") - Escala de Log', fontsize=12)
    plt.ylabel('Centralidade de Intermediação (Importância como "Ponte") - Escala de Log', fontsize=12)
    plt.legend(title='Perfil Estratégico')
    plt.tight_layout()
    output_plot = str(config.OUTPUT_PATHS['strategic_plot']).format(year=ano_analise)
    plt.savefig(output_plot, dpi=300)
    print(f"Gráfico de perfis estratégicos salvo em: {output_plot}")
    plt.show()
    
    print("--- SCRIPT 6 CONCLUÍDO ---")

if __name__ == '__main__':
    run()