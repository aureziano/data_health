# Leprosy Precision Surveillance - Shiny App

Esta é a ferramenta interativa que acompanha a dissertação de Mestrado. Ela transforma os modelos preditivos e a análise de séries temporais em uma aplicação prática de suporte à decisão.

## Funcionalidades
1. **Calculadora de Risco (G2D)**: Baseada no modelo LightGBM, estima a probabilidade de um paciente apresentar Grau 2 de Incapacidade Física com base em suas características clínicas.
2. **Dashboard de Monitoramento**: Visualização interativa da subnotificação pandêmica e da reabsorção do backlog (2020-2024).

## Como Instalar e Rodar

### 1. Instalar Dependências
No seu terminal (dentro do ambiente virtual), execute:
```bash
pip install -r shiny/requirements_shiny.txt
```

### 2. Rodar a Aplicação
Execute o comando abaixo para iniciar o servidor local:
```bash
shiny run shiny/app.py
```

A aplicação abrirá no seu navegador, geralmente no endereço `http://127.0.0.1:8000`.

### 3. Rodar via Docker (Recomendado para Produção)
Se você tiver o Docker instalado, pode rodar o ambiente isolado:
```bash
docker-compose -f shiny/docker-compose.yml up --build
```

## Como usar no Shiny Posit Cloud
Para hospedar sua aplicação gratuitamente ou em ambientes profissionais no [Shiny Posit](https://shiny.posit.co/py/):
1.  **Crie uma conta** em [shinyapps.io](https://www.shinyapps.io/).
2.  Instale o conector: `pip install rsconnect-python`
3.  Faça o deploy via terminal:
    ```bash
    rsconnect deploy shiny shiny/app.py --name seu-nome-app
    ```
4.  Certifique-se de que os arquivos `.joblib` e `.csv` estejam no mesmo diretório do `app.py`, pois o Posit irá empacotá-los juntos.

## Estrutura da Pasta
- `app.py`: Interface e lógica do servidor.
- `model_risk.joblib`: Modelo LightGBM pré-treinado.
- `dashboard_data.csv`: Dados agregados para visualização temporal.
- `docker-compose.yml`: Configuração de execução em container.
- `Dockerfile`: Definição da imagem de aplicação.
- `prepare_model.py`: Script original de treinamento (caso precise regerar o modelo).
