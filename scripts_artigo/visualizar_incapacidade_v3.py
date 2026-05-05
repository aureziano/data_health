import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
from pathlib import Path

# Configurações de estilo
sns.set_theme(style="whitegrid", palette="flare")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300

def gerar_visualizacoes_v3():
    print("--- INICIANDO GERAÇÃO DE VISUALIZAÇÕES (V3) ---")
    
    # Caminhos
    results_dir = Path('results/incapacidade_v3')
    output_dir = Path('./overleaf/fig/incapacidade')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Carregar Dados
    social_sexo = pd.read_csv(results_dir / 'social_sexo.csv')
    social_idade = pd.read_csv(results_dir / 'social_idade.csv')
    social_escol = pd.read_csv(results_dir / 'social_escolaridade.csv')
    social_classe = pd.read_csv(results_dir / 'social_classe.csv')
    stats_df = pd.read_csv(results_dir / 'estatisticas_socio_clinicas.csv')
    mic_data = pd.read_csv(results_dir / 'microrregioes_evolucao.csv')
    
    # 2. Painel Socio-Clínico
    print("Gerando painel socio-clínico...")
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Sexo
    sns.barplot(data=social_sexo, x='SEXO', y='Taxa_Melhora', ax=axes[0,0], hue='SEXO', legend=False)
    axes[0,0].set_title('Melhora Clínica por Sexo (2018-2022)')
    axes[0,0].set_ylabel('Taxa de Melhora (%)')
    
    # Idade
    order_idade = ["Crianças (<15)", "Jovens (15-29)", "Adultos (30-59)", "Idosos (60+)"]
    sns.barplot(data=social_idade, x='FAIXA_ETARIA', y='Taxa_Melhora', order=order_idade, ax=axes[0,1], hue='FAIXA_ETARIA', legend=False)
    axes[0,1].set_title('Melhora Clínica por Faixa Etária')
    axes[0,1].set_ylabel('Taxa de Melhora (%)')
    
    # Escolaridade
    sns.barplot(data=social_escol, x='ESCOLARIDADE', y='Taxa_Melhora', ax=axes[1,0], hue='ESCOLARIDADE', legend=False)
    axes[1,0].set_title('Melhora Clínica por Escolaridade')
    axes[1,0].set_ylabel('Taxa de Melhora (%)')
    plt.setp(axes[1,0].get_xticklabels(), rotation=45)
    
    # Classe
    sns.barplot(data=social_classe, x='CLASSE', y='Taxa_Melhora', ax=axes[1,1], hue='CLASSE', legend=False)
    axes[1,1].set_title('Melhora Clínica por Classificação Operacional')
    axes[1,1].set_ylabel('Taxa de Melhora (%)')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'painel_socio_clinico.png', bbox_inches='tight')
    plt.close()
    
    # 3. Tendência de Gravidade por Classe (MB vs PB)
    print("Gerando tendência por classe operacional...")
    plt.figure(figsize=(12, 6))
    for classe in ['PB', 'MB']:
        subset = stats_df[stats_df['Classe'] == classe]
        plt.plot(subset['Ano'], subset['Média_Diag'], label=f'Média Diag ({classe})', marker='o')
        plt.fill_between(subset['Ano'], subset['Média_Diag'] - 0.1, subset['Média_Diag'] + 0.1, alpha=0.1)
    
    plt.title('Evolução do Grau Médio de Incapacidade por Classificação Operacional')
    plt.xlabel('Ano')
    plt.ylabel('Média GIF')
    plt.legend()
    plt.savefig(output_dir / 'tendencia_por_classe.png', bbox_inches='tight')
    plt.close()
    
    # 4. Mapa de Microrregiões V3
    print("Gerando mapa de microrregiões V3...")
    try:
        mic_shp = gpd.read_file('data/MAPAS/BR_Microrregioes_2022/BR_Microrregioes_2022.shp')
        mic_shp['CD_MICRO'] = mic_shp['CD_MICRO'].astype(str)
        mic_data['CD_MICRO'] = mic_data['CD_MICRO'].astype(str)
        
        map_final = mic_shp.merge(mic_data, on='CD_MICRO', how='left')
        
        fig, ax = plt.subplots(1, 1, figsize=(12, 12))
        map_final.plot(column='taxa_melhora', cmap='RdYlGn', legend=True,
                       legend_kwds={'label': "Taxa de Melhora (%)", 'orientation': "horizontal", 'pad': 0.02},
                       ax=ax, missing_kwds={'color': 'lightgrey'}, linewidth=0.1, edgecolor='0.5')
        ax.set_title('Espacialização da Taxa de Melhora do GIF no Brasil (2018-2022)')
        ax.axis('off')
        plt.savefig(output_dir / 'mapa_microrregioes_v3.png', bbox_inches='tight')
        plt.close()
    except Exception as e:
        print(f"Erro ao gerar mapa: {e}")

    print(f"Visualizações V3 concluídas. Salvas em {output_dir}")

if __name__ == "__main__":
    gerar_visualizacoes_v3()
