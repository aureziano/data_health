import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def gerar_visualizacoes():
    print("--- INICIANDO GERAÇÃO DE VISUALIZAÇÕES (VERSÃO FINAL CORRIGIDA) ---")
    
    # Caminhos
    data_dir = Path('results/incapacidade')
    output_dir = Path('graficos_analise/incapacidade')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Configuração de Estilo
    sns.set_theme(style="whitegrid", palette="muted")
    plt.rcParams['figure.dpi'] = 150
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
    
    # 1. Gráfico de Série Histórica (Evolução PCT)
    try:
        print("1. Gerando série histórica de evolução...")
        df_hist_pct = pd.read_csv(data_dir / 'historico_evolucao_pct.csv')
        df_hist_pct.set_index('NU_ANO', inplace=True)
        
        plt.figure(figsize=(12, 6))
        plt_data = df_hist_pct[['Melhora', 'Estável', 'Piora']] * 100
        plt_data.plot(kind='line', marker='o', ax=plt.gca(), linewidth=2)
        plt.title('Evolução do Grau de Incapacidade Física na Hanseníase (2001-2024)', fontsize=14)
        plt.ylabel('Proporção de Casos (%)')
        plt.xlabel('Ano de Notificação')
        plt.legend(title='Mudança de GIF')
        plt.tight_layout()
        plt.savefig(output_dir / 'serie_historica_evolucao.png')
        plt.close()
        print("   [OK] serie_historica_evolucao.png")
    except Exception as e:
        print(f"   [ERRO] Falha no gráfico 1: {e}")

    # 2. Gráfico de Médias de GIF (Diagnóstico vs Cura)
    try:
        print("2. Gerando gráfico de médias de GIF...")
        df_graus = pd.read_csv(data_dir / 'historico_graus_media.csv')
        plt.figure(figsize=(12, 6))
        plt.plot(df_graus['NU_ANO'], df_graus['AVALIA_N'], label='Média GIF (Diagnóstico)', color='#e74c3c', marker='s', linewidth=2)
        plt.plot(df_graus['NU_ANO'], df_graus['AVAL_ATU_N'], label='Média GIF (Cura)', color='#2ecc71', marker='^', linewidth=2)
        plt.fill_between(df_graus['NU_ANO'], df_graus['AVAL_ATU_N'], df_graus['AVALIA_N'], color='gray', alpha=0.1, label='Redução da Incapacidade')
        plt.title('Evolução do Grau Médio de Incapacidade: Diagnóstico vs. Cura', fontsize=14)
        plt.ylabel('Grau Médio (0-2)')
        plt.xlabel('Ano')
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_dir / 'media_gif_historico.png')
        plt.close()
        print("   [OK] media_gif_historico.png")
    except Exception as e:
        print(f"   [ERRO] Falha no gráfico 2: {e}")

    # 3. Matriz de Transição (Heatmap)
    try:
        print("3. Gerando matriz de transição...")
        df_matriz = pd.read_csv(data_dir / 'matriz_transicao_2019_2022.csv', index_col=0)
        plt.figure(figsize=(8, 6))
        sns.heatmap(df_matriz, annot=True, fmt=".1%", cmap="YlGnBu", annot_kws={"size": 12})
        plt.title('Matriz de Transição de GIF: Diagnóstico -> Cura (2019-2022)', fontsize=14)
        plt.ylabel('Grau no Diagnóstico')
        plt.xlabel('Grau na Cura')
        plt.tight_layout()
        plt.savefig(output_dir / 'matriz_transicao_heatmap.png')
        plt.close()
        print("   [OK] matriz_transicao_heatmap.png")
    except Exception as e:
        print(f"   [ERRO] Falha no gráfico 3: {e}")

    # 4. Distribuição por Região (Barras Empilhadas)
    try:
        print("4. Gerando gráfico por regiões...")
        df_uf = pd.read_csv(data_dir / 'analise_uf_regiao.csv')
        resumo_regiao = df_uf.groupby('regiao')[['Melhora', 'Estável', 'Piora']].sum()
        resumo_reg_pct = resumo_regiao.div(resumo_regiao.sum(axis=1), axis=0) * 100
        
        # Ordem das regiões
        ordem = ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul']
        resumo_reg_pct = resumo_reg_pct.reindex(ordem)
        
        ax = resumo_reg_pct.plot(kind='bar', stacked=True, figsize=(10, 6), color=['#2ecc71', '#3498db', '#e74c3c'])
        plt.title('Status de Evolução do GIF por Região (2019-2022)', fontsize=14)
        plt.ylabel('Porcentagem de Casos (%)')
        plt.xlabel('Região Geográfica')
        plt.xticks(rotation=0)
        plt.legend(title='Evolução', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(output_dir / 'evolucao_por_regiao.png')
        plt.close()
        resumo_reg_pct.to_csv(data_dir / 'resumo_regiao.csv')
        print("   [OK] evolucao_por_regiao.png e resumo_regiao.csv")
    except Exception as e:
        print(f"   [ERRO] Falha no gráfico de regiões: {e}")

    print(f"--- FIM DA GERAÇÃO DE VISUALIZAÇÕES ---")

if __name__ == "__main__":
    gerar_visualizacoes()
