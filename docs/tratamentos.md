## NU_IDADE_N

Se a quantidade de meses for maior que 12, a função calcula os anos e os meses restantes. Se não houver meses restantes (ou seja, se a divisão for exata), a função retorna apenas os anos com meses igual a 0.

Exemplo de funcionamento:
Para um valor de 14 meses, a função retornará 1 ano e 2 meses.

Para um valor de 24 meses, a função retornará 2 anos e 0 meses.

Sendo criados:

- `IDADE_ANOS`: idade em Anos (tratada de 'NU_IDADE_N') \
- `IDADE_MESES`: Meses para recem nascidos (tratada 'NU_IDADE_N') \

### IDADE_ANOS

Top 10 Frequências
            Frequência Absoluta  Frequência Relativa (%)
IDADE_ANOS                                              
49                        18743                 1.904709
50                        18656                 1.895868
48                        18580                 1.888144
51                        18572                 1.887331
46                        18507                 1.880726
47                        18361                 1.865889
44                        18285                 1.858166
45                        18072                 1.836520
52                        17954                 1.824529
53                        17827                 1.811623
Outliers
224 registros (0.02%)
Valores Distintos
[58, 44, 32, 40, 31, 42, 34, 38, 52, 24, 28, 43, 29, 49, 26, 16, 25, 66, 78, 60, 36, 71, 23, 21, 55, 14, 53, 9, 48, 33, 20, 27, 41, 61, 19, 45, 39, 76, 15, 7, 50, 12, 8, 18, 46, 17, 35, 47, 63, 10, 57, 11, 37, 69, 67, 51, 59, 75, 56, 68, 74, 79, 70, 54, 82, 72, 62, 22, 6, 64, 30, 77, 83, 81, 65, 80, 94, 92, 5, 73, 87, 13, 86, 89, 1, 3, 85, 96, 0, 4, 2, 101, 84, 91, 93, 88, 120, 90, 97, 98, 95, 102, 99, 100, 103, 104, 109, 105, 106, 108, 110, 118, 117, 115]
Contagem de NaN
0 registros (0.00%)

### IDADE_MESES

Top 10 Frequências
             Frequência Absoluta  Frequência Relativa (%)
IDADE_MESES                                              
1                            365                67.343173
2                             40                 7.380074
3                             25                 4.612546
5                             24                 4.428044
6                             22                 4.059041
4                             20                 3.690037
7                             16                 2.952030
10                            11                 2.029520
8                              8                 1.476015
11                             6                 1.107011
Outlierss
46 registros (8.49%)
Valores Distintos
[1, 5, 11, 2, 4, 10, 8, 6, 3, 9, 7]
Contagem de NaN
0 registros (0.00%)


## CS_SEXO

Categorizado assim:

- M:1
- F:2
- I:9

- Os valores não definidos foram substituidos por Ignorado (9)
`CS_SEXO_CAT`: Sexo categorizado (tratada 'CS_SEXO_CAT')

### CS_SEXO_CAT

Top 10 Frequências
             Frequência Absoluta  Frequência Relativa (%)
CS_SEXO_CAT                                              
1                         550808                55.974432
2                         433041                44.006666
9                            186                 0.018902
Outlierss
186 registros (0.02%)
Valores Distintos
[1, 2, 9]
Contagem de NaN
0 registros (0.00%)

## CS_GESTANT

1. 1ºTrimestre 

        2. 2ºTrimestre 

        3. 3ºTrimestre

        4. Idade gestacional Ignorada 

        5. Não 

        6. Não se aplica

        9. Ignorado

- Os valores não definidos foram substituidos por Ignorado (9)

'CS_GESTANT_CAT' : GESTANTE (tratada 'CS_GESTANT')

### CS_GESTANT_CAT

Top 10 Frequências
                Frequência Absoluta  Frequência Relativa (%)
CS_GESTANT_CAT                                              
6                            608826                61.870360
5                            204663                20.798346
9                            166181                16.887712
2                              1382                 0.140442
4                              1184                 0.120321
1                              1006                 0.102232
3                               793                 0.080587
Outlierss
375209 registros (38.13%)
Valores Distintos
[6, 9, 5, 1, 4, 3, 2]
Contagem de NaN
0 registros (0.00%)

## CS_RACA

        1. Branca 

        2. Preta 

        3. Amarela

        4. Parda 

        5. Indígena 

        9. Ignorado

- Os valores não definidos foram substituidos por Ignorado (9)
'CS_RACA_CAT': Código Raça (tratada 'CS_RACA')

### CS_RACA_CAT

Top 10 Frequências
             Frequência Absoluta  Frequência Relativa (%)
CS_RACA_CAT                                              
0                         485235                49.310746
1                         256308                26.046635
2                         118802                12.072945
9                         108217                10.997271
4                          11750                 1.194063
5                           3723                 0.378340
Outlierss
123690 registros (12.57%)
Valores Distintos
[9, 1, 0, 2, 5, 4]
Contagem de NaN
0 registros (0.00%)

### NU_LESOES

- Os valores não definidos foram substituidos por Ignorado (9)

'NU_LESOES_CAT':  Nº de lesões cutâneas (tratada 'NU_LESOES')

#### NU_LESOES_CAT

Top 10 Frequências
               Frequência Absoluta  Frequência Relativa (%)
NU_LESOES_CAT                                              
1                           240196                24.409294
0                           169459                17.220831
2                            95257                 9.680245
5                            73754                 7.495059
10                           71352                 7.250962
3                            59534                 6.049988
6                            57123                 5.804976
20                           42967                 4.366410
4                            36831                 3.742855
8                            27111                 2.755085
Outlierss
80034 registros (8.13%)
Valores Distintos
[0, 3, 1, 25, 2, 5, 4, 15, 30, 6, 7, 20, 12, 10, 11, 8, 16, 9, 13, 17, 14, 19, 18, 58, 40, 23, 37, 99, 34, 33, 22, 36, 27, 28, 24, 50, 39, 42, 70, 32, 21, 29, 35, 65, 90, 45, 31, 80, 52, 60, 74, 57, 38, 96, 88, 43, 41, 44, 48, 55, 86, 26, 56, 73, 63, 71, 78, 46, 79, 59, 54, 51, 72, 76, 47, 62, 75, 68, 84, 95, 49, 98, 87, 82, 53, 92, 69, 93, 64, 81, 61, 97, 67, 85, 89, 83, 91, 94, 77, 66]
Contagem de NaN
0 registros (0.00%)


### FORMACLINI

        1- I -Indeterminada

        2- T - Tuberculóide

        3- D - Dimorfa

        4- V - Virchowiana

        5- Não classificado

- Os valores não definidos e zero foram substituidos por Não classificado (5)        

#### FORMACLINI_CAT

Top 10 Frequências
                Frequência Absoluta  Frequência Relativa (%)
FORMACLINI_CAT                                              
3                            391087                39.743200
2                            174628                17.746117
4                            170896                17.366862
1                            156208                15.874232
5                             90568                 9.203738
9                               535                 0.054368
6                               112                 0.011382
8                                 1                 0.000102
Outlierss
536 registros (0.05%)
Valores Distintos
[1, 4, 2, 3, 5, 9, 8, 6]
Contagem de NaN
0 registros (0.00%)

## AVALIA_N

        0 Grau zero

        1- Grau I

        2- Grau II

        3 - Não avaliado
- Os valores não definidos foram substituidos por Não avaliado (3)  

'AVALIA_N_CAT': Avaliação do Grau de Incapacidade Física no Diagnóstico (tratada 'AVALIA_N') 

#### AVALIA_N_CAT

Top 10 Frequências
              Frequência Absoluta  Frequência Relativa (%)
AVALIA_N_CAT                                              
0                          576474                58.582672
1                          216608                22.012225
3                          116197                11.808218
2                           74756                 7.596884
Outlierss
116197 registros (11.81%)
Valores Distintos
[0, 2, 1, 3]
Contagem de NaN
0 registros (0.00%)

### CLASSOPERA: Classificação operacional, por ocasião do diagnóstico, para eleição do esquema terapêutico

        1- PB - Paucibacilar

        2- MB - Multibacilar

        3- Não classificado (criado)

- Os valores não definidos (3 e 9) foram substituidos por Não classificado (3)
'CLASSOPERA': Classificação operacional, por ocasião do diagnóstico, para eleição do esquema terapêutico (tratada 'CLASSOPERA_CAT')

#### CLASSOPERA_CAT

Top 10 Frequências
                Frequência Absoluta  Frequência Relativa (%)
CLASSOPERA_CAT                                              
2                            643974                65.442184
1                            337254                34.272561
3                              2807                 0.285254
Outlierss
0 registros (0.00%)
Valores Distintos
[2, 1, 3]
Contagem de NaN
0 registros (0.00%)

## BACILOSCOP: Informar o resultado da baciloscopia

        1. Positiva

        2. Negativa

        3. Não realizada

        9. Ignorado

- Os valores não definidos (3 e 9) foram substituidos por Ignorado (9)
'BACILOSCOP_CAT': Informar o resultado da baciloscopia (tratada 'BACILOSCOP')       

#### BACILOSCOP_CAT

Top 10 Frequências
                Frequência Absoluta  Frequência Relativa (%)
BACILOSCOP_CAT                                              
9                            521449                52.990900
3                            167509                17.022667
2                            167493                17.021041
1                            127584                12.965392
Outlierss
0 registros (0.00%)
Valores Distintos
[9, 1, 2, 3]
Contagem de NaN
0 registros (0.00%)

## ESQ_INI_N: Esquema terapêutico instituído por ocasião do diagnostico

        1. PQT/ PB/ 6 doses

        2. PQT/ MB/ 12 doses

        3. Outros Esquemas Substitutos

        9. Ignorado (Criado)

- Os valores não definidos foram substituidos por Ignorado (9)
'ESQ_INI_N_CAT': Esquema terapêutico instituído por ocasião do diagnostico (tratada 'ESQ_INI_N')       

#### ESQ_INI_N_CAT

Top 10 Frequências
               Frequência Absoluta  Frequência Relativa (%)
ESQ_INI_N_CAT                                              
2                           586425                59.593917
1                           332384                33.777660
3                            60422                 6.140229
9                             4804                 0.488194
Outlierss
4804 registros (0.49%)
Valores Distintos
[3, 1, 2, 9]
Contagem de NaN
0 registros (0.00%)


## CONTREG: Número de pessoas que residam ou tenham residido, nos últimos 5 anos com o doente, a contar da Data do diagnóstico

- Os valores não definidos foram substituidos por zero.
'CONTREG_CAT': Número de pessoas que residam ou tenham residido, nos últimos 5 anos com o doente, a contar da Data do diagnóstico (tratada 'CONTREG')

#### CONTREG_CAT

Top 10 Frequências
             Frequência Absoluta  Frequência Relativa (%)
CONTREG_CAT                                              
3                         175106                17.794692
0                         166110                16.880497
2                         159730                16.232146
4                         131789                13.392715
1                         129446                13.154613
5                          83026                 8.437302
6                          51082                 5.191076
7                          29617                 3.009751
8                          19895                 2.021778
9                          12070                 1.226582
Outlierss
38234 registros (3.89%)
Valores Distintos
[0, 3, 1, 4, 2, 5, 6, 7, 12, 8, 11, 10, 9, 17, 31, 15, 16, 13, 14, 19, 24, 23, 21, 22, 27, 45, 20, 18, 55, 28, 32, 33, 29, 30, 59, 34, 35, 25, 96, 39, 26, 40, 97, 92, 36, 43, 89, 66, 47, 57, 98, 70, 56, 99, 94, 38, 53, 37, 41, 69, 58, 80, 46, 62, 64, 76, 44, 48, 42, 75, 72, 50, 51, 74, 60, 49, 84, 85, 77, 63, 65, 78, 68, 52, 83, 54, 71, 61, 95]
Contagem de NaN
0 registros (0.00%)

## NERVOSAFET: Número de nervos afetados

- Os valores não definidos foram substituidos por zero.
'NERVOSAFET_CAT': Informar o resultado da baciloscopia (tratada 'NERVOSAFET')       

#### NERVOSAFET_CAT

Top 10 Frequências
                Frequência Absoluta  Frequência Relativa (%)
NERVOSAFET_CAT                                              
0                            734135                74.604562
2                             72115                 7.328499
1                             63568                 6.459933
4                             35316                 3.588897
3                             31472                 3.198260
6                             14199                 1.442936
5                             13288                 1.350358
8                              7007                 0.712068
10                             4609                 0.468378
7                              4178                 0.424578
Outlierss
114217 registros (11.61%)
Valores Distintos
[0, 20, 1, 4, 2, 6, 3, 8, 5, 15, 9, 7, 10, 12, 25, 18, 11, 16, 14, 21, 24, 13, 22, 19, 30, 17, 34, 60, 96, 90, 71, 26, 23, 33, 66, 32, 36, 42, 85, 99, 51, 50, 27, 29, 62, 45, 40, 44, 87, 55, 81, 68, 74, 28, 69, 56, 31, 91, 89, 39, 94, 63, 88, 93]
Contagem de NaN
0 registros (0.00%)

## AVAL_ATU_N: Avaliação de incapacidade física no momento da cura

        0. grau zero

        1. grau I

        2. grau II

        3. Não avaliado

        9- Ignorado

- Os valores não definidos (N e Nan) foram substituidos por Ignorado (9)
'AVAL_ATU_N_CAT': Avaliação de incapacidade física no momento da cura (tratada 'AVAL_ATU_N')       

#### AVAL_ATU_N_CAT

Top 10 Frequências
                Frequência Absoluta  Frequência Relativa (%)
AVAL_ATU_N_CAT                                              
0                            406518                41.311335
9                            277218                28.171559
3                            168595                17.133029
1                             96641                 9.820891
2                             35063                 3.563186
Outlierss
0 registros (0.00%)
Valores Distintos
[0, 2, 3, 1, 9]
Contagem de NaN
0 registros (0.00%)

## ESQ_ATU_N: Esquema terapêutico em uso 

        1- PQT/PB/06 doses

        2- PQT/MB/12 doses

        3- Outros Esquemas Substitutivos

- Os valores não definidos foram substituidos por Ignorado (9)
'ESQ_ATU_N_CAT': Esquema terapêutico em uso (tratada 'ESQ_ATU_N')       

#### ESQ_ATU_N_CAT

Top 10 Frequências
               Frequência Absoluta  Frequência Relativa (%)
ESQ_ATU_N_CAT                                              
2                           572013                58.129335
1                           317564                32.271616
3                            81611                 8.293506
9                            12847                 1.305543
Outlierss
12847 registros (1.31%)
Valores Distintos
[3, 1, 2, 9]
Contagem de NaN
0 registros (0.00%)

## DOSE_RECEB: Número de doses supervisionadas

- Os valores não definidos foram substituidos por zero
'DOSE_RECEB_CAT': Informar o resultado da baciloscopia (tratada 'DOSE_RECEB')       

#### DOSE_RECEB_CAT

Top 10 Frequências
                Frequência Absoluta  Frequência Relativa (%)
DOSE_RECEB_CAT                                              
0                            337140                34.260976
12                           304305                30.924205
6                            159536                16.212431
1                             32107                 3.262790
2                             19022                 1.933061
3                             16477                 1.674432
5                             15682                 1.593643
4                             15586                 1.583887
24                            12891                 1.310014
7                             11733                 1.192336
Outlierss
596 registros (0.06%)
Valores Distintos
[0, 12, 6, 3, 1, 9, 18, 24, 11, 7, 5, 23, 2, 21, 8, 17, 29, 13, 34, 14, 4, 16, 15, 10, 20, 25, 26, 22, 36, 19, 28, 27, 31, 35, 30, 54, 33, 69, 37, 55, 39, 32, 57, 42, 72, 48, 40, 47, 74, 46, 43, 66, 96, 61, 38, 70, 85, 52, 50, 51, 56, 60, 41, 65, 44, 99, 92, 83, 78, 84, 89, 64, 86, 90, 45, 63, 62, 71, 81, 91, 97, 53]
Contagem de NaN
0 registros (0.00%)

## EPIS_RACIO: Episódio Reacional Durante o Tratamento

        1- Reação tipo 1

        2- Reação tipo 2

        3- Reação tipo 1 e 2

        4- Sem Reação

        9- Ignorado (Criado)

- Os valores não definidos (N) foram substituidos por Ignorado (9)
'EPIS_RACIO_CAT': Episódio Reacional Durante o Tratamento (tratada 'EPIS_RACIO')      

#### EPIS_RACIO_CAT

Top 10 Frequências
                Frequência Absoluta  Frequência Relativa (%)
EPIS_RACIO_CAT                                              
9                            455448                46.283720
4                            427152                43.408212
1                             70134                 7.127186
2                             21239                 2.158358
3                             10062                 1.022525
Outlierss
0 registros (0.00%)
Valores Distintos
[9, 4, 1, 3, 2]
Contagem de NaN
0 registros (0.00%)

## CONTEXAM: Número de contatos examinados

- Os valores não definidos foram substituidos por zero.
'CONTEXAM_CAT': Número de contatos examinados (tratada 'CONTEXAM')       

#### CONTEXAM_CAT

Top 10 Frequências
              Frequência Absoluta  Frequência Relativa (%)
CONTEXAM_CAT                                              
0                          367354                37.331396
2                          138079                14.031920
1                          131093                13.321985
3                          129476                13.157662
4                           87420                 8.883830
5                           51298                 5.213026
6                           30245                 3.073570
7                           16613                 1.688253
8                           11251                 1.143354
9                            6363                 0.646623
Outlierss
32457 registros (3.30%)
Valores Distintos
[0, 2, 1, 3, 4, 5, 6, 11, 8, 7, 12, 9, 17, 10, 31, 16, 15, 14, 26, 22, 24, 13, 21, 18, 27, 19, 32, 20, 29, 43, 30, 35, 23, 70, 33, 25, 36, 71, 46, 80, 28, 74, 90, 40, 39, 42, 37, 57, 53, 62, 99, 54, 76, 44, 34, 38, 48, 56, 63, 75, 45, 72, 66, 50, 58, 49, 98, 55, 60, 51, 84, 85, 77, 52, 47, 92, 78, 68, 83, 41, 65, 69, 88, 95]
Contagem de NaN
0 registros (0.00%)


## TPALTA_N: Tipo de Saída

        1- Cura

        2- transf. p/ mesmo município

        3- transf. p/ outro município

        4- transf. p/ outro Estado

        5- transf. p/ outro país

        6- Óbito

        7- Abandono

        8- Erro diagnóstico

        9- transf. não especificada

- Os valores não definidos (Nan e N) foram substituidos por transf. não especificada (9).
'TPALTA_N_CAT': Tipo de Saída (tratada 'TPALTA_N')       

#### TPALTA_N_CAT

Top 10 Frequências
              Frequência Absoluta  Frequência Relativa (%)
TPALTA_N_CAT                                              
1                          754121                76.635587
9                           88344                 8.977729
7                           55872                 5.677847
3                           30711                 3.120926
6                           14902                 1.514377
4                           13395                 1.361232
8                           13158                 1.337148
2                           12822                 1.303002
5                             710                 0.072152
Outlierss
229914 registros (23.36%)
Valores Distintos
[1, 9, 7, 6, 4, 5, 8, 3, 2]
Contagem de NaN
0 registros (0.00%)
