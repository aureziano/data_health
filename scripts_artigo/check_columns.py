import pandas as pd
import pickle
try:
    with open('data/HANSENIASE_TOTAL.pkl', 'rb') as f:
        df = pickle.load(f)
    print("Colunas encontradas:")
    print(df.columns.tolist())
except Exception as e:
    print(f"Erro: {e}")
