import pandas as pd
import requests
import os
from tqdm import tqdm
import json
from datetime import datetime
from unidecode import unidecode
import re

def criar_mapa_ibge(caminho_populacao_csv):
    """
    Carrega o arquivo de população e cria um dicionário para mapear
    (NOME_MUNICIPIO_NORMALIZADO, UF) para id_municipio.
    """
    try:
        df_pop = pd.read_csv(caminho_populacao_csv)
        df_pop = df_pop.sort_values('ano').drop_duplicates('id_municipio', keep='last')
        mapa = {
            f"{unidecode(str(row['nome_municipio'])).upper().strip()}_{row['sigla_uf'].upper()}": row['id_municipio']
            for _, row in df_pop.iterrows()
        }
        print(f"Mapa de municípios do IBGE criado com sucesso com {len(mapa)} entradas.")
        return mapa
    except FileNotFoundError:
        print(f"ERRO: Arquivo de população '{caminho_populacao_csv}' não encontrado.")
        return None

def baixar_e_processar_dados_antt_corrigido_final():
    """
    SCRIPT FINAL CORRIGIDO: Corrige o typo no ID do dataset para garantir o
    acesso correto à API da ANTT.
    """
    mapa_ibge = criar_mapa_ibge('.\\data\\IBGE\\populacao_municipios.csv')
    if mapa_ibge is None: return

    print("\nETAPA 1: Buscando lista de arquivos via API da ANTT...")
    # A CORREÇÃO ESTÁ AQUI: O hífen em '6327' foi restaurado.
    dataset_id = "989414bc-6327-4a1c-be47-22ba31a9d271"
    api_url = f"https://dados.antt.gov.br/api/3/action/package_show?id={dataset_id}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        dataset_info = response.json()
        resources = dataset_info['result']['resources']
        all_urls = sorted([res['url'] for res in resources if res.get('url') and 'venda_passagem' in res['url'] and res['url'].lower().endswith('.csv')])
        
        ano_atual = datetime.now().year
        mes_atual = datetime.now().month
        file_urls = []
        for url in all_urls:
            match = re.search(r'venda_passagem_(\d{2})_(\d{4})\.csv', url, re.IGNORECASE)
            if match:
                mes, ano = int(match.group(1)), int(match.group(2))
                if ano < ano_atual or (ano == ano_atual and mes < mes_atual):
                     file_urls.append(url)
        
        print(f"Sucesso! Encontrados {len(file_urls)} arquivos com dados válidos para processar.")
    except Exception as e:
        print(f"ERRO na Etapa 1: {e}")
        return

    print("\nETAPA 2: Iniciando download, processamento e tradução para códigos IBGE...")
    lista_de_dataframes_finais = []

    for url in tqdm(file_urls, desc="Processando arquivos ANTT"):
        try:
            match = re.search(r'venda_passagem_(\d{2})_(\d{4})\.csv', url, re.IGNORECASE)
            if not match: continue
            mes, ano = int(match.group(1)), int(match.group(2))
            
            df_mes = pd.read_csv(url, sep=None, engine='python', encoding='latin1')
            
            if df_mes.empty: continue

            df_mes.columns = [unidecode(str(col).lower().strip()) for col in df_mes.columns]
            df_mes.rename(columns={'ponto_origem_viagem': 'origem_nome_uf', 'ponto_destino_viagem': 'destino_nome_uf', 'quantidade_bilhetes': 'fluxo_passageiros'}, inplace=True)

            if not all(col in df_mes.columns for col in ['origem_nome_uf', 'destino_nome_uf', 'fluxo_passageiros']):
                continue
            
            df_mes = df_mes[['origem_nome_uf', 'destino_nome_uf', 'fluxo_passageiros']].copy()
            df_mes.dropna(inplace=True)

            def criar_chave_antt(ponto_viagem):
                s = str(ponto_viagem).split('(')[0].split(' - ')[0].strip()
                parts = s.split('/')
                if len(parts) != 2: return None
                nome = unidecode(parts[0]).upper().strip()
                uf = parts[1].upper().strip()
                return f"{nome}_{uf}"
            
            df_mes['chave_origem'] = df_mes['origem_nome_uf'].apply(criar_chave_antt)
            df_mes['chave_destino'] = df_mes['destino_nome_uf'].apply(criar_chave_antt)
            df_mes['id_municipio_origem'] = df_mes['chave_origem'].map(mapa_ibge)
            df_mes['id_municipio_destino'] = df_mes['chave_destino'].map(mapa_ibge)
            df_mes['ano'], df_mes['mes'] = ano, mes

            df_final_mes = df_mes[['ano', 'mes', 'id_municipio_origem', 'id_municipio_destino', 'fluxo_passageiros']].copy()
            df_final_mes.dropna(inplace=True)
            if df_final_mes.empty: continue

            df_final_mes = df_final_mes.astype({'id_municipio_origem': 'int64', 'id_municipio_destino': 'int64', 'fluxo_passageiros': 'int64'})
            lista_de_dataframes_finais.append(df_final_mes)
        except Exception:
            pass

    if not lista_de_dataframes_finais:
        print("\nNenhum dado foi processado com sucesso. A correspondência de nomes de municípios ainda pode estar falhando.")
        return

    print("\nETAPA 3: Consolidando todos os dados em um arquivo final...")
    df_final = pd.concat(lista_de_dataframes_finais, ignore_index=True)
    df_final_agrupado = df_final.groupby(['ano', 'mes', 'id_municipio_origem', 'id_municipio_destino'], as_index=False)['fluxo_passageiros'].sum()

    output_dir = os.path.join('data', 'MOBILIDADE', 'ANTT')
    final_csv_path = os.path.join(output_dir, 'dados_rodoviarios_consolidados_com_ibge.csv')
    os.makedirs(output_dir, exist_ok=True)
    df_final_agrupado.to_csv(final_csv_path, index=False)

    print("\n--- PROCESSO CONCLUÍDO COM SUCESSO! ---")
    print(f"Total de registros de fluxo (origem-destino-mês) com código IBGE: {len(df_final_agrupado)}")
    print(f"Arquivo final salvo em: {final_csv_path}")
    print("\nPré-visualização dos dados finais:")
    print(df_final_agrupado.head())

if __name__ == '__main__':
    baixar_e_processar_dados_antt_corrigido_final()