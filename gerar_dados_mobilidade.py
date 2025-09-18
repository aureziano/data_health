# -*- coding: utf-8 -*-
"""
Script para baixar e filtrar dados de mobilidade usando IDs de municípios,
UF e região da sua tabela `populacao_municipios.csv`, com tratamento de erros
para arquivos ausentes ou com formato inesperado.
"""

import requests
import pandas as pd
from pathlib import Path

print("--- INICIANDO SCRIPT ---")

BASE_DIR = Path("./data/MOBILIDADE")
BASE_DIR.mkdir(parents=True, exist_ok=True)

def get_regioes_municipios():
    """
    Busca dados de todos os municípios do Brasil, incluindo ID, nome e região,
    e retorna um DataFrame do Pandas.
    """
    print("--- BUSCANDO DADOS DE REGIÕES DOS MUNICÍPIOS ---")
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios?orderBy=nome"
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        municipios_json = response.json()
        municipios_lista = []
        for municipio in municipios_json:
            try:
                regiao = municipio['microrregiao']['mesorregiao']['UF']['regiao']['nome']
                municipios_lista.append({
                    'id_municipio': str(municipio['id']),
                    'regiao': regiao
                })
            except (KeyError, TypeError):
                # Handle cases where the nested structure is not as expected
                # For example, Brasília (ID 5300108) does not have a microrregiao
                if str(municipio.get('id')) == '5300108':
                    municipios_lista.append({
                        'id_municipio': str(municipio['id']),
                        'regiao': 'Centro-Oeste'
                    })
                else:
                    print(f"Warning: Dados de região não encontrados para o município ID {municipio.get('id')}")
                continue
        print("--- DADOS DE REGIÕES CARREGADOS ---")
        return pd.DataFrame(municipios_lista)
    except requests.exceptions.RequestException as e:
        print(f"--- ERRO AO BUSCAR DADOS DE REGIÕES: {e} ---")
        return pd.DataFrame()

# 1) Carrega referência de municípios
print("--- CARREGANDO DADOS DE MUNICÍPIOS ---")
mun_ref = pd.read_csv(
    "./data/IBGE/populacao_municipios.csv",
    dtype={"id_municipio": str}
)

# Adiciona dados de região
regioes_df = get_regioes_municipios()
if not regioes_df.empty:
    mun_ref = pd.merge(mun_ref, regioes_df, on='id_municipio', how='left')

# Adiciona uma coluna com o nome do município em maiúsculas para o merge
mun_ref['municipio_upper'] = mun_ref['nome_municipio'].str.upper()
print("--- DADOS DE MUNICÍPIOS CARREGADOS ---")

# 2) URLs corretas dos datasets
URLS = {
    "anac_voos.csv": "https://siros.anac.gov.br/siros/registros/registros/registros.csv",
}

# 3) Download com tratamento de 404
def download(url: str, dest: Path):
    print(f"--- VERIFICANDO DOWNLOAD PARA {dest.name} ---")
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        print(f"--- ARQUIVO {dest.name} JÁ EXISTE ---")
        return
    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        dest.write_bytes(resp.content)
        print(f"Baixado: {dest.name}")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"Não encontrado (404): {dest.name}")
        else:
            raise

print("--- INICIANDO DOWNLOADS ---")
for fname, url in URLS.items():
    download(url, BASE_DIR / fname)
print("--- DOWNLOADS FINALIZADOS ---")

# 4) Função de filtragem e merge
def filtrar(path: Path, cols_loc: list[str]) -> pd.DataFrame:
    print(f"--- INICIANDO FILTRAGEM PARA {path.name} ---")
    try:
        df = pd.read_csv(path, dtype=str, low_memory=False, sep=";", skiprows=1, encoding='utf-8')
        print(f"--- ARQUIVO {path.name} LIDO COM SUCESSO ---")
    except Exception as e:
        print(f"Erro ao ler o arquivo {path.name}: {e}")
        return pd.DataFrame()

    if df.empty:
        return pd.DataFrame()

    all_municipios = pd.Series(dtype=str)
    for col in cols_loc:
        if col in df.columns:
            # Extrai o nome do município da coluna de localização
            print(f"--- EXTRAINDO MUNICÍPIOS DE {col} ---")
            # Attempt to extract municipality name more robustly
            extracted_municipios = []
            for entry in df[col].dropna():
                found_municipio = None
                # Try to find a known municipality name within the entry
                for mun_name in mun_ref['nome_municipio'].str.upper().unique():
                    if mun_name in entry.upper():
                        found_municipio = mun_name
                        break
                if found_municipio:
                    extracted_municipios.append(found_municipio)
                else:
                    # Fallback to original splitting logic if no direct match
                    split_parts = entry.split(' - ')
                    if split_parts:
                        extracted_municipios.append(split_parts[0])
                    else:
                        extracted_municipios.append(entry) # Append original if no split possible
            municipios = pd.Series(extracted_municipios)
            all_municipios = pd.concat([all_municipios, municipios], ignore_index=True)
        else:
            print(f"Coluna {col} não encontrada em {path.name}")

    all_municipios = all_municipios.dropna().unique()
    print("--- MUNICÍPIOS ÚNICOS EXTRAÍDOS ---")

    # Cria um DataFrame com os nomes dos municípios
    df_municipios = pd.DataFrame(all_municipios, columns=['municipio_upper'])

    # Merge para encontrar o id_municipio
    print("--- REALIZANDO MERGE COM DADOS DE MUNICÍPIOS ---")
    # Ensure 'municipio_upper' in mun_ref is unique for merge stability
    mun_ref_unique = mun_ref.drop_duplicates(subset=['municipio_upper'])
    merged_df = df_municipios.merge(
        mun_ref_unique[['municipio_upper', 'id_municipio', 'sigla_uf', 'regiao']],
        on="municipio_upper",
        how="inner"
    )
    print("--- MERGE FINALIZADO ---")

    return merged_df[['id_municipio', 'sigla_uf', 'regiao']]


# 5) Definição de colunas de ID
CAMPO_POR_ARQ = {
    "anac_voos.csv":         ["Arpt Origem", "Arpt Destino"],
}

# 6) Processamento com tratamento de erros de parser
print("--- INICIANDO PROCESSAMENTO DOS ARQUIVOS ---")
for fname, keys in CAMPO_POR_ARQ.items():
    in_path = BASE_DIR / fname
    if not in_path.is_file():
        print(f"Arquivo ausente: {fname}")
        continue

    try:
        df_filtered = filtrar(in_path, keys)
        if not df_filtered.empty:
            out_path = BASE_DIR / f"filtro_{fname}"
            df_filtered.to_csv(out_path, index=False, encoding="utf-8")
            print(f"Filtrado: {out_path.name} -> {len(df_filtered)} registros")
        else:
            print(f"Nenhum dado filtrado para {fname}")

    except Exception as e:
        print(f"Outro erro em {fname}: {e}")
        continue

print("------- PROCESSO DE TRATAMENTO FINALIZADO -------")