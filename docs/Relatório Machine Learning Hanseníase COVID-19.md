# **Dinâmicas Epidemiológicas da Hanseníase e Doenças Tropicais Negligenciadas no Brasil: Uma Análise Abrangente da Incapacidade Física, Subnotificação Pandêmica e Aplicação de Machine Learning Avançado em Saúde**

## **Introdução**

A hanseníase, uma doença infecciosa crônica causada pelo *Mycobacterium leprae*, permanece como um dos desafios mais persistentes e complexos para a saúde pública no Brasil, país que ocupa a segunda posição mundial em número absoluto de casos, atrás apenas da Índia. Caracterizada por um longo período de incubação e pela predileção do bacilo por células de Schwann e pele, a doença possui um potencial incapacitante singular, capaz de gerar deformidades físicas irreversíveis se não diagnosticada e tratada precocemente. O cenário epidemiológico brasileiro, historicamente marcado por heterogeneidades regionais e determinantes sociais profundos, sofreu um choque exógeno sem precedentes com a emergência da pandemia de COVID-19 em 2020\. A crise sanitária global não apenas interrompeu as cadeias de transmissão e vigilância, mas também obscureceu a verdadeira magnitude da endemia através de barreiras operacionais massivas.

Este relatório técnico-científico tem como objetivo fornecer uma análise exaustiva e multidimensional do estado atual da hanseníase no Brasil, com foco em três pilares interconectados: (1) a epidemiologia do Grau de Incapacidade Física (GIF/G2D) como marcador sentinela de falhas no diagnóstico e na gestão clínica; (2) a análise comparativa da subnotificação durante a pandemia de COVID-19, contrastando a hanseníase com a tuberculose e outras doenças negligenciadas para isolar os efeitos específicos da interrupção de exames físicos; e (3) a avaliação crítica de técnicas de Inteligência Artificial e Machine Learning (ML)—especificamente Random Forest, XGBoost com técnicas de balanceamento (SMOTE), LightGBM e Gated Recurrent Units (GRU)—como ferramentas emergentes para a previsão de risco, retificação de dados e vigilância de precisão.

A análise baseia-se em uma revisão sistemática de literatura revisada por pares, boletins epidemiológicos oficiais do Ministério da Saúde (2024-2025) e estudos ecológicos de séries temporais interrompidas. Busca-se não apenas descrever os fenômenos, mas elucidar as relações causais subjacentes e propor um roteiro analítico para a recuperação das metas da estratégia "Zero Hanseníase" no cenário pós-pandêmico.

## ---

**Parte I: A Carga da Incapacidade Física na Hanseníase: Indicadores de Diagnóstico Tardio e Desafios Operacionais**

### **1.1 O Significado Epidemiológico e Clínico do Grau de Incapacidade Física (GIF)**

A avaliação do Grau de Incapacidade Física (GIF) constitui a pedra angular do monitoramento da gravidade da hanseníase. Diferentemente de outras doenças infecciosas onde a carga é medida primariamente pela mortalidade, na hanseníase, a morbidade e o estigma associados às deformidades físicas representam o principal peso social e econômico. O sistema de graduação recomendado pela Organização Mundial da Saúde (OMS) e adotado pelo Ministério da Saúde do Brasil classifica os pacientes em três níveis:

* **Grau 0:** Ausência de comprometimento neural nos olhos, mãos e pés.  
* **Grau 1:** Diminuição ou perda da sensibilidade (anestesia) nos olhos, mãos e/ou pés, sem deformidades visíveis. Este estágio representa o dano neural estabelecido, porém muitas vezes reversível ou manejável sem estigma visual imediato.  
* **Grau 2 (G2D):** Presença de deformidades visíveis (como lagoftalmo, garras, reabsorção óssea, mãos e pés caídos) ou danos graves (úlceras, cegueira).

A detecção de um caso novo já apresentando Grau 2 de Incapacidade (G2D) é universalmente reconhecida como um indicador de **falha operacional** e **atraso diagnóstico**. Significa que o paciente conviveu com a doença ativa e transmissível por um período prolongado—estimado em anos—permitindo que a resposta inflamatória ou a ação direta do bacilo causassem danos irreversíveis aos nervos periféricos antes de qualquer intervenção terapêutica.1 Portanto, a taxa de G2D não mede apenas a gravidade clínica, mas a eficiência da vigilância epidemiológica e a acessibilidade da Atenção Primária à Saúde (APS).

### **1.2 Tendências Temporais do Grau 2 de Incapacidade no Brasil (2014–2024)**

A análise da série histórica recente revela um cenário preocupante de manutenção da gravidade, mesmo diante de flutuações nas taxas de detecção geral.

#### **1.2.1 O Paradoxo da Pandemia: Queda na Detecção, Aumento da Proporção de Incapacidade**

Durante os anos críticos da pandemia de COVID-19 (2020-2021), observou-se um fenômeno epidemiológico que pode ser descrito como um "paradoxo de gravidade". Enquanto a taxa geral de detecção de novos casos despencou devido às restrições de mobilidade e redirecionamento de serviços de saúde, a proporção de casos diagnosticados com G2D entre os avaliados manteve-se estável ou aumentou, indicando que apenas os casos mais avançados e sintomáticos conseguiam acessar o sistema de saúde colapsado.

Dados do Boletim Epidemiológico de 2025 indicam que, em 2023, o Brasil diagnosticou 22.773 casos novos de hanseníase. Deste total, **2.173 indivíduos (9,5%)** já apresentavam Grau 2 de Incapacidade física no momento do diagnóstico.3 Esse percentual é classificado como "alto" segundo os parâmetros do Ministério da Saúde, evidenciando que quase um em cada dez pacientes inicia o tratamento já mutilado.

Estudos de série temporal interrompida mostram que a pandemia causou uma redução imediata na detecção, mas a retomada lenta em 2022 e 2023 trouxe à tona uma "demanda reprimida" de casos com maior complexidade clínica.4 Em Minas Gerais, por exemplo, a proporção de casos multibacilares (MB)—forma clínica associada a maior carga bacilar e risco de incapacidade—subiu de 71,8% em 2019 para **81,6% em 2024**.6 Isso sugere que os casos paucibacilares (iniciais) deixaram de ser diagnosticados massivamente, restando ao sistema de saúde a identificação tardia das formas avançadas.

#### **1.2.2 A Persistência da Transmissão Recente: G2D em Menores de 15 Anos**

A presença de G2D em crianças e adolescentes (menores de 15 anos) é um indicador sentinela de gravidade extrema, denotando transmissão ativa e recente na comunidade e, frequentemente, dentro do domicílio, associada à falha no exame de contatos. Em 2023, foram notificados 958 casos novos nesta faixa etária no Brasil.3 A detecção de deformidades físicas neste grupo etário reflete uma dupla falha: a exposição precoce ao bacilo e a incapacidade do sistema de saúde em diagnosticar a criança antes da evolução para a sequela, apesar das múltiplas oportunidades de contato com serviços de saúde (escola, vacinação).7

#### **1.2.3 Heterogeneidade Regional e Aglomerados de Risco**

A distribuição espacial do G2D no Brasil não é homogênea, refletindo as desigualdades socioeconômicas estruturais do país.

* **Regiões Hiperendêmicas (Norte e Centro-Oeste):** Estados como Mato Grosso e Tocantins apresentam as maiores taxas de detecção geral e, consequentemente, números absolutos elevados de G2D. Nestas áreas, a alta endemicidade mantém a doença como uma prioridade visível, mas a cobertura em áreas remotas permanece um desafio logístico.8  
* **O Fenômeno do Sul/Sudeste:** Paradoxalmente, regiões com menor taxa de detecção geral, como o Sul e Sudeste, frequentemente apresentam *proporções* mais elevadas de G2D entre os casos novos. Isso ocorre devido à menor suspeição clínica por parte dos profissionais de saúde na atenção básica, levando a diagnósticos tardios apenas quando as sequelas já são evidentes. Estudos indicam que em áreas de baixa endemicidade, a "endemia oculta" se manifesta através de casos diagnosticados tardiamente com incapacidades severas, como observado em análises espaciais no estado de São Paulo e Paraná.4

### **1.3 A Lacuna na Avaliação de Alta e a "Falsa Cura"**

Um aspecto crítico, frequentemente negligenciado, é a evolução da incapacidade *após* o início do tratamento e no momento da alta (cura bacteriológica). A poliquimioterapia (PQT) mata o bacilo, mas não reverte o dano neural estabelecido e não cessa imediatamente os processos imunológicos (reações hansênicas) que podem continuar a danificar os nervos.

#### **1.3.1 Avaliação de Incapacidade na Cura: Um Indicador Precário**

O indicador "Proporção de casos novos com Grau de Incapacidade Física avaliado na cura" mensura a qualidade longitudinal da assistência. Dados recentes mostram uma deterioração alarmante deste indicador. Em 2023, apenas **70,4%** dos casos novos curados tiveram seu grau de incapacidade avaliado no momento da alta.10 Este desempenho é classificado como **"precário"** (\<75%), indicando que o sistema de saúde está "perdendo" o paciente no momento crucial de definir suas necessidades de reabilitação.

O número de municípios brasileiros com desempenho classificado como "precário" para este indicador aumentou de 1.115 em 2014 para **1.190 em 2023**.8 Isso implica que milhares de brasileiros estão recebendo alta administrativa sem uma avaliação formal de suas condições físicas, o que impede o acesso a programas de prevenção de incapacidades e reabilitação física.

#### **1.3.2 Progressão da Incapacidade Pós-Alta**

A "cura" da hanseníase não é sinônimo de fim do risco de incapacidade. Estudos de sobrevivência mostram que a probabilidade de progressão do grau de incapacidade (piora da função neural) pode chegar a **35% em até 15 anos após a alta**.11 Fatores como reações hansênicas tardias e neurites silenciosas continuam a operar. A falta de monitoramento pós-alta, evidenciada pelos dados precários de avaliação na cura, cria uma coorte de "curados" que evoluem para deficiências severas, invisíveis às estatísticas epidemiológicas de casos ativos, mas que oneram o sistema de previdência e saúde a longo prazo.

### **1.4 Determinantes do Diagnóstico Tardio**

A literatura aponta fatores de risco consistentes para o desenvolvimento de G2D, que devem ser alvos de intervenção:

* **Fatores Sociodemográficos:** O sexo masculino é consistentemente associado a maior risco de G2D (OR ajustado significativo), atribuído a barreiras culturais de autocuidado e horários de funcionamento das unidades de saúde incompatíveis com a jornada de trabalho.12 A baixa escolaridade e a idade avançada (\>60 anos) também são preditores fortes.13  
* **Fatores Clínicos:** A forma clínica multibacilar (Virchowiana ou Dimorfa) e a presença de múltiplos nervos espessados (\>2) são os maiores preditores biológicos de incapacidade. A ocorrência de reações hansênicas (Tipo 1 ou 2\) durante o curso da doença multiplica o risco de dano neural permanente.14  
* **Modo de Detecção:** Pacientes detectados por "demanda espontânea" (encaminhamento ou procura própria com sintomas avançados) têm chances muito maiores de apresentar G2D do que aqueles detectados por "busca ativa" (exame de contatos, inquéritos). O colapso da busca ativa durante a pandemia exacerbou este fator.5

## ---

**Parte II: A Pandemia Oculta: Análise Comparativa da Subnotificação entre Hanseníase e Tuberculose**

A emergência de saúde pública da COVID-19 impôs uma reorganização drástica nos serviços de saúde. No entanto, o impacto não foi uniforme entre todas as doenças transmissíveis. A comparação entre hanseníase e tuberculose (TB) — duas doenças negligenciadas com dinâmicas de transmissão e diagnóstico distintas — revela como as características operacionais de cada agravo determinaram a magnitude de sua subnotificação.

### **2.1 Hanseníase: O Colapso do Diagnóstico Físico**

A hanseníase depende fundamentalmente do exame dermatoneurológico presencial para diagnóstico. A identificação de manchas hipocrômicas com alteração de sensibilidade e o palpear de nervos periféricos exigem proximidade física entre profissional e paciente, algo que foi estritamente limitado pelas medidas de distanciamento social.

* **Magnitude da Queda:** Estudos de séries temporais interrompidas demonstram que a detecção de hanseníase sofreu uma redução imediata de **0,55 (55%)** na taxa de detecção geral no início da pandemia.3 Em números absolutos, observou-se uma redução de **35% a 45%** nos diagnósticos em 2020 em comparação com a média histórica (2015-2019).15 No estado da Bahia, a redução chegou a 44,4%.15  
* **Descontinuidade da Busca Ativa:** A detecção em menores de 15 anos, que depende fortemente de campanhas escolares e busca ativa domiciliar, sofreu uma queda ainda mais acentuada, próxima de **50%**.3 Escolas fechadas e agentes comunitários de saúde focados na COVID-19 desmantelaram a rede de detecção precoce.  
* **Repercussão:** Diferentemente de doenças agudas, onde a subnotificação pode significar casos leves que se resolveram, na hanseníase, os casos não diagnosticados em 2020/2021 continuaram evoluindo. A "retomada lenta" observada a partir de 2022 não foi suficiente para compensar o déficit, resultando no aumento da proporção de G2D discutido anteriormente.

### **2.2 Tuberculose: Resiliência Relativa e Desafios Laboratoriais**

A tuberculose, embora também afetada, apresentou um padrão de subnotificação menos severo em termos percentuais, mas com implicações letais imediatas devido à sua natureza aguda e respiratória.

* **Magnitude da Queda:** As análises indicam uma redução de **8,3%** no diagnóstico geral de TB e **8,1%** na TB pulmonar no Brasil em 2020\.17 Embora significativa, essa queda é consideravelmente menor que a da hanseníase (\>35%).  
* **Fatores de Proteção Relativa:** A tosse persistente, principal sintoma da TB, é um sinal de alerta que motiva a procura por serviços de emergência, diferentemente das manchas indolores da hanseníase. Além disso, a infraestrutura de diagnóstico da TB (raio-X, coleta de escarro) permaneceu parcialmente ativa como parte do diagnóstico diferencial para COVID-19 sintomático respiratório.  
* **Impacto Laboratorial:** A redução foi mais acentuada nos casos com **baciloscopia positiva (-17,1%)**.17 Isso sugere que, embora os pacientes pudessem ser atendidos e tratados empiricamente por quadro clínico-radiológico, a confirmação laboratorial caiu drasticamente, possivelmente devido à sobrecarga dos laboratórios de saúde pública com testes de RT-PCR para SARS-CoV-2 e à biossegurança envolvida no manuseio de escarro.  
* **Estimativa de Casos Perdidos:** Modelos estatísticos estimam que o Brasil deixou de notificar cerca de **11.647 casos de TB em 2020** e **6.170 em 2021**.18 Ao contrário da hanseníase, onde a consequência primária é a incapacidade, na TB, essa subnotificação traduz-se diretamente em aumento da mortalidade e transmissão aérea sustentada.

### **2.3 Comparativo com Outras Doenças Negligenciadas (DTNs)**

A subnotificação foi um fenômeno sistêmico, mas heterogêneo:

* **Leishmaniose Visceral (LV):** Apresentou uma queda de **46,7%** nos diagnósticos em 2020\.19 Assim como a hanseníase, a LV depende de suspeição clínica específica e inquéritos sorológicos caninos/humanos que foram interrompidos.  
* **Dengue:** A dengue apresentou um padrão misto. Em 19 dos 25 estados analisados, houve subnotificação massiva explicada pela redução na busca por cuidados. No entanto, a região Sul experimentou surtos reais que superaram as barreiras de notificação.20 Isso demonstra que epidemias explosivas (como a de dengue) forçam a notificação, enquanto endemias silenciosas (hanseníase) são facilmente invisibilizadas em crises.

| Doença | Redução na Detecção (2020 vs Histórico) | Mecanismo Principal de Queda | Consequência Imediata |
| :---- | :---- | :---- | :---- |
| **Hanseníase** | **\~35% \- 55%** | Suspensão de exames físicos e busca ativa; medo de contágio em consultas não urgentes. | Aumento oculto de incapacidades (G2D) e transmissão intradomiciliar. |
| **Tuberculose** | **\~8% \- 17%** | Competição de infraestrutura laboratorial; menor acesso, mas sintomas respiratórios mantiveram alguma procura. | Aumento da mortalidade não tratada e transmissão comunitária. |
| **Leishmaniose Visceral** | **\~46%** | Interrupção de inquéritos de campo e controle de vetores. | Aumento da letalidade por diagnóstico tardio. |

*Tabela 1: Comparativo do impacto da pandemia na notificação de doenças selecionadas.*

## ---

**Parte III: Machine Learning e Inteligência Artificial na Saúde: Previsão de Incapacidade e Análise de Dados**

Diante da complexidade dos dados epidemiológicos e da necessidade de recuperar o tempo perdido na vigilância, técnicas de Machine Learning (ML) têm se mostrado ferramentas indispensáveis. A literatura recente (2020-2025) destaca o uso de algoritmos de aprendizado supervisionado e profundo para prever diagnósticos tardios, classificar riscos e realizar previsões temporais (forecasting).

### **3.1 O Desafio dos Dados Desbalanceados: O Papel do SMOTE**

Em bases de dados de saúde como o SINAN, eventos críticos como o G2D ou formas clínicas específicas são frequentemente a "classe minoritária" (ex: 10% dos casos são G2D, 90% não são). Algoritmos tradicionais tendem a enviesar a predição para a classe majoritária, ignorando os casos graves que mais precisamos identificar.

A técnica **SMOTE (Synthetic Minority Over-sampling Technique)** tem sido fundamental para resolver isso. Em vez de simplesmente duplicar registros existentes da classe minoritária (o que causaria *overfitting*), o SMOTE cria dados sintéticos interpolando as características de casos minoritários vizinhos no espaço vetorial.

* **Aplicação Prática:** No estudo de *Freitas et al. (2025)* sobre previsão de G2D no Brasil, o SMOTE foi aplicado sempre que a classe minoritária representava menos de 25% dos dados.5  
* **Resultados:** O uso de SMOTE em conjunto com classificadores como XGBoost elevou significativamente a sensibilidade (recall) dos modelos, garantindo que o sistema não "deixasse passar" os pacientes com alto risco de incapacidade, mesmo que fossem estatisticamente raros.21

### **3.2 Algoritmos Baseados em Árvores de Decisão (Ensemble Methods)**

Três algoritmos dominam a literatura recente sobre previsão de risco em hanseníase e outras DTNs: Random Forest, XGBoost e LightGBM.

#### **3.2.1 Random Forest (RF)**

O Random Forest cria múltiplas árvores de decisão independentes e agrega seus resultados (bagging). É robusto e lida bem com dados categóricos sem necessidade de normalização excessiva.

* **Na Hanseníase:** Foi utilizado com sucesso para classificar casos em paucibacilares ou multibacilares com base em dados moleculares e sorológicos, alcançando alta especificidade.23 Também serviu como modelo base em aplicativos de triagem clínica baseados nos dados do SINAN.24  
* **Limitações:** Embora robusto, pode ser computacionalmente mais pesado e menos preciso em dados muito desbalanceados se não ajustado corretamente.

#### **3.2.2 XGBoost (Extreme Gradient Boosting)**

O XGBoost utiliza a técnica de *boosting*, onde novas árvores são criadas para corrigir os erros das anteriores. É altamente otimizado para velocidade e desempenho.

* **Predição de Diagnóstico:** Em estudos utilizando o "Questionário de Suspeição de Hanseníase" (LSQ), o XGBoost foi um dos algoritmos com melhor desempenho para diferenciar casos reais de falso-positivos, especialmente quando combinado com SMOTE para ajustar o desbalanceamento.25  
* **Relevância Regional:** O modelo mostrou excelente acurácia (AUC-ROC de 0,93) na região Sul do Brasil para prever G2D, superando modelos mais simples.5 Ele lida nativamente com valores ausentes (comuns no SINAN), o que é uma vantagem crucial em dados de saúde pública.

#### **3.2.3 LightGBM (Light Gradient Boosting Machine)**

O LightGBM diferencia-se por crescer as árvores de forma "leaf-wise" (por folha) em vez de "level-wise" (por nível), e por usar histogramas para agrupar valores contínuos, o que o torna extremamente rápido e eficiente em memória.

* **O Campeão de Eficiência:** No estudo comparativo de 2025 sobre G2D no Brasil, o **LightGBM** (junto com o modelo Ensemble) demonstrou o **melhor desempenho preditivo**, especialmente nas regiões Norte e Nordeste (Acurácia: 0,85; AUC: 0,93).5  
* **Seleção de Atributos:** Estudos combinam LightGBM com algoritmos de seleção de características como **Boruta** ou **RFE (Recursive Feature Elimination)**. Essa combinação permite identificar quais variáveis (ex: número de nervos afetados, escolaridade, forma clínica) são os verdadeiros preditores de incapacidade, eliminando o ruído epidemiológico.26 Devido à sua eficiência computacional, o LightGBM foi eleito o modelo preferencial para implementação em sistemas de saúde com recursos limitados.5

### **3.3 Redes Neurais para Séries Temporais: Gated Recurrent Units (GRU)**

Enquanto os modelos de árvore (XGBoost, LightGBM) são excelentes para classificação de risco individual (diagnóstico), as Redes Neurais Recorrentes (RNN) são necessárias para **previsão temporal (forecasting)** da incidência da doença.

#### **3.3.1 Arquitetura GRU**

A GRU é uma evolução das RNNs tradicionais, similar à LSTM (Long Short-Term Memory), mas com uma arquitetura simplificada (duas portas: *reset* e *update*). Ela resolve o problema do "desvanecimento do gradiente", permitindo que o modelo aprenda dependências de longo prazo em sequências temporais (ex: como a notificação de casos de 2 anos atrás influencia a atual).

#### **3.3.2 Aplicação em Doenças Infecciosas**

* **Vantagens:** A GRU é computacionalmente mais leve que a LSTM e frequentemente apresenta desempenho similar ou superior em datasets menores ou com ruído, típicos de notificações mensais de doenças.27  
* **Uso na Pandemia:** Modelos GRU foram amplamente utilizados para prever ondas de COVID-19 e mortes, capturando a não-linearidade das curvas epidêmicas melhor que modelos estatísticos clássicos (ARIMA).27  
* **Potencial na Hanseníase:** A metodologia **GRGNN** (Graph Neural Network integrada com GRU) tem sido proposta para capturar não apenas a dependência temporal, mas também a espacial (vizinhos geográficos) na previsão de epidemias, superando modelos isolados.29 Para a hanseníase, o uso de GRU permitiria modelar o "gap" de detecção criado pela pandemia, prevendo quantos casos deveriam ter sido notificados (counterfactual) versus o observado, quantificando com precisão a carga oculta que o sistema de saúde deve buscar ativamente.

## ---

**Conclusão e Recomendações**

A análise integrada dos dados epidemiológicos e das ferramentas tecnológicas aponta para um momento crítico na saúde pública brasileira. A pandemia de COVID-19 exacerbou a negligência histórica com a hanseníase, resultando em um acúmulo silencioso de casos que agora emergem com graus avançados de incapacidade física. A persistência de G2D, especialmente em crianças, e a precariedade na avaliação de alta são sintomas de um sistema que atua de forma reativa, e não preventiva.

No entanto, a ciência de dados oferece um caminho robusto para a recuperação. A aplicação de modelos de Machine Learning — especificamente o uso de **SMOTE para equilibrar a detecção de casos raros/graves**, **LightGBM para estratificação de risco eficiente** em regiões endêmicas, e **GRU para modelagem temporal de demanda oculta** — não é apenas uma possibilidade acadêmica, mas uma necessidade operacional.

**Recomendações Estratégicas:**

1. **Vigilância Preditiva:** Implementar modelos LightGBM/Ensemble nos sistemas municipais (e-SUS) para "flagrar" automaticamente pacientes com alto risco de G2D (baseado em nervos afetados e perfil sociodemográfico) para acompanhamento prioritário.  
2. **Busca Ativa Guiada por Dados:** Utilizar modelos de série temporal (GRU) e espaciais para identificar microáreas onde a queda de detecção em 2020-2021 foi desproporcional à tendência histórica, direcionando mutirões de busca ativa para esses "pontos cegos".  
3. **Monitoramento Pós-Alta:** Instituir a obrigatoriedade da avaliação de GIF na alta e utilizar algoritmos para identificar pacientes "curados" que mantêm alto risco de neurite, garantindo seguimento continuado para prevenir a evolução de incapacidades pós-tratamento.

O Brasil possui os dados e a tecnologia necessários. A integração dessas ferramentas de inteligência artificial à rotina da vigilância epidemiológica é o passo decisivo para transformar a meta de "Zero Hanseníase" de uma aspiração em uma realidade tangível.

#### **Referências citadas**

1. Ministério da Saúde apresenta resultados do Inquérito Nacional de Incapacidades da Hanseníase \- Portal Gov.br, acessado em dezembro 17, 2025, [https://www.gov.br/saude/pt-br/assuntos/noticias/2025/outubro/ministerio-da-saude-apresenta-resultados-do-inquerito-nacional-de-incapacidades-da-hanseniase](https://www.gov.br/saude/pt-br/assuntos/noticias/2025/outubro/ministerio-da-saude-apresenta-resultados-do-inquerito-nacional-de-incapacidades-da-hanseniase)  
2. Physical disabilities caused by leprosy in 100 million cohort in Brazil \- PMC \- NIH, acessado em dezembro 17, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC7983385/](https://pmc.ncbi.nlm.nih.gov/articles/PMC7983385/)  
3. Sousa 2025- An interrupted time series study of the leprosy case detection in Brazil after the COVID-19 pandemic.pdf  
4. Impact of the COVID-19 Pandemic on the Detection of Leprosy in Micro-Regions with a High Risk of Illness in Minas Gerais, Brazil \- MDPI, acessado em dezembro 17, 2025, [https://www.mdpi.com/2036-7449/16/6/89](https://www.mdpi.com/2036-7449/16/6/89)  
5. Evaluating Machine Learning Models for Predicting Late Leprosy Diagnosis by Physical Disability Grade in Brazil (2018–2022) \- PMC \- NIH, acessado em dezembro 17, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC12115529/](https://pmc.ncbi.nlm.nih.gov/articles/PMC12115529/)  
6. Boletim Epidemiológico Hanseníase em Minas Gerais | 2025 \- SES-MG, acessado em dezembro 17, 2025, [https://www.saude.mg.gov.br/wp-content/uploads/2025/05/boletim-hanseniase-mg-2025.pdf](https://www.saude.mg.gov.br/wp-content/uploads/2025/05/boletim-hanseniase-mg-2025.pdf)  
7. Estratégia Nacional para Enfrentamento à Hanseníase \- Prefeitura de Porto Alegre, acessado em dezembro 17, 2025, [https://prefeitura.poa.br/sites/default/files/usu\_doc/hotsites/sms/vigilancia-em-saude/plano\_estrategia%20hanseniase\_23jan24\_isbn%20(26).pdf](https://prefeitura.poa.br/sites/default/files/usu_doc/hotsites/sms/vigilancia-em-saude/plano_estrategia%20hanseniase_23jan24_isbn%20\(26\).pdf)  
8. boletim-epidemiologico-de-hanseniase-numero-especial-jan-2025.pdf, acessado em dezembro 17, 2025, [https://aal.org.br/wp-content/uploads/2025/01/boletim-epidemiologico-de-hanseniase-numero-especial-jan-2025.pdf](https://aal.org.br/wp-content/uploads/2025/01/boletim-epidemiologico-de-hanseniase-numero-especial-jan-2025.pdf)  
9. Barriga Verde \- Dive/SC, acessado em dezembro 17, 2025, [https://dive.sc.gov.br/index.php/component/phocadownload/category/63-hanseniase?download=1901:situacao-epidemiologica-da-hanseniase-2024](https://dive.sc.gov.br/index.php/component/phocadownload/category/63-hanseniase?download=1901:situacao-epidemiologica-da-hanseniase-2024)  
10. Boletim Epidemiológico de Hanseníase 2025 \- Portal Gov.br, acessado em dezembro 17, 2025, [https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes/boletins/epidemiologicos/especiais/2025/boletim-epidemiologico-de-hanseniase-numero-especial-jan-2025.pdf](https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes/boletins/epidemiologicos/especiais/2025/boletim-epidemiologico-de-hanseniase-numero-especial-jan-2025.pdf)  
11. (PDF) Disability progression among leprosy patients released from treatment: a survival analysis \- ResearchGate, acessado em dezembro 17, 2025, [https://www.researchgate.net/publication/341610366\_Disability\_progression\_among\_leprosy\_patients\_released\_from\_treatment\_a\_survival\_analysis](https://www.researchgate.net/publication/341610366_Disability_progression_among_leprosy_patients_released_from_treatment_a_survival_analysis)  
12. (PDF) Clinical variables associated with disability in leprosy cases in northeast Brazil, acessado em dezembro 17, 2025, [https://www.researchgate.net/publication/276865749\_Clinical\_variables\_associated\_with\_disability\_in\_leprosy\_cases\_in\_northeast\_Brazil](https://www.researchgate.net/publication/276865749_Clinical_variables_associated_with_disability_in_leprosy_cases_in_northeast_Brazil)  
13. Time trend and identification of risk areas for physical disability due to leprosy in Brazil: An ecological study, 2001-2022 \- NIH, acessado em dezembro 17, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC11883925/](https://pmc.ncbi.nlm.nih.gov/articles/PMC11883925/)  
14. Factors associated with delayed diagnosis of leprosy in an endemic area in Northeastern Brazil: a cross-section \- SciELO, acessado em dezembro 17, 2025, [https://www.scielo.br/j/csp/a/DLJnznBZmLhHhnSm5wshygw/?format=pdf\&lang=en](https://www.scielo.br/j/csp/a/DLJnznBZmLhHhnSm5wshygw/?format=pdf&lang=en)  
15. Impact of the COVID‐19 pandemic on the diagnosis of new leprosy cases in Northeastern Brazil, 2020 \- ResearchGate, acessado em dezembro 17, 2025, [https://www.researchgate.net/publication/352669533\_Impact\_of\_the\_COVID-19\_pandemic\_on\_the\_diagnosis\_of\_new\_leprosy\_cases\_in\_Northeastern\_Brazil\_2020](https://www.researchgate.net/publication/352669533_Impact_of_the_COVID-19_pandemic_on_the_diagnosis_of_new_leprosy_cases_in_Northeastern_Brazil_2020)  
16. Impact of the COVID-19 pandemic on the diagnosis of leprosy in Brazil: An ecological and population-based study \- PMC \- PubMed Central, acessado em dezembro 17, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC8759948/](https://pmc.ncbi.nlm.nih.gov/articles/PMC8759948/)  
17. Impact of the COVID-19 Pandemic on the Diagnosis of Tuberculosis in Brazil: Is the WHO End TB Strategy at Risk? \- PMC \- PubMed Central, acessado em dezembro 17, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC9277074/](https://pmc.ncbi.nlm.nih.gov/articles/PMC9277074/)  
18. Impact of the COVID-19 pandemic on tuberculosis notification in Brazil | medRxiv, acessado em dezembro 17, 2025, [https://www.medrxiv.org/content/10.1101/2022.09.05.22279616v1.full-text](https://www.medrxiv.org/content/10.1101/2022.09.05.22279616v1.full-text)  
19. Impact of the COVID-19 Pandemic Surveillance of Visceral Leishmaniasis in Brazil: An Ecological Study \- PubMed Central, acessado em dezembro 17, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC10888456/](https://pmc.ncbi.nlm.nih.gov/articles/PMC10888456/)  
20. (PDF) Impact of the COVID-19 pandemic on dengue in Brazil: Interrupted time series analysis of changes in surveillance and transmission \- ResearchGate, acessado em dezembro 17, 2025, [https://www.researchgate.net/publication/387441476\_Impact\_of\_the\_COVID-19\_pandemic\_on\_dengue\_in\_Brazil\_Interrupted\_time\_series\_analysis\_of\_changes\_in\_surveillance\_and\_transmission](https://www.researchgate.net/publication/387441476_Impact_of_the_COVID-19_pandemic_on_dengue_in_Brazil_Interrupted_time_series_analysis_of_changes_in_surveillance_and_transmission)  
21. Leveraging XGBoost and explainable AI for accurate prediction of ..., acessado em dezembro 17, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC12577272/](https://pmc.ncbi.nlm.nih.gov/articles/PMC12577272/)  
22. Comparative Evaluation of Support Vector Classifier, Random Forest, and XGBoost for Early Breast Cancer Prediction With Feature Importance and Class Balancing | Cureus Journals | Article, acessado em dezembro 17, 2025, [https://www.cureusjournals.com/articles/5794-comparative-evaluation-of-support-vector-classifier-random-forest-and-xgboost-for-early-breast-cancer-prediction-with-feature-importance-and-class-balancing](https://www.cureusjournals.com/articles/5794-comparative-evaluation-of-support-vector-classifier-random-forest-and-xgboost-for-early-breast-cancer-prediction-with-feature-importance-and-class-balancing)  
23. A novel integrated molecular and serological analysis method to predict new cases of leprosy amongst household contacts \- PMC \- PubMed Central, acessado em dezembro 17, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC6586366/](https://pmc.ncbi.nlm.nih.gov/articles/PMC6586366/)  
24. Leprosy Screening Based on Artificial Intelligence: Development of a Cross-Platform App, acessado em dezembro 17, 2025, [https://mhealth.jmir.org/2021/4/e23718](https://mhealth.jmir.org/2021/4/e23718)  
25. (PDF) Development and validation of a machine learning approach for screening new leprosy cases based on the leprosy suspicion questionnaire \- ResearchGate, acessado em dezembro 17, 2025, [https://www.researchgate.net/publication/389359250\_Development\_and\_validation\_of\_a\_machine\_learning\_approach\_for\_screening\_new\_leprosy\_cases\_based\_on\_the\_leprosy\_suspicion\_questionnaire](https://www.researchgate.net/publication/389359250_Development_and_validation_of_a_machine_learning_approach_for_screening_new_leprosy_cases_based_on_the_leprosy_suspicion_questionnaire)  
26. Diabetes Prediction Using Feature Selection Algorithms and Boosting-Based Machine Learning Classifiers \- PMC \- NIH, acessado em dezembro 17, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC12563305/](https://pmc.ncbi.nlm.nih.gov/articles/PMC12563305/)  
27. Forecasting of COVID-19 using deep layer Recurrent Neural Networks (RNNs) with Gated Recurrent Units (GRUs) and Long Short-Term Memory (LSTM) cells, acessado em dezembro 17, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC7955925/](https://pmc.ncbi.nlm.nih.gov/articles/PMC7955925/)  
28. Approach to COVID-19 time series data using deep learning and spectral analysis methods, acessado em dezembro 17, 2025, [https://www.aimspress.com/article/doi/10.3934/bioeng.2022001?viewType=HTML](https://www.aimspress.com/article/doi/10.3934/bioeng.2022001?viewType=HTML)  
29. Integrating gated recurrent unit in graph neural network to improve infectious disease prediction: an attempt \- Frontiers, acessado em dezembro 17, 2025, [https://www.frontiersin.org/journals/public-health/articles/10.3389/fpubh.2024.1397260/full](https://www.frontiersin.org/journals/public-health/articles/10.3389/fpubh.2024.1397260/full)  
30. Integrating gated recurrent unit in graph neural network to improve infectious disease prediction: an attempt \- PMC \- NIH, acessado em dezembro 17, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC11144875/](https://pmc.ncbi.nlm.nih.gov/articles/PMC11144875/)