import matplotlib.pyplot as plt
import os

# Configurações
dir_graficos = "./overleaf/fig"
os.makedirs(dir_graficos, exist_ok=True)

def plot_pedagogical_sliding_window():
    """Gera uma ilustração pedagógica do esquema de Sliding Window (Walk-forward)."""
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Cores premium
    color_train = '#3498db'  # Azul suave
    color_test = '#e67e22'   # Laranja suave
    
    n_splits = 4
    for i in range(n_splits):
        # Barra de fundo (Tempo total)
        ax.barh(i, 10, left=0, color='whitesmoke', edgecolor='lightgray', linewidth=0.5)
        
        # Bloco de Treino (Crescente)
        train_width = 3 + i * 1.5
        ax.barh(i, train_width, left=0, color=color_train, edgecolor='black', alpha=0.8, 
                label='Janela de Treino' if i == 0 else "")
        
        # Bloco de Teste (Ponto seguinte)
        ax.barh(i, 1, left=train_width, color=color_test, edgecolor='black', alpha=0.9,
                label='Ponto de Validação' if i == 0 else "")
        
        ax.text(-0.5, i, f"Etapa {i+1}", va='center', ha='right', fontsize=11, fontweight='bold')

    ax.set_yticks([])
    ax.set_xticks(range(11))
    ax.set_xticklabels([f"T{x}" for x in range(11)])
    ax.set_xlabel("Eixo Temporal (Meses/Anos)", fontsize=12)
    ax.set_title("Esquema de Validação Walk-forward (Sliding Window)", fontsize=14, pad=20)
    
    # Detalhe estético: setas de progressão
    for i in range(n_splits-1):
        ax.annotate('', xy=(3 + (i+1)*1.5, i+0.4), xytext=(3 + i*1.5, i+0.1),
                    arrowprops=dict(arrowstyle="->", color='gray', lw=1, connectionstyle="arc3,rad=.2"))

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False, fontsize=11)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    plt.tight_layout()
    plt.savefig(f"{dir_graficos}/esquema_sliding_window.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Gráfico de esquema Sliding Window gerado com sucesso em overleaf/fig/esquema_sliding_window.png")

if __name__ == "__main__":
    plot_pedagogical_sliding_window()
