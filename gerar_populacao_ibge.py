'''
--------Lembrar de instalar as bibliotecas---------
pip install sidrapy
'''
import os
from pathlib import Path
import requests
import sidrapy
import pandas as pd

# https://dkko.me/posts/coletando-ibge-sidra-populacao-municipios/

def get_periodos(agregado: str):
    url = f"https://servicodados.ibge.gov.br/api/v3/agregados/{agregado}/periodos"
    response = requests.get(url)
    return response.json()

def download_table(
    sidra_tabela: str,
    territorial_level: str,
    ibge_territorial_code: str,
    variable: str = "allxp",
    classifications: dict = None,
    data_dir: Path = Path("data"),
) -> list[Path]:
    """Download a SIDRA table in CSV format on temp_dir()

    Args:
        sidra_tabela (str): SIDRA table code
        territorial_level (str): territorial level code
        ibge_territorial_code (str): IBGE territorial code
        variable (str, optional): variable code. Defaults to None.
        classifications (dict, optional): classifications and categories codes.
            Defaults to None.

    Returns:
        list[Path]: list of downloaded files
    """
    filepaths = []
    periodos = get_periodos(sidra_tabela)
    for periodo in periodos:
        filename = f"{periodo['id']}.csv"
        dest_filepath = data_dir / filename
        dest_filepath.parent.mkdir(exist_ok=True, parents=True)
        if dest_filepath.exists():
            print("File already exists:", dest_filepath)
            continue
        print("Downloading", filename)
        df = sidrapy.get_table(
            table_code=sidra_tabela,  # Tabela SIDRA
            territorial_level=territorial_level,  # Nível de Municípios
            ibge_territorial_code=ibge_territorial_code,  # Territórios
            period=periodo["id"],  # Período
            variable=variable,  # Variáveis
            classifications=classifications,
        )
        df.to_csv(dest_filepath, index=False, encoding="utf-8")
        filepaths.append(dest_filepath)
    return filepaths

data_dir = Path("data/IBGE")
data_dir.mkdir(parents=True, exist_ok=True)
files = []


#### População dos Censos 1970, 1980, 1991, 2000 e 2010 (Tabela 200)

# Populacao Censos
sidra_tabela = "200"
territorial_level = "6"
ibge_territorial_code = "all"

files_census = download_table(
    sidra_tabela=sidra_tabela,
    territorial_level=territorial_level,
    ibge_territorial_code=ibge_territorial_code,
    variable="allxp",
    classifications={"2": "0", "1": "0", "58": "0"},
    data_dir=data_dir,
)
files.extend(files_census)


#### População dos municípios do Brasil em 2022 (Tabela 9514)
# Populacao Censo 2022
sidra_tabela = "9514"
territorial_level = "6"
ibge_territorial_code = "all"

files_census_2022 = download_table(
    sidra_tabela=sidra_tabela,
    territorial_level=territorial_level,
    ibge_territorial_code=ibge_territorial_code,
    variable="allxp",
    classifications={"2": "6794", "287": "100362", "286": "113635"},
    data_dir=data_dir,
)
files.extend(files_census_2022)


#### População das Contagens (Tabelas 305 e 793)

# Populacao Contagens
sidra_tabelas = (
    "305",
    "793",
)

for sidra_tabela in sidra_tabelas:
    files_counts = download_table(
        sidra_tabela=sidra_tabela,
        territorial_level=territorial_level,
        ibge_territorial_code=ibge_territorial_code,
        data_dir=data_dir,
    )
    files.extend(files_counts)


#### Populacao Estimativas (Tabela 6579)
# Populacao Estimativas
sidra_tabela = "6579"

files_estimates = download_table(
    sidra_tabela=sidra_tabela,
    territorial_level=territorial_level,
    ibge_territorial_code=ibge_territorial_code,
    data_dir=data_dir,
)
files.extend(files_estimates)

def read_file(filepath: Path, **read_csv_args) -> pd.DataFrame:
    print("Reading file", filepath)
    data = pd.read_csv(filepath, skiprows=1, na_values=["...", "-"], **read_csv_args)
    data = data.dropna(subset="Valor")
    return data

def refine(df: pd.DataFrame) -> pd.DataFrame:
    df = (
        df.dropna(subset="Valor")
        .rename(
            columns={
                "Ano": "ano",
                "Município (Código)": "id_municipio",
                "Valor": "pessoas",
            }
        )
        .assign(pessoas=lambda x: x["pessoas"].astype(int))
    )
    df[["nome_municipio", "sigla_uf"]] = df["Município"].str.split(" - ", expand=True)
    df = df.drop(columns="Município")
    df = df[["ano", "id_municipio", "nome_municipio", "sigla_uf", "pessoas"]]
    return df

if files:
    df = refine(
        pd.concat(
            (
                read_file(file, usecols=("Ano", "Município (Código)", "Município", "Valor"))
                for file in files
            ),
            ignore_index=True,
        )
    )


    df.head()
    df.info()

    #### Salvando os dados de todos os anos em um único arquivo
    df.to_csv("populacao_municipios.csv", index=False, encoding="utf-8")