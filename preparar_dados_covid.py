import pandas as pd
from pathlib import Path

def preparar_dados_reais_covid():
    """
    Baixa os dados compilados da COVID-19 do Brasil.IO e extrai a data do
    primeiro caso para cada município, salvando em um formato compatível
    com o nosso projeto (código IBGE de 6 dígitos).
    """
    print("--- INICIANDO PREPARAÇÃO DOS DADOS REAIS DA COVID-19 ---")
    
    url_brasil_io = "https://data.brasil.io/dataset/covid19/caso_full.csv.gz"
    
    try:
        print(f"Baixando e lendo os dados de: {url_brasil_io}")
        
        # CORREÇÃO APLICADA AQUI: Usando o novo nome da coluna 'last_available_confirmed'
        colunas_para_ler = ['city_ibge_code', 'date', 'last_available_confirmed']
        
        df_covid = pd.read_csv(
            url_brasil_io,
            usecols=colunas_para_ler,
            parse_dates=['date']
        )
        print("Download e leitura concluídos.")

        # CORREÇÃO APLICADA AQUI: Filtrando pela nova coluna
        df_covid_com_casos = df_covid[df_covid['last_available_confirmed'] > 0].copy()

        print("Encontrando a data do primeiro caso para cada município...")
        df_primeiros_casos = df_covid_com_casos.groupby('city_ibge_code')['date'].min().reset_index()

        df_primeiros_casos.rename(columns={
            'city_ibge_code': 'id_municipio',
            'date': 'data_primeiro_caso'
        }, inplace=True)
        
        print("Harmonizando os códigos de município para 6 dígitos...")
        df_primeiros_casos.dropna(subset=['id_municipio'], inplace=True)
        df_primeiros_casos['id_municipio'] = df_primeiros_casos['id_municipio'].astype(int)
        df_primeiros_casos['id_municipio'] = df_primeiros_casos['id_municipio'] // 10

        output_path = Path('data') / 'MOBILIDADE' / 'covid_primeiros_casos.csv'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        df_primeiros_casos.to_csv(output_path, index=False)
        
        print("\n--- SUCESSO! ---")
        print(f"Arquivo '{output_path}' criado com sucesso.")
        print(f"Total de municípios com dados de primeiro caso: {len(df_primeiros_casos)}")
        print("\nPré-visualização dos dados:")
        print(df_primeiros_casos.head())
        print("\nAgora você pode adaptar o script '5_validacao_covid19.py' para usar este arquivo.")

    except Exception as e:
        print(f"\nOcorreu um erro: {e}")
        print("Verifique sua conexão com a internet ou se o link/formato do Brasil.IO mudou novamente.")

if __name__ == '__main__':
    preparar_dados_reais_covid()