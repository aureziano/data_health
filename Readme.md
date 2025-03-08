# Ambiente Virtual Python e Análise de Dados do DATASUS

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![DATASUS](https://img.shields.io/badge/DATASUS-2F80ED?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxZW0iIGhlaWdodD0iMWVtIiB2aWV3Qm94PSIwIDAgMjQgMjQiPjxwYXRoIGZpbGw9IndoaXRlIiBkPSJNMTkuMzUgMTAuMDRBNy40OSA3LjQ5IDAgMCAwIDEyIDRDOS4xMSA0IDYuNiA1LjY0IDUuMzUgOC4wNEEzLjk5OSAzLjk5OSAwIDAgMCAyIDEyYzAgMi4yMSAxLjc5IDQgNCA0aDEzYzIuMjEgMCA0LTEuNzkgNC00YzAtMi4yMS0xLjc5LTQtNC00eiIvPjwvc3ZnPg==&logoColor=white)
![IBGE](https://img.shields.io/badge/IBGE-2D5BBB?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxZW0iIGhlaWdodD0iMWVtIiB2aWV3Qm94PSIwIDAgMjQgMjQiPjxwYXRoIGZpbGw9IndoaXRlIiBkPSJNMTIgMkM2LjQ4IDIgMiA2LjQ4IDIgMTJzNC40OCAxMCAxMCAxMHMxMC00LjQ4IDEwLTEwUzE3LjUyIDIgMTIgMnptMCAxOGMtNC40MSAwLTgtMy41OS04LThzMy41OS04IDgtOHM4IDMuNTkgOCA4cy0zLjU5IDgtOCA4eiIvPjwvc3ZnPg==&logoColor=white)
![Machine Learning](https://img.shields.io/badge/Machine_Learning-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)
![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-yellow?style=for-the-badge)


Este projeto visa analisar dados do DATASUS relacionados à Hanseníase, integrando-os com informações demográficas do IBGE para análises estatísticas e aplicação de modelos de machine learning.

## Configuração do Ambiente Virtual

### Criação do ambiente

```bash
python -m venv .\venv_healt
```

### Ativação do ambiente

#### No Windows

```bash
.\venv_healt\Scripts\activate
```

#### No Linux

```bash
source ./venv_healt/bin/activate
```

### Desativar ambiente

```bash
deactivate
```

## Gerenciamento de Dependências

### Instalar Dependências

```bash
pip install -r requirements.txt
```

### Criar Arquivo de Dependências

```bash
pip freeze > requirements.txt
```

## Obtenção e Processamento de Dados do DATASUS

### Fonte de Dados
Os dados foram obtidos da página do DATASUS (https://datasus.saude.gov.br/transferencia-de-arquivos/#) com os seguintes parâmetros:

- **Fonte**: SINAN - Sistema de Informações de Agravos de Notificação
- **Modalidade**: Dados
- **Tipo de Arquivo**: HANS - Hanseníase
- **Ano**: Todos
- **UF**: BR

### Conversão de Arquivos DBC para DataFrame

Instalação das bibliotecas necessárias:

```bash
pip install pandas datasus-dbc dbfread
```

O processo de conversão está detalhado no notebook [convert_dbc.ipynb](convert_dbc.ipynb).

## Integração com Dados do IBGE

### API SIDRA

A API SIDRA fornece acesso a dados populacionais como censos e estimativas.

```bash
pip install sidrapy
```

Exemplo de uso:

```python
import sidrapy
```

Detalhes sobre a utilização estão no arquivo [populacao_ibge.ipynb](populacao_ibge.ipynb).

### Biblioteca IBGE

Fornece informações sobre estados e municípios para associação por região e código.

```bash
pip install ibge
```

Exemplo de uso:

```python
from ibge.localidades import *

# Buscar informações dos estados
dados_estados = Estados()
dt_est = dados_estados.json_ibge
print(dt_est[17])
```

Resultado:
```
{'id': 32, 'sigla': 'ES', 'nome': 'Espírito Santo', 'regiao': {'id': 3, 'sigla': 'SE', 'nome': 'Sudeste'}}
```

Mais informações sobre esta biblioteca em [wsus_ibge.ipynb](wsus_ibge.ipynb).

## Análises e Modelos de Machine Learning

### Modelos Implementados

O notebook [wsus_ml.ipynb](wsus_ml.ipynb) contém implementações de:

- **Clusterização**
- **PCA (Análise de Componentes Principais)**
- **Modelos de Predição**:
  - Séries Temporais (LSTM, Redes Neurais)
  - ARIMA e SARIMA
  - Prophet
  - XGBoost
  - MLP (Multilayer Perceptron)
  - SVR (Support Vector Regression)
  - Random Forest

### Análises Adicionais

- **Testes Gerais**: [wsus.ipynb](wsus.ipynb)
- **Análise de Variáveis e Correlações**: [wsus_correlacao.ipynb](wsus_correlacao.ipynb)

## Documentação

- **Documentação do WSUS**: [Documentacao](docs/Documentacao.md)
- **Documentação do Tratamento de Variáveis**: [Tratamento](docs/tratamentos.md)

---

Este projeto está em desenvolvimento contínuo, com atualizações regulares de funcionalidades e melhorias na análise de dados.

Citations:
[1] https://docs.python.org/3/library/venv.html
[2] https://pydigger.com/pypi/datasus-db
[3] https://octave.sourceforge.io/io/function/dbfread.html
[4] https://github.com/AlanTaranti/sidrapy
[5] https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais/28971-base-de-faces-de-logradouros-do-brasil.html
[6] https://aclanthology.org/C18-1061/
[7] https://www.alura.com.br/artigos/redes-neurais
[8] https://stackoverflow.com/questions/64207964/venv-base-both-active-on-a-python-project-how-do-i-get-into-venv-only
[9] https://github.com/Ileriayo/markdown-badges
[10] https://github.com/mymatsubara/datasus-dbc
[11] https://github.com/olemb/dbfread
[12] https://sidrapy.readthedocs.io/pt-br/latest/modules/table.html
[13] https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais/15774-malhas.html
[14] https://arxiv.org/abs/2408.10006
[15] https://www.sas.com/pt_br/insights/analytics/neural-networks.html
[16] https://docs.python.org/pt-br/dev/library/venv.html
[17] https://shields.io
[18] http://siab.datasus.gov.br/DATASUS/index.php?area=060805&item=6
[19] https://stackoverflow.com/questions/53877645/dbfreader-python-3-7-issues
[20] https://shop.wwf.org.uk/products/panda-face-pin-badge-1
