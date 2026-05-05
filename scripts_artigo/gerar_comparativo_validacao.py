import matplotlib.pyplot as plt
import numpy as np
import os

# Configurações
dir_graficos = "./overleaf/fig"
os.makedirs(dir_graficos, exist_ok=True)

def plot_validation_comparison():
    """Gera um comparativo pedagógico entre K-Fold (errado para TS) e Walk-forward (correto)."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    # Cores
    color_train = '#3498db'
    color_test = '#e67e22'
    
    # 1. K-Fold Tradicional (CUIDADO: Shuffled)
    ax1.set_title("A. Validação Cruzada Tradicional (K-Fold) - Inadequada para Séries Temporais", fontsize=12, fontweight='bold', color='red')
    for i in range(4):
        # Gera índices aleatórios para simular o shuffle
        indices = np.arange(10)
        np.random.seed(i)
        np.random.shuffle(indices)
        
        train_idx = indices[:7]
        test_idx = indices[7:9]
        
        ax1.barh(i, 10, left=0, color='whitesmoke', edgecolor='lightgray', alpha=0.3)
        for idx in train_idx:
            ax1.barh(i, 1, left=idx, color=color_train, edgecolor='black', alpha=0.6)
        for idx in test_idx:
            ax1.barh(i, 1, left=idx, color=color_test, edgecolor='black', alpha=0.9)
            
        ax1.text(-0.5, i, f"Fold {i+1}", va='center', ha='right', fontsize=10)
    
    ax1.text(5, -1, "↑ Risco de Vazamento de Dados (Futuro predizendo Passado) ↑", color='red', ha='center', fontsize=9, style='italic')

    # 2. Walk-forward (Séries Temporais)
    ax2.set_title("B. Validação Walk-forward - Padrão Ouro para Séries Temporais", fontsize=12, fontweight='bold', color='green')
    for i in range(4):
        train_width = 3 + i * 1.5
        ax2.barh(i, 10, left=0, color='whitesmoke', edgecolor='lightgray', alpha=0.3)
        ax2.barh(i, train_width, left=0, color=color_train, edgecolor='black', alpha=0.8,
                label='Treino (Passado)' if i == 0 else "")
        ax2.barh(i, 1, left=train_width, color=color_test, edgecolor='black', alpha=0.9,
                label='Teste (Futuro)' if i == 0 else "")
        ax2.text(-0.5, i, f"Etapa {i+1}", va='center', ha='right', fontsize=10)

    ax2.set_xticks(range(11))
    ax2.set_xticklabels([f"T{x}" for x in range(11)])
    ax2.set_xlabel("Eixo Temporal (Fluxo do Tempo →)", fontsize=11)
    
    ax1.set_yticks([])
    ax2.set_yticks([])
    
    ax2.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2, frameon=False)
    
    plt.tight_layout()
    plt.savefig(f"{dir_graficos}/comparativo_metodos_validacao.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Gráfico comparativo de métodos gerado com sucesso.")

if __name__ == "__main__":
    plot_validation_comparison()
