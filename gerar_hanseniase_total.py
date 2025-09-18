
import pandas as pd
import glob

# Path to the folder containing the HANSBR files
path = r'd:\python\data_health\data\HANSENIASE'
all_files = glob.glob(path + "/HANSBR*.csv")

li = []

for filename in all_files:
    df = pd.read_csv(filename, index_col=None, header=0, sep=',', encoding='utf-8', low_memory=False)
    li.append(df)

frame = pd.concat(li, axis=0, ignore_index=True)

# Save the consolidated file
output_path = r'd:\python\data_health\data\HANSENIASE\HANSENIASE_TOTAL_.csv'
frame.to_csv(output_path, index=False, encoding='utf-8')

print(f"Arquivo HANSENIASE_TOTAL_.csv criado com sucesso em {output_path}")
