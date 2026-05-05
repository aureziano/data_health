import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configurações gerais
dir_graficos = "./scripts_artigo/graficos"
dir_relatorios = "./scripts_artigo/relatorios"
os.makedirs(dir_graficos, exist_ok=True)
os.makedirs(dir_relatorios, exist_ok=True)

# 1. Carregamento e inspeção inicial
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config
caminho_arquivo = str(config.PATHS['hanceniase'])
try:
    df = pd.read_csv(caminho_arquivo, encoding="utf-8", low_memory=False)
except FileNotFoundError:
    print(f"Arquivo {caminho_arquivo} não encontrado. Executando com DataFrame vazio para testes.")
    df = pd.DataFrame()

# 2. Separação de variáveis por tipo
cols_num = df.select_dtypes(include=[np.number]).columns.tolist()
cols_cat = df.select_dtypes(exclude=[np.number]).columns.tolist()

# 3. Relatório de estatísticas e missing em .txt
with open(f"{dir_relatorios}/relatorio_eda.txt", "w", encoding="utf-8") as f:
    f.write(f"Dimensões: {df.shape}\n\n")
    f.write(f"Tipos de dados:\n{df.dtypes.value_counts()}\n\n")
    f.write(f"Primeiras linhas:\n{df.head().to_string()}\n\n")
    f.write(f"Qtd variáveis numéricas: {len(cols_num)}\n")
    f.write(f"Qtd variáveis categóricas: {len(cols_cat)}\n\n")

    if not df.empty:
        # Missing values
        missing_abs = df.isna().sum()
        missing_pct = (missing_abs / len(df)) * 100
        missing = pd.DataFrame({"missing_abs": missing_abs, "missing_pct": missing_pct})
        missing = missing.sort_values("missing_pct", ascending=False)
        f.write(f"Missing por variável:\n{missing.to_string()}\n\n")

        # Estatísticas descritivas – numéricas
        desc_num = df[cols_num].describe(percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]).T
        f.write(f"Estatísticas descritivas – numéricas:\n{desc_num.to_string()}\n\n")

        # Estatísticas descritivas – categóricas
        resumo_cat = {}
        for c in cols_cat:
            resumo_cat[c] = {
                "n_unicos": df[c].nunique(dropna=True),
                "moda": df[c].mode(dropna=True).iloc[0] if df[c].mode(dropna=True).size > 0 else np.nan,
                "freq_moda": df[c].value_counts(dropna=True).iloc[0] if df[c].value_counts(dropna=True).size > 0 else np.nan
            }
        resumo_cat = pd.DataFrame(resumo_cat).T
        f.write(f"Estatísticas descritivas – categóricas:\n{resumo_cat.to_string()}\n\n")

        # Outliers
        outlier_summary = []
        for c in cols_num:
            serie = df[c].dropna()
            if serie.empty:
                continue
            q1 = serie.quantile(0.25)
            q3 = serie.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            n_outliers = ((serie < lower) | (serie > upper)).sum()
            outlier_pct = n_outliers / len(serie) * 100
            outlier_summary.append({
                "coluna": c,
                "q1": q1,
                "q3": q3,
                "iqr": iqr,
                "limite_inf": lower,
                "limite_sup": upper,
                "n_outliers": n_outliers,
                "pct_outliers": outlier_pct
            })
        outlier_df = pd.DataFrame(outlier_summary).sort_values("pct_outliers", ascending=False)
        f.write(f"Resumo de outliers por variável numérica (critério 1.5 * IQR):\n{outlier_df.to_string()}\n\n")

# 4. Gráficos com título específico por variável
if not df.empty:
    # Missing
    plt.figure(figsize=(10, 6))
    sns.histplot(missing["missing_pct"], bins=20, kde=False)
    plt.title("Distribuição de % missing por variável")
    plt.xlabel("% missing")
    plt.ylabel("Contagem de variáveis")
    plt.savefig(f"{dir_graficos}/missing_pct_histograma.png", bbox_inches='tight')
    plt.close()

    # Distribuições – numéricas
    for c in cols_num:
        serie = df[c].dropna()
        if serie.empty or serie.isna().all():
            print(f"Variável {c} sem dados válidos. Pulando boxplot.")
            continue

        plt.figure(figsize=(12, 4))
        plt.subplot(1, 2, 1)
        sns.histplot(serie, kde=True)
        plt.title(f"Histograma da variável {c}")

        plt.subplot(1, 2, 2)
        sns.boxplot(x=serie)
        plt.title(f"Boxplot da variável {c}")
        plt.tight_layout()
        plt.savefig(f"{dir_graficos}/distribuicao_{c}.png", bbox_inches='tight')
        plt.close()

    # Distribuições – categóricas
    for c in cols_cat:
        vc = df[c].value_counts(dropna=False).head(20)
        if vc.empty:
            print(f"Variável {c} sem dados válidos. Pulando barplot.")
            continue

        plt.figure(figsize=(10, 4))
        sns.barplot(x=vc.index.astype(str), y=vc.values)
        plt.title(f"Distribuição da variável {c} (top 20)")
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig(f"{dir_graficos}/distribuicao_{c}.png", bbox_inches='tight')
        plt.close()

    # Correlação
    if len(cols_num) > 1:
        corr = df[cols_num].corr()
        plt.figure(figsize=(12, 10))
        sns.heatmap(corr, cmap="coolwarm", center=0)
        plt.title("Matriz de correlação das variáveis numéricas")
        plt.savefig(f"{dir_graficos}/correlacao_matriz.png", bbox_inches='tight')
        plt.close()

    # Relações numérico × categórico
    exemplos_cat = [c for c in ["CS_SEXO", "SG_UF_NOT", "ID_MUNICIP"] if c in df.columns]
    for cat_col in exemplos_cat:
        for num_col in [c for c in cols_num if c not in ["NU_ANO"]][:5]:
            plt.figure(figsize=(10, 4))
            sns.boxplot(data=df, x=cat_col, y=num_col)
            plt.title(f"{num_col} por {cat_col}")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(f"{dir_graficos}/{num_col}_por_{cat_col}.png", bbox_inches='tight')
            plt.close()
