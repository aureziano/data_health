import pandas as pd
import numpy as np

def generate_dashboard_data():
    print("Gerando dashboard_data.csv (Fix)...")
    dates = pd.date_range(start='2019-01-01', end='2024-12-01', freq='MS')
    
    # Gerando dados que mimetizam a realidade brasileira da hanseníase na pandemia
    # 2019: Estabilidade (~2300 casos/mês)
    # 2020-2021: Queda brusca (~1400 casos/mês)
    # 2022-2024: Recuperação e Backlog (~2500 casos/mês)
    
    real = []
    expected = []
    
    for d in dates:
        exp = 2200 + np.random.randint(-100, 100)
        expected.append(exp)
        
        if d < pd.Timestamp('2020-03-01'):
            real.append(exp + np.random.randint(-50, 50))
        elif d < pd.Timestamp('2022-05-01'):
            real.append(exp * 0.65 + np.random.randint(-100, 100)) # Queda de ~35%
        else:
            real.append(exp * 1.1 + np.random.randint(-100, 200)) # Backlog +10%
            
    df = pd.DataFrame({'Data': dates, 'Real': real, 'Esperado': expected})
    df.to_csv("shiny/dashboard_data.csv", index=False)
    print("✓ shiny/dashboard_data.csv gerado com sucesso.")

if __name__ == "__main__":
    generate_dashboard_data()
