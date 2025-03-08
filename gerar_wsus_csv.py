import os
import pandas as pd
import numpy as np
from datetime import datetime

# Path dos arquivos a serem analisados
path_csv = os.path.join('.', 'data', 'HANS')
path_csv

## Montando o DataFrame
# Encontrar arquivos com o padrão HANSENIASE_TOTAL_
print("-----------------------------------PROCESSO DE TRATAMENTO DE DADOS INICIADO---------------------------")
arquivos = []
for f in os.listdir(path_csv):
    if f.startswith("HANSENIASE_TOTAL_") and f.endswith(".csv"):
        try:
            # Extrair data do nome do arquivo
            data_str = f.split('_')[-3:]  # Pega os últimos 3 elementos (dd, mm, yyyy)
            data = datetime.strptime('_'.join(data_str).replace('.csv', ''), '%d_%m_%Y')
            arquivos.append((data, f))
        except Exception as e:
            print(f"Arquivo com formato inválido: {f} - {e}")

# Executar script externo se nenhum arquivo for encontrado
if not arquivos:
    print("Nenhum arquivo encontrado. Executando script para gerar arquivo...")
    path_convert_dbc = os.path.join(".\\","convert_dbc.py")
    resultado = os.system('python ' + path_convert_dbc)
    
    if resultado == 0:
        print("Script executado com sucesso. Verificando novo arquivo...")
        # Recarregar lista de arquivos após execução do script
        for f in os.listdir(path_csv):
            if f.startswith('HANSENIASE_TOTAL_') and f.endswith('.csv'):
                try:
                    data_str = f.split('_')[-3:]
                    data = datetime.strptime('_'.join(data_str).replace('.csv', ''), '%d_%m_%Y')
                    arquivos.append((data, f))
                except Exception as e:
                    print(f"Erro ao processar novo arquivo: {f} - {e}")
    else:
        print("Erro na execução do script. Arquivo não gerado.")

if arquivos:
    # Ordenar arquivos pela data mais recente
    arquivos.sort(reverse=True, key=lambda x: x[0])
    
    # Pegar arquivo mais recente
    ultimo_arquivo = os.path.join(path_csv, arquivos[0][1])
    
    print(f"Carregando arquivo mais recente: {ultimo_arquivo}")
    
    # Carregar dados
    df_dados = pd.read_csv(ultimo_arquivo, encoding='utf-8', low_memory=False)
    
    print("\nPrimeiras linhas do DataFrame:")
    print(f"\nTotal de registros: {len(df_dados):,}")
    print(f"Data de referência: {arquivos[0][0].strftime('%d/%m/%Y')}")
else:
    print("Nenhum arquivo válido encontrado na pasta")
   
df_dados.head()  


# Remover as linhas onde TP_NOT é 'Total'
df_dados = df_dados[df_dados['TP_NOT'] != 'Total']
print(f"DataFrame atualizado com {df_dados.shape[0]} linhas.")


# Filtrar o DataFrame excluindo as linhas com NDUPLIC_N == 2
df_dados = df_dados[df_dados["NDUPLIC_N"] != 2]

print("Linhas com NDUPLIC_N == 2 foram removidas.")
print(f"DataFrame atualizado com {df_dados.shape[0]} linhas.")

# Verificar colunas com valor constante e seus valores
colunas_constantes = {col: df_dados[col].iloc[0] for col in df_dados.columns if df_dados[col].nunique() == 1}

if colunas_constantes:
    print("Colunas com valor constante e seus respectivos valores:")
    for coluna, valor in colunas_constantes.items():
        print(f"{coluna}: {valor}")
else:
    print("Não há colunas com valores constantes no DataFrame.")


# Dropar as colunas com valor constante
df_dados = df_dados.drop(columns=colunas_constantes)

print(f"Colunas removidas: {colunas_constantes}")
print(f"DataFrame atualizado com {df_dados.shape[1]} colunas.")    


### Investigação de variaveis
# Obter os valores únicos
valores_unicos = df_dados["NU_LOTE_IA"].unique()
valores_unicos[5]



############################################## AVAL_ATU_N ######################################################################
### Tratamento a variavel `AVAL_ATU_N`
# Converter a coluna 'AVAL_ATU_N' para string primeiro
df_dados["AVAL_ATU_N_CAT"] = df_dados['AVAL_ATU_N'].astype(str)

# Criar a nova coluna categorizada
df_dados["AVAL_ATU_N_CAT"] = df_dados['AVAL_ATU_N_CAT'].replace({'nan': '9', 'N': '9'}).astype(int)
df_dados["AVAL_ATU_N_CAT"].value_counts()
#-------------------------------------------------------------------------------------------------------------------------------

############################################## CLASSATUAL ######################################################################
# Converter a coluna 'CLASSATUAL' para string primeiro
df_dados['CLASSATUAL'] = df_dados['CLASSATUAL'].astype(str)

# Criar a nova coluna categorizada
df_dados['CLASSATUAL_CAT'] = df_dados['CLASSATUAL'].replace({'nan': '0', 'N': '0', '9': '0'})
df_dados['CLASSATUAL_CAT'] = df_dados['CLASSATUAL_CAT'].map({'1': 1, '2': 2, '0': 0}).fillna(0).astype(int)
df_dados['CLASSATUAL_CAT'].value_counts()
#-------------------------------------------------------------------------------------------------------------------------------

############################################## NU_IDADE_N ######################################################################
def extrair_idade(valor):
    valor_str = str(valor).zfill(4)
    unidade = int(valor_str[0])
    quantidade = int(valor_str[1:])

    if unidade == 4:  # Anos
        return quantidade, 0
    elif unidade == 3:  # Meses
        if quantidade > 12:
            anos = quantidade // 12
            meses = quantidade % 12
            if meses == 0:  # Se não houver meses restantes, meses = 0
                return anos, 0
            else:
                return anos, meses
        else:
            return 0, quantidade
    elif unidade == 2:  # Dias
        return 0, 1  # Considerando que dias são menores que meses
    elif unidade == 1:  # Horas
        return 0, 1  # Considerando que horas são menores que dias
    else:
        return 0, 0

# Aplicar a função à coluna NU_IDADE_N
df_dados[['IDADE_ANOS', 'IDADE_MESES']] = df_dados['NU_IDADE_N'].apply(
    lambda x: pd.Series(extrair_idade(x))
)
#-------------------------------------------------------------------------------------------------------------------------------

############################################## CS_SEXO ######################################################################
df_dados['CS_SEXO_CAT'] = df_dados['CS_SEXO'].replace({np.nan: 9, 'M': 1, 'F': 2, 'I': 9}).astype(int)
df_dados['CS_SEXO_CAT'].value_counts()
#-------------------------------------------------------------------------------------------------------------------------------

############################################## CS_GESTANT ######################################################################
df_dados['CS_GESTANT_CAT'] = df_dados['CS_GESTANT'].replace({np.nan: 9}).astype(int)

df_dados['CS_GESTANT_CAT'].value_counts()
#-------------------------------------------------------------------------------------------------------------------------------

############################################## CS_RACA ######################################################################
df_dados['CS_RACA_CAT'] = df_dados['CS_RACA'].replace({np.nan: 9}).astype(int)

df_dados['CS_RACA_CAT'].value_counts()
#-------------------------------------------------------------------------------------------------------------------------------

############################################## NU_LESOES ######################################################################
df_dados['NU_LESOES_CAT'] = df_dados['NU_LESOES'].replace(np.nan, 0).astype(int)

df_dados['NU_LESOES_CAT'].value_counts()
#-------------------------------------------------------------------------------------------------------------------------------

############################################## FORMACLINI ######################################################################
df_dados['FORMACLINI_CAT'] = df_dados['FORMACLINI'].replace({np.nan: 5, 0: 5}).astype(int)

df_dados['FORMACLINI_CAT'].value_counts()
#-------------------------------------------------------------------------------------------------------------------------------

############################################## AVALIA_N ######################################################################
df_dados['AVALIA_N_CAT'] = df_dados['AVALIA_N'].replace({np.nan: 3}).astype(int)

df_dados['AVALIA_N_CAT'].value_counts()
#-------------------------------------------------------------------------------------------------------------------------------

############################################## CLASSOPERA ######################################################################
df_dados['CLASSOPERA_CAT'] = df_dados['CLASSOPERA'].replace({np.nan: 3, 9: 3}).astype(int)

df_dados['CLASSOPERA_CAT'].value_counts()
#-------------------------------------------------------------------------------------------------------------------------------

############################################## BACILOSCOP ######################################################################
df_dados['BACILOSCOP_CAT'] = df_dados['BACILOSCOP'].replace({np.nan: 9}).astype(int)

df_dados['BACILOSCOP_CAT'].value_counts()
#-------------------------------------------------------------------------------------------------------------------------------

############################################## ESQ_INI_N ######################################################################
df_dados['ESQ_INI_N_CAT'] = df_dados['ESQ_INI_N'].replace(np.nan, 9).astype(int)

df_dados['ESQ_INI_N_CAT'].value_counts()
#-------------------------------------------------------------------------------------------------------------------------------

############################################## CONTREG ######################################################################
df_dados['CONTREG_CAT'] = df_dados['CONTREG'].replace(np.nan, 0).astype(int)

df_dados['CONTREG_CAT'].value_counts()
#-------------------------------------------------------------------------------------------------------------------------------

############################################## NERVOSAFET ######################################################################
df_dados['NERVOSAFET_CAT'] = df_dados['NERVOSAFET'].replace(np.nan, 0).astype(int)

df_dados['NERVOSAFET_CAT'].value_counts()
#-------------------------------------------------------------------------------------------------------------------------------

############################################## AVAL_ATU_N ######################################################################
df_dados['AVAL_ATU_N_CAT'] = df_dados['AVAL_ATU_N'].replace({np.nan: 9, 'N': 9}).astype(int)

df_dados['AVAL_ATU_N_CAT'].value_counts()
#-------------------------------------------------------------------------------------------------------------------------------

############################################## ESQ_ATU_N ######################################################################
df_dados['ESQ_ATU_N_CAT'] = df_dados['ESQ_ATU_N'].replace({np.nan: 9, 'N': 9}).astype(int)

df_dados['ESQ_ATU_N_CAT'].value_counts()
#-------------------------------------------------------------------------------------------------------------------------------

############################################## DOSE_RECEB ######################################################################
df_dados['DOSE_RECEB_CAT'] = df_dados['DOSE_RECEB'].replace(np.nan, 0).astype(int)

df_dados['DOSE_RECEB_CAT'].value_counts()
#-------------------------------------------------------------------------------------------------------------------------------

##############################################  ######################################################################
df_dados['CLASSOPERA_CAT'] = df_dados['CLASSOPERA'].replace({np.nan: 3, 9: 3}).astype(int)

df_dados['CLASSOPERA_CAT'].value_counts()
#-------------------------------------------------------------------------------------------------------------------------------
############################################## EPIS_RACIO ######################################################################
df_dados['EPIS_RACIO_CAT'] = df_dados['EPIS_RACIO'].replace({np.nan: 9, 'N': 9}).astype(int)

df_dados['EPIS_RACIO_CAT'].value_counts()
#-------------------------------------------------------------------------------------------------------------------------------
############################################## CONTEXAM ######################################################################
df_dados['CONTEXAM_CAT'] = df_dados['CONTEXAM'].replace({np.nan: 0}).astype(int)

df_dados['CONTEXAM_CAT'].value_counts()
#-------------------------------------------------------------------------------------------------------------------------------
##############################################  ######################################################################
df_dados['TPALTA_N_CAT'] = df_dados['TPALTA_N'].replace({np.nan: 9, 'N': 9}).astype(int)

df_dados['TPALTA_N_CAT'].value_counts()
#-------------------------------------------------------------------------------------------------------------------------------



colunas_eliminadas = {"NDUPLIC_N",
                      "ID_UNIDADECS_GESTANT",
                        "SEM_DIAG",
                        "SG_UF",
                        "CS_ESCOL_N",
                        "ID_MN_RESI",
                        "ID_RG_RESI",
                        "ID_PAIS",
                        "NDUPLIC_N",
                        "DT_DIGITA",
                        "DT_TRANSUS",
                        "DT_TRANSDM",
                        "DT_TRANSSM",
                        "DT_TRANSRS",
                        "DT_TRANSSE",
                        "NU_LOTE_V",
                        "NU_LOTE_H",
                        "MIGRADO_W",
                        "ID_OCUPA_N",
                        "IN_VINCULA",
                        "NU_LOTE_IA"
                    }

# Dropar as colunas especificadas
df_dados = df_dados.drop(columns=colunas_eliminadas, errors='ignore')

print(f"As colunas {colunas_eliminadas} foram removidas.")
print(f"O DataFrame agora tem {df_dados.shape[1]} colunas.")

# Selecionar colunas numéricas
numeric_df = df_dados.select_dtypes(include=['number'])
numeric_df.columns

data_atual = datetime.now().strftime('%d_%m_%Y')
nome_arquivo = f"HANSENIASE_PROCESS_{data_atual}.csv"

path_hans = os.path.join(".\\","data", "HANS", nome_arquivo)

# Salvar o DataFrame consolidado
df_dados.to_csv(path_hans, 
                      index=False, 
                      encoding='utf-8')

print(f"Arquivo salvo com sucesso: {nome_arquivo}")
print(f"Total de registros: {len(df_dados):,}")
print(f"Local: {os.path.abspath(nome_arquivo)}")


print("-----------------------------------PROCESSO DE TRATAMENTO FINALIZADO---------------------------")