import os
import pandas as pd
from datasus_dbc import decompress
from dbfread import DBF
from datetime import datetime

def ler_dbc_seguro(caminho_arquivo):
    """Função robusta para processar arquivos .dbc com tratamento de erros"""
    try:
        # Gera caminho temporário único
        temp_dbf = os.path.join(os.getcwd(), f"temp_{os.urandom(4).hex()}.dbf")
        
        # Descompressão usando a assinatura correta
        decompress(caminho_arquivo, temp_dbf)  # Corrigido: dois argumentos
        
        # Leitura do DBF resultante
        return pd.DataFrame(DBF(temp_dbf, encoding='iso-8859-1'))
    
    except Exception as e:
        print(f"Erro crítico em {os.path.basename(caminho_arquivo)}: {str(e)}")
        return pd.DataFrame()
    
    finally:
        # Limpeza segura do arquivo temporário
        if 'temp_dbf' in locals() and os.path.exists(temp_dbf):
            os.remove(temp_dbf)

# Processamento dos arquivos
print("-----------------------------------PROCESSO DE CONVERSÃO E CRIAÇÃO DE ARQUIVO CSV---------------------------")
diretorio_base = os.path.join(".", "data", "HANS")
arquivos = [f for f in os.listdir(diretorio_base) if f.startswith('HANSBR') and f.endswith('.dbc')]

dados_completos = pd.concat(
    [ler_dbc_seguro(os.path.join(diretorio_base, arquivo)) for arquivo in arquivos],
    ignore_index=True
)

if not dados_completos.empty:
    print(f"Dados carregados com sucesso! ({len(dados_completos)} registros)")
    print(dados_completos.head())
else:
    print("Nenhum dado válido processado")


dados_completos.head()


## Salvando os dados em .csv

# Gerar nome do arquivo com data atual
data_atual = datetime.now().strftime('%d_%m_%Y')
nome_arquivo = f"HANSENIASE_TOTAL_{data_atual}.csv"

path_hans = os.path.join(".", "data", "HANSENIASE", nome_arquivo)
os.makedirs(os.path.dirname(path_hans), exist_ok=True)

# Salvar o DataFrame consolidado
dados_completos.to_csv(path_hans, 
                      index=False, 
                      encoding='utf-8')

print(f"Arquivo salvo com sucesso: {nome_arquivo}")
print(f"Total de registros: {len(dados_completos):,}")
print(f"Local: {os.path.abspath(path_hans)}")


print("-----------------------------------PROCESSO DE CONVERSÃO FINALIZADO---------------------------")
