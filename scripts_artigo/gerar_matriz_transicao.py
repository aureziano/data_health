import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Configurações
PATH_DATA = str(config.PATHS['hanceniase'])
OUTPUT_DIR = "./scripts_artigo/graficos/clinica"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def main():
    print("Gerando Matriz de Transição Clínica (Diagnóstico -> Alta)...")
    
    # 1. Carregamento
    try:
        df = pd.read_csv(PATH_DATA, low_memory=False)
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        return

    # 2. Limpeza e Filtro
    # AVALIA_N: GIF no diagnóstico
    # AVAL_ATU_N: GIF na última avaliação/alta
    cols = ['AVALIA_N', 'AVAL_ATU_N']
    
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        # Filtro para valores válidos de GIF (0, 1, 2)
        df = df[df[col].isin([0, 1, 2])]

    # 3. Cálculo da Matriz de Transição
    matrix = pd.crosstab(df['AVALIA_N'], df['AVAL_ATU_N'], normalize='index') * 100

    # 4. Plotagem
    plt.figure(figsize=(8, 6))
    sns.heatmap(matrix, annot=True, fmt=".1f", cmap="YlOrRd", cbar_kws={'label': 'Frequência (%)'})
    
    plt.title("Matriz de Transição do Grau de Incapacidade Física\n(Diagnóstico vs. Última Avaliação)", fontsize=14, fontweight='bold')
    plt.xlabel("Grau na Alta / Atual", fontsize=12)
    plt.ylabel("Grau no Diagnóstico", fontsize=12)
    
    # Ajuste de labels
    labels = ["Grau 0", "Grau 1", "Grau 2"]
    plt.xticks(ticks=[0.5, 1.5, 2.5], labels=labels)
    plt.yticks(ticks=[0.5, 1.5, 2.5], labels=labels)

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/matriz_transicao_gif.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Matriz de transição salva em {OUTPUT_DIR}/matriz_transicao_gif.png")

if __name__ == "__main__":
    main()
