import pandas as pd
import requests
import zipfile
import io
import os
from datetime import datetime
from tqdm import tqdm # Para uma barra de progresso amigável

def baixar_e_processar_dados_anac():
    """
    Baixa, extrai, limpa e consolida os microdados de voos da ANAC.
    """
    
    # --- 1. Configuração ---
    base_url = "https://www.gov.br/anac/pt-br/assuntos/regulados/empresas-aereas/Instrucoes-para-a-elaboracao-e-apresentacao-das-demonstracoes-contabeis/envio-de-informacoes/basica/{ano}/basica{ano}-{mes:02d}.zip"
    
    # Diretório de saída para o arquivo final
    output_dir = os.path.join('data', 'MOBILIDADE')
    final_csv_path = os.path.join(output_dir, 'dados_aereos_consolidados.csv')

    # Cria o diretório se ele não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # Colunas que realmente importam para a análise de mobilidade (fluxo)
    colunas_relevantes = [
        'nr_ano_partida_real', 
        'nr_mes_partida_real', 
        'dt_partida_real',
        'nm_municipio_origem', 
        'sg_uf_origem', 
        'nm_municipio_destino', 
        'sg_uf_destino', 
        'nr_passag_pagos' # Essencial para medir o fluxo
    ]

    # Lista para armazenar os DataFrames de cada mês
    lista_de_dataframes = []

    # --- 2. Loop de Download e Processamento ---
    
    # Define o período dinamicamente para não baixar arquivos futuros
    ano_inicial = 2000
    ano_atual = datetime.now().year
    mes_atual = datetime.now().month

    # Gerando a lista de anos e meses para a barra de progresso
    tarefas = []
    for ano in range(ano_inicial, ano_atual + 1):
        # O último ano vai até o mês atual, os outros vão até 12
        limite_mes = mes_atual if ano == ano_atual else 12
        for mes in range(1, limite_mes + 1):
            tarefas.append((ano, mes))

    print(f"Iniciando download e processamento de {len(tarefas)} arquivos da ANAC (de {ano_inicial}-01 a {ano_atual}-{mes_atual})...")
    print(f"Os dados consolidados serão salvos em: {final_csv_path}")

    for ano, mes in tqdm(tarefas, desc="Processando arquivos mensais"):
        
        url = base_url.format(ano=ano, mes=mes)

        try:
            # Faz o request para baixar o arquivo
            response = requests.get(url, timeout=30)
            
            # Se o arquivo não for encontrado (comum para meses futuros ou falhas no site), pula para o próximo
            if response.status_code == 404:
                # print(f"AVISO: Arquivo para {ano}-{mes:02d} não encontrado (URL: {url}). Pulando.")
                continue
            
            # Garante que o request foi bem-sucedido
            response.raise_for_status()

            # Usa BytesIO para tratar o conteúdo baixado como um arquivo em memória
            zip_buffer = io.BytesIO(response.content)

            with zipfile.ZipFile(zip_buffer) as z:
                # Pega o nome do primeiro arquivo CSV dentro do ZIP
                nome_csv = z.namelist()[0]
                
                with z.open(nome_csv) as csv_file:
                    # Lê o CSV com Pandas, selecionando apenas as colunas de interesse
                    # A codificação 'latin1' é comum em arquivos de órgãos brasileiros
                    df_mes = pd.read_csv(
                        csv_file, 
                        sep=';', 
                        encoding='latin1',
                        usecols=lambda col: col in colunas_relevantes,
                        low_memory=False
                    )
                    
                    # Adiciona o DataFrame à nossa lista
                    lista_de_dataframes.append(df_mes)

        except requests.exceptions.RequestException as e:
            print(f"\nERRO de conexão ao tentar baixar {url}. Pulando. Erro: {e}")
        except (zipfile.BadZipFile, IndexError):
            print(f"\nERRO: O arquivo baixado de {url} não é um ZIP válido ou está vazio. Pulando.")
        except Exception as e:
            print(f"\nERRO inesperado ao processar o arquivo de {ano}-{mes:02d}. Pulando. Erro: {e}")


    # --- 3. Consolidação e Salvamento ---
    if not lista_de_dataframes:
        print("\nNenhum dado foi baixado. Verifique a conexão ou as URLs. Encerrando.")
        return

    print("\nConsolidando todos os dados em um único arquivo...")
    
    # Concatena todos os DataFrames da lista em um só
    df_final = pd.concat(lista_de_dataframes, ignore_index=True)

    # Limpeza final: remover voos sem informação de passageiros ou município
    df_final.dropna(
        subset=['nr_passag_pagos', 'nm_municipio_origem', 'nm_municipio_destino'], 
        inplace=True
    )
    # Garante que os passageiros sejam tratados como números inteiros
    df_final['nr_passag_pagos'] = df_final['nr_passag_pagos'].astype(int)

    # Salva o arquivo final em formato CSV
    df_final.to_csv(final_csv_path, index=False)

    print("\n--- Processo Concluído com Sucesso! ---")
    print(f"Total de registros de voos processados: {len(df_final)}")
    print(f"Arquivo salvo em: {final_csv_path}")
    print("\nPré-visualização dos dados:")
    print(df_final.head())
    print("\nInformações do DataFrame final:")
    df_final.info()


if __name__ == '__main__':
    baixar_e_processar_dados_anac()