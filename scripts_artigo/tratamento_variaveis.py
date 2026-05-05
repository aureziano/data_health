import pandas as pd
import numpy as np
import os

# Configurações gerais
dir_tratamento = "./tratamento"
os.makedirs(dir_tratamento, exist_ok=True)

# 1. Carregamento dos dados
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config
caminho_arquivo = str(config.PATHS['hanceniase'])
try:
    df = pd.read_csv(caminho_arquivo, encoding="utf-8", low_memory=False)
except FileNotFoundError:
    print(f"Arquivo {caminho_arquivo} não encontrado.")
    exit()

# 2. Seleção de variáveis relevantes (sem variáveis de data/hora)
# CORREÇÃO: Removido TPALTA_N das features (era usado como target - DATA LEAKAGE)
# Target correto: AVAL_ATU_N (Grau de Incapacidade Física - G2D)
variaveis_preditoras = [
    'CLASSOPERA', 'BACILOSCOP', 'ESQ_INI_N', 'CONTREG', 'NERVOSAFET', 'ESQ_ATU_N',
    'DOSE_RECEB', 'CONTEXAM', 'CS_SEXO', 'CS_RACA', 'CS_ESCOL_N',
    'NU_ANO'
]
variaveis_alvo = ['AVAL_ATU_N']  # Grau de Incapacidade Física (G2D)

# 3. Remover linhas com missing no alvo
df = df.dropna(subset=variaveis_alvo + variaveis_preditoras)

# 4. Codificação categórica (apenas para variáveis relevantes)
df_encoded = pd.get_dummies(df[variaveis_preditoras], drop_first=True)

# 5. Salvar dados tratados
df_encoded.to_csv(f"{dir_tratamento}/dados_tratados.csv", index=False)
df[variaveis_alvo].to_csv(f"{dir_tratamento}/alvo_tratado.csv", index=False)

print("Tratamento de variáveis concluído. Arquivos salvos em ./tratamento.")
