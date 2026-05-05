# Scripts de Análise e Modelagem (Hanseníase)

Este diretório contém o motor analítico da dissertação, dividido em módulos de processamento de dados, modelagem preditiva e geração de visualizações para o documento final.

## 🚀 Estrutura do Ecossistema

### 1. Modelagem Preditiva e Séries Temporais
- `analise_completa_series.py`: Executa o ensemble multimodelo (SARIMA, Prophet, XGBoost) para quantificar o gap de subnotificação pandêmica.
- `modelagem_avancada.py`: Implementa o classificador LightGBM + SMOTE para predição de G2D, gerando métricas e gráficos SHAP (Waterfall e Bar).
- `gerar_comparativo_validacao.py`: Ilustra o contraste metodológico entre K-Fold (inadequado) e Walk-forward (correto) para séries temporais.

### 2. Caracterização e Clustering
- `analise_incapacidade.py`: Script principal de clusterização UMAP + K-Means, gerando perfis de vulnerabilidade e justificativas estatísticas.
- `gerar_analise_silhueta.py`: Validação técnica da escolha de $K=2$ clusters via perfis de silhueta.
- `comparativo_projecoes.py`: Comparação visual entre PCA, t-SNE e UMAP para justificar a escolha algorítmica.
- `gerar_matriz_transicao.py`: Heatmap de evolução do Grau de Incapacidade Física entre diagnóstico e alta.

### 3. Utilidades de Documentação
- `perfil_cluster_gravidade.py`: Gera tabelas estruturadas em LaTeX sobre os perfis clínicos dos grupos identificados.
- `gerar_esquema_sliding_window.py`: Cria ilustrações pedagógicas sobre o funcionamento da validação temporal.

---

## 🛠️ Como Executar (Makefile Externo)

Na raiz do projeto, utilize o `Makefile` para automatizar o fluxo de trabalho:

- `make pdf`: Sincroniza todos os artefatos gerados pelos scripts e compila a dissertação (`main_dis.tex`).
- `make pres`: Sincroniza os artefatos e compila os slides de defesa (`apresentacao.tex`).
- `make sync`: Comando interno que organiza figuras em `overleaf/fig/` e tabelas em `overleaf/tabs/`, tratando caracteres especiais no LaTeX.
- `make clean`: Limpa arquivos auxiliares de compilação.

## 📂 Organização de Saídas
- `overleaf/fig/`: Gráficos consolidados para inserção no corpo do texto.
- `overleaf/tabs/`: Tabelas em formato `.tex` geradas dinamicamente.
- `data/HANS/`: Base de dados SINAN utilizada nos experimentos.

---
**Nota:** Todos os scripts salvam logs de execução em `./logs/` para auditoria dos resultados.
