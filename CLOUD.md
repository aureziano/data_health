# Especificações do Artigo - Modelagem Espaço-Temporal da Hanseníase no Brasil

## 1. Metadados do Artigo

### Título
**Modelagem e Predição Espaço-Temporal da Hanseníase no Brasil: Uma Abordagem Integrada de Redes de Mobilidade Humana e Fatores Socioambientais**

### Subtítulo (Versão Alternativa)
**Uma Abordagem Híbrida para Modelagem da Hanseníase: Combinando Análise de Redes, Séries Temporais Históricas e Machine Learning**

### Journal-Alvo
Computational Statistics & Data Analysis

### Palavras-chave
Hanseníase | Mobilidade Humana | Modelagem Espaço-Temporal | Aprendizado de Máquina | Vigilância em Saúde | Big Data

### Autores
[Autores] - Centro de Integração de Dados e Conhecimentos para a Saúde (CIDACS), Fiocruz

### Afiliações
- **CIDACS**: Centro de Integração de Dados e Conhecimentos para a Saúde (CIDACS), Instituto Gonçalo Moniz, Fundação Oswaldo Cruz (Fiocruz), Salvador, Bahia, Brasil
- **MeSP2**: Laboratório de Medicina e Saúde Pública de Precisão (MeSP2), Instituto Gonçalo Moniz, Fundação Oswaldo Cruz (Fiocruz), Salvador, Bahia, Brasil
- **COPPE/UFRJ**: Luiz Coimbra Institute of Graduate and Engineering Research (COPPE), Federal University of Rio de Janeiro (UFRJ), Rio de Janeiro, Brasil

---

## 2. Fontes de Dados

### Dados Epidemiológicos
| Fonte | Descrição | Período |
|-------|-----------|---------|
| SINAN | Sistema de Informações de Agravos de Notificação - Hanseníase | 2001-2024 |
| DATASUS | Transferência de arquivos .dbc | Todos os anos, UF BR |

### Dados Demográficos
| Fonte | Descrição |
|-------|-----------|
| IBGE | Estimativas populacionais municipais |
| IBGE | Dados de ligações intermunicipais (2016) |

### Dados de Mobilidade
| Fonte | Descrição | Período |
|-------|-----------|---------|
| ANAC | Agência Nacional de Aviação Civil - Transporte aéreo | 2017-2022 |
| ANTT | Agência Nacional de Transportes Terrestres - Transporte rodoviário | 2022 |
| IBGE | Redes rodoviária e fluvial | 2016 |

### Dados de Validação
| Fonte | Descrição |
|-------|-----------|
| Brasil.IO | Dados de dispersão COVID-19 (validação da rede de mobilidade) |
| GISAID | Dados genômicos SARS-CoV-2 |

---

## 3. Metodologia Detalhada

### 3.1 Pré-processamento de Dados

#### Harmonização de Códigos IBGE
- Conversão do padrão de 7 dígitos (mobilidade/demografia) para 6 dígitos (saúde/SINAN)
- Método: Remoção do dígito verificador via divisão inteira

#### Tratamento de Variáveis
- `AVAL_ATU_N` (Grau de Incapacidade) categorizada em:
  - 0: Grau zero
  - 1: Grau I
  - 2: Grau II
  - 3: Não avaliado
  - 9: Ignorado
- `CLASSOPERA` (Classificação Operacional) categorizada em:
  - 1: Paucibacilar (PB)
  - 2: Multibacilar (MB)
  - 0: Não se aplica/Ignorado
- `NU_IDADE_N` extraída em anos (`IDADE_ANOS`) e meses (`IDADE_MESES`)

### 3.2 Construção da Rede de Mobilidade

#### Representação como Grafo
- Grafo direcionado e ponderado $G=(V, E)$
- $V$ = nós (municípios - código IBGE 6 dígitos)
- $E$ = arestas (fluxo total de passageiros)

#### Métricas de Centralidade
- **Centralidade de Grau Ponderado**: volume total de conexões
- **Centralidade de Intermediação**: importância estrutural na rede

#### Score Sentinela
Combinação das métricas de centralidade para identificar perfis estratégicos:
- **Hubs Nacionais**: alto volume de mobilidade (ex: São Paulo, Guarulhos)
- **Pontes Críticas**: importância estrutural para disseminação inter-regional (ex: Arealva, Jundiaí)
- **Nós de Infraestrutura**: suporte à rede de vigilância

### 3.3 Clusterização

#### Algoritmos Utilizados
- **UMAP** (Uniform Manifold Approximation and Projection): redução de dimensionalidade
- **K-Means**: agrupamento não-supervisionado

#### Hiperparâmetros Otimizados
- `n_neighbors` (UMAP): 30
- `n_clusters` (K-Means): 2

#### Métricas de Validação
| Parâmetro | Valor |
|-----------|-------|
| Silhouette Score | 0.689642 |
| Davies-Bouldin Index | 0.446947 |

#### Justificativa de K=2
- Silhueta indica coesão e separabilidade adequadas
- K=2 proporciona fenótipos clinicamente acionáveis:
  - "Diagnóstico Oportuno"
  - "Diagnóstico Tardio/Vulnerabilidade"
- K>2 gera fragmentação excessiva sem benefício prático para saúde pública

### 3.4 Modelagem Preditiva

#### Modelos Utilizados

##### LightGBM + SMOTE
- **Framework**: Gradient Boosting com crescimento leaf-wise
- **Tratamento de desbalanceamento**: SMOTE (Synthetic Minority Over-sampling)
- **Hiperparâmetros**:
  - `n_estimators`: 100
  - `learning_rate`: 0.05
  - `num_leaves`: 64
- **Nota**: Target utilizado foi `TPALTA_N` (Tipo de Alta) - **possível data leakage** - ver limitações

##### Random Forest Regressor
- Uso como baseline para comparação
- Interpretabilidade via importância de features

##### GRU (Gated Recurrent Unit)
- Arquitetura de Rede Neural Recorrente
- Input shape: (look_back=12, 1)
- Layers: GRU(50) -> Dropout(0.2) -> GRU(50) -> Dropout(0.2) -> Dense(1)
- Otimizador: Adam
- Loss: MSE
- **Nota**: Script possui bug (falta import config) - ver limitações

### 3.5 Modelagem de Séries Temporais

#### Modelos Implementados
1. **Naive Seasonal**: baseline simples (repete ano anterior)
2. **SARIMA (5,1,0)x(1,1,1,12)**: sazonalidade anual
3. **Holt-Winters**: suavização exponencial com tendência e sazonalidade
4. **Prophet**: tendência piecewise com detecção automática de changepoints
5. **XGBoost**: com features de lags (1 e 12 meses)

#### Marcos Temporais Utilizados
| Marco | Data | Referência |
|-------|------|------------|
| Início Pandemia OMS | 2020-03-11 | Declaração OMS |
| Fim ESPIN Brasil | 2022-04-22 | Portaria 913 |
| Fim Emergência OMS | 2023-05-05 | Declaração OMS |

#### Resultados Comparativos
| Modelo | Gap Pandemia | Gap Recuperação | Gap Total | MAE |
|--------|-------------|-----------------|------------|-----|
| Naive Seasonal | 25.335 | 24.155 | 49.490 | 829.23 |
| SARIMA | 25.315 | 18.099 | 43.415 | 724.33 |
| Holt-Winters | 27.487 | 27.870 | 55.358 | 922.64 |
| Prophet | 29.156 | 32.726 | 61.883 | 1.031.39 |
| XGBoost | 24.144 | 19.495 | 43.640 | 728.48 |

#### Estimativa de Subnotificação
- **SARIMA**: ~43.415 casos (-33,56%)
- **Prophet**: ~61.883 casos (-47,84%)
- **Intervalo de incerteza**: [43k, 61k] casos

### 3.6 Explicabilidade (SHAP)

#### Métodos Aplicados
- **TreeExplainer**: para LightGBM
- **SHAP Values**: decomposição de previsões individuais
- **Visualizações**: Bar Plot, Waterfall Plot, Beeswarm Plot

#### Importância Global (Top 10)
| Atributo | Impacto Médio SHAP |
|----------|-------------------|
| TPALTA_N_7 | 0.2119 |
| TPALTA_N_4 | 0.1237 |
| TPALTA_N_3 | 0.1143 |
| DOSE_RECEB | 0.1115 |
| TPALTA_N_6 | 0.0616 |
| TPALTA_N_2 | 0.0477 |
| TPALTA_N_8 | 0.0452 |
| NU_ANO | 0.0339 |
| BACILOSCOP | 0.0157 |
| CONTEXAM | 0.0111 |

### 3.7 Validação Estatística

#### Testes Aplicados
- **Mutual Information (MI)**: ranqueamento de variáveis preditoras
- **Kruskal-Wallis**: comparação entre clusters (p < 0,001)
- **Mann-Whitney U**: validação de variáveis individuais
- **ITS (Interrupted Time Series)**: detecção de quebras estruturais

---

## 4. Resultados Principais

### 4.1 Análise de Clustering

#### Métricas de Otimização
| n_neighbors | n_clusters | Silhouette | Davies-Bouldin |
|------------|-----------|------------|----------------|
| 30 | 2 | 0.689642 | 0.446947 |
| 15 | 4 | 0.631881 | 0.532029 |
| 15 | 2 | 0.624289 | 0.592053 |

#### Projeções Comparativas
| Método | Trustworthiness | Tempo de Execução |
|--------|-----------------|-------------------|
| UMAP | Melhor equilíbrio | Moderado |
| PCA | Baixo | Rápido |
| t-SNE | Fragmentado | Lento |

### 4.2 Modelagem Preditiva

#### LightGBM + SMOTE
- **Nota**: Resultados apresentam métricas = 1.0 (suspeito de data leakage)
- Precisa revisão do target (atualmente TPALTA_N)

#### Random Forest Regressor
- R² reportado: 0.8654
- MAE: 2.69 casos

#### GRU
- R² reportado: 0.9020
- **Nota**: Script com bug (falta import config)

### 4.3 Análise de Subnotificação

#### Estágio I: Pandemia Oculta (2020-2022)
- Gap negativo: -33,56% de detecção
- Causa: colapso da busca ativa, conversão de unidades para COVID-19

#### Estágio II: Reabsorção de Backlog (2023-2024)
- Gap positivo: notificações superiores à projeção contrafactual
- Causa: diagnóstico do passivo acumulado

---

## 5. Estrutura de Arquivos

### Artigo Principal
```
overleaf/
├── main.tex          # Versão completa (dissertação)
├── artigo.tex        # Versão artigo curto
├── bibliografia.bib # Referências completas
├── references.bib   # Referências alternativas
├── main_dis.tex     # Versão dissertação
├── main_dis.pdf     # PDF compilado
└── compilado/        # Arquivos de compilação
```

### Capítulos
```
overleaf/Chapters/
├── Chapter1.tex      # Introdução
├── Chapter2.tex      # Revisão de Literatura
├── Chapter3.tex      # Metodologia
├── Chapter4.tex      # Resultados: Caracterização e Clustering
├── Chapter5.tex      # Resultados: Modelagem Preditiva e Séries Temporais
└── Chapter6.tex      # Conclusões
```

### Tabelas LaTeX
```
overleaf/tabs/
├── tabela_comparativo_modelos_full.tex
├── tabela_importancia_shap.tex
├── resultados_modelagem.tex
├── otimizacao_clustering.tex
├── tabela_regional_normalizada.tex
├── tabela_projecoes.tex
├── perfil_clusters_incapacidade.tex
├── paradoxo_its.tex
└── paradoxo_falsa_cura.tex
```

### Figuras
```
overleaf/fig/
├── design_estudo_timeline.png
├── comparativo_focado_ts.png
├── shap_bar.png
├── shap_waterfall.png
├── shap_beeswarm.png
├── analise_regional_normalizada.png
├── analise_silhueta_k2_k3.png
├── comparativo_projecoes.png
└── justificativa_alta_gravidade.png
```

### Scripts de Geração
```
scripts_artigo/
├── tratamento_variaveis.py    # ⚠️ POSSUI DATA LEAKAGE
├── analise_completa_series.py
├── modelagem_gru.py          # ⚠️ POSSUI BUG (falta import config)
├── modelagem_avancada.py
├── analise_incapacidade.py
├── perfil_cluster_gravidade.py
├── gerar_shap_beeswarm.py
├── comparativo_projecoes.py
├── analise_paradoxo_pandemia.py
├── eda.py
└── relatorios/               # Relatórios intermediários
    ├── metricas_series_temporais.tex
    └── otimizacao_clustering.tex
```

### Dados Processados
```
tratamento/
├── dados_tratados.csv   # Features codificadas
└── alvo_tratado.csv     # Target

results/
├── rede_mobilidade_completa.gpickle
├── centralidade_anual.csv
├── dataset_ml_hanseniase.csv
└── feature_importance.png
```

---

## 6. Status do Projeto

### ✅ Concluído
- Coleta e pré-processamento de dados
- Análise exploratória
- Clusterização (UMAP + K-Means)
- Modelagem de séries temporais
- Validação ITS
- Explicabilidade SHAP
- Compilação do artigo LaTeX

### ⚠️ Pendente
- Revisão do target no modelo LightGBM (data leakage)
- Correção do bug no modelagem_gru.py
- Validação final dos R² reportados (0.8654 e 0.9020)
- Verificação de consistência dos resultados

---

## 7. Limitações e Bugs Conhecidos

### CRÍTICO: Data Leakage no Tratamento de Variáveis

**Local**: `scripts_artigo/tratamento_variaveis.py:21-25`

**Problema**:
```python
variaveis_preditoras = [
    'CLASSOPERA', 'BACILOSCOP', 'ESQ_INI_N', 'CONTREG', 'NERVOSAFET', 'ESQ_ATU_N',
    'DOSE_RECEB', 'CONTEXAM', 'TPALTA_N', 'CS_SEXO', 'CS_RACA', 'CS_ESCOL_N',
    'NU_ANO'
]
variaveis_alvo = ['TPALTA_N']  # ❌ TPALTA_N está nas features E no target!
```

A variável `TPALTA_N` (Tipo de Alta) é usada simultaneamente como feature e como target, causando correlação perfeita e métricas infladas (precision/recall = 1.0).

**Correção sugerida**: Usar `AVAL_ATU_N` (Grau de Incapacidade) como target.

---

### CRÍTICO: Bug no Script GRU

**Local**: `scripts_artigo/modelagem_gru.py`

**Problema**:
```python
# Linha 16: usa config mas não importa
df = pd.read_csv(str(config.PATHS['hanceniase']), low_memory=False)
```

Falta `import config` no início do arquivo.

**Correção sugerida**: Adicionar `import config` no topo do arquivo.

---

###其他 Questões

1. **Inconsistência nos resultados**: O artigo reporta R²=0.8654 (Random Forest) e R²=0.9020 (GRU), mas não localizamos a geração desses valores nos scripts verificados.

2. **Validação de modelos**: Os modelos de séries temporais estão validados, mas falta validação cruzada rigorosa para os modelos de classificação.

---

## 8. Referências Bibliográficas Principais

### Artigos do Grupo de Pesquisa
- Oliveira et al. (2024) - Mobilidade humana e dispersão de patógenos
- Inovação em Saúde (2024) - Modelagem computacional hanseníase
- Dados de mobilidade ANAC/ANTT (2017-2022)

### Bases de Dados
- SINAN Hanseníase
- IBGE População e Mobilidade
- GISAID (genomas SARS-CoV-2)

### Estado da Arte
- UMAP para redução de dimensionalidade em saúde
- SHAP para explicabilidade em modelos de risco
- ITS para análise de impacto de pandemias

---

## 9. Notas Técnicas

### Ambiente de Desenvolvimento
- Python 3.x
- Virtualenv
- Dependências em `requirements.txt`

### Bibliotecas Principais
- pandas, numpy
- scikit-learn, lightgbm, xgboost
- tensorflow/keras
- shap
- statsmodels
- prophet
- umap-learn
- matplotlib, seaborn

### Execução do Pipeline
```bash
python gerar_dados_overleaf.py
```

---

*Documento gerado automaticamente para fins de documentação interna.*
*Última atualização: 2026-05-05*