- TP_NOT: Tipo de Notificação [varchar(1)] # Valor Constante

        1 – Negativa

        2 – Individual

        3 – Surto

        4 – Agregado 

- TP_NOT.1: Tipo de Notificação  - 2 - Individual [varchar(1)] # Valor Constante

- ID_AGRAVO: Identificação de Agravo/Doença (CID) [varchar2(4)] # Valor Constante

- DT_NOTIFIC: Data da Notificação [date] # Ano mais importante

- NU_ANO: Ano da Notificação [varchar(4)]

- SG_UF_NOT: SG ? UF do Estado de Notificação [varchar(2)]

- ID_MUNICIP: Id de identificação do Municipio [varchar(6)]

- ID_REGIONA: Código da regional de saúde da tabela de município do sistema [varchar2(4)]

- ID_UNIDADE: Códigos e nomes de estabelecimento [varchar(7)] # sem necessidade

- DT_DIAG: Data do inicio do tratamento [date]

- SEM_DIAG: Semana epidemiológica do diagnóstico do caso notificado [varchar(6)] # sem necessidade

- ANO_NASC: Ano de Nascimento [date]

- NU_IDADE_N: Idade, com Código (4 - Ano e 0 para completar) A composição da variável obedece o seguinte critério: 1° dígito: Ex: 3009 – nove meses, 4018 – dezoito anos  [number(4)]

        1. Hora

        2. Dia

        3. Mês

        4. Ano
        
- CS_SEXO: Sexo [varchar(1)]

        0. Masculino

        1. Feminino

- CS_GESTANT: Código Gestante [varchar2(1)] # Não usar
        1. 1ºTrimestre 

        2. 2ºTrimestre 

        3. 3ºTrimestre

        4. Idade gestacional Ignorada 

        5. Não 

        6. Não se aplica

        9. Ignorado
        
- CS_RACA: Código Raça [varchar2(1)]

        1. Branca 

        2. Preta 

        3. Amarela

        4. Parda 

        5. Indígena 

        9. Ignorado

- CS_ESCOL_N: Código Escolaridade [varchar2(2)] # SN

        0. Analfabeto 

        1. 1ª a 4ª série incompleta do EF (antigo primário ou 1º grau) 

        2. 4ª série completa do EF (antigo primário ou 1º grau)

        3. 5ª à 8ª série incompleta do EF (antigo ginásio ou 1º grau) 

        4. Ensino fundamental completo (antigo ginásio ou 1º grau) 

        5. Ensino médio incompleto (antigo colegial ou 2º grau )

        6. Ensino médio completo (antigo colegial ou 2º grau ) 

        7. Educação superior incompleta 

        8. Educação superior completa 

        9. Ignorado 

        10. Não se aplica

- SG_UF: Código do Estado Notificante  [varchar(2)] # DUP

- ID_MN_RESI: Código do município de residência do caso notificado  [varchar2(6)] #DUP

- ID_RG_RESI: Regional de saúde onde está localizado o município de residência do paciente por ocasião da notificação [varchar2(4)] #DUP

- ID_PAIS: País onde residia o paciente por ocasião da notificação  [varchar(4)] #SN

- NDUPLIC_N: Identifica duplicidade  [varchar2(1)] # Retirar depois de eliminar

        0 ou branco – Não identificado

        1 – Não é duplicidade (nãolistar)

        2 – Duplicidade (não contar) 

- DT_DIGITA: Data de digitação [date] #SN

- DT_TRANSUS: Data de transferência da unidade de saúde [date] #SN

- DT_TRANSDM: Data de transferência do distrito municipal [date] #SN

- DT_TRANSSM: Data de transferência da secretaria municipal de saúde [date] #SN

- DT_TRANSRM: Data de transferência da regional municipal [date] # Valor Constante

- DT_TRANSRS: Data de transferência da regional de saúde [date] #SN

- DT_TRANSSE: Data de transferência da secretaria estadual de saúde [date] #SN

- NU_LOTE_V: Identifica o Lote da transferência da notificação um nível do sistema para outro #SN

- NU_LOTE_H: Identifica do Lote da transferência de registros dentro de um mesmo nível do sistema #SN

- CS_FLXRET: Identifica se o registro está habilitado ou foi enviado pelo fluxo de retorno para o município de residência # Valor Constante

        0 - Não

        1 - habilitado para envio.

        2 - enviado 

- FLXRECEBI: Identifica se o registro foi recebido pelo fluxo de retorno [varchar2(1)] # Valor Constante

- MIGRADO_W: Identifica se o registro é oriundo da rotina de migração da base Windows. [varchar2(1)] #SN

        1. migrado do Sinan Windows 

- ID_OCUPA_N: Ocupação do indivíduo que sofreu o agravo (Tabela CBO) [varchar2(6)] #SN

- NU_LESOES:  Nº de lesões cutâneas [numeric(2)]

- FORMACLINI: Forma clínica inicial por ocasião do diagnóstico, segundo classificação de Madrid [varchar(1)] 

        1- I -Indeterminada

        2- T - Tuberculóide

        3- D - Dimorfa

        4- V - Virchowiana

        5- Não classificado

- AVALIA_N: Avaliação do Grau de Incapacidade Física no Diagnóstico [varchar(1)]

        0 Grau zero

        1- Grau I

        2- Grau II

        3 - Não avaliado

- CLASSOPERA: Classificação operacional, por ocasião do diagnóstico, para eleição do esquema terapêutico [varchar(1)]

        1- PB - Paucibacilar

        2- MB - Multibacilar

- MODOENTR: Modo de entrada do paciente no sistema [varchar(1)]

        1- Caso novo

        2- Transferencia do mesmo município (outra unidade)

        3- Transferência de outro município (mesma UF)

        4- Transferência de outro estado

        5- Transferencia de outro país

        6- Recidiva

        7- Outros reingressos

        9- Ignorado

- MODODETECT: Modo de detecção do caso novo [varchar(1)]

        1- Encaminhamento

        2- Demanda espontânea

        3- Exame de coletividade

        4- Exame de contatos

        5- Outros modos

        9- Ignorado

- BACILOSCOP: Informar o resultado da baciloscopia [varchar(1)]

        1. Positiva

        2. Negativa

        3. Não realizada

        9. Ignorado

- DTINICTRAT: Data do inicio do tratamento [date]

- ESQ_INI_N: Esquema terapêutico instituído por ocasião do diagnostico [varchar(1)]

        1. PQT/ PB/ 6 doses

        2. PQT/ MB/ 12 doses

        3. Outros Esquemas Substitutos

- CONTREG: Número de pessoas que residam ou tenham residido, nos últimos 5 anos com o doente, a contar da Data do diagnóstico [numeric(2)]

- NERVOSAFET: Número de nervos afetados [numeric(2)]

- UFATUAL : Código da UF do cadastro do IBGE [varchar(2)] # Valor Constante

- ID_MUNI_AT :Código e nome dos municípios do cadastro do IBGE [varchar(6)] #SN

- DT_NOTI_AT: Data de notificação atual [date] #SN

- ID_UNID_AT: Códigos e nomes de estabelecimentos de saúde (CNES) [varchar(7)] #SN

- UFRESAT: Sigla da UF de residência atual do paciente [varchar(2)] #SN

- MUNIRESAT: código IBGE do município de residência atual do paciente [varchar(6)] #SN

- DTULTCOMP: Data do último comparecimento [date]

- CLASSATUAL: Classificação operacional atual [varchar(1)]

        1. PB (Paucibacilar) 

        2. MB (Multibacilar) 

- AVAL_ATU_N: Avaliação de incapacidade física no momento da cura - [varchar(1)]

        0. grau zero

        1. grau I

        2. grau II

        3. Não avaliado

        9- Ignorado

- ESQ_ATU_N: Esquema terapêutico em uso [varchar(1)]

        1- PQT/PB/06 doses

        2- PQT/MB/12 doses

        3- Outros Esquemas Substitutivos

- DOSE_RECEB: Número de doses supervisionadas [numeric(2)]

- EPIS_RACIO: Episódio Reacional Durante o Tratamento [varchar(1)]

        1- Reação tipo 1

        2- Reação tipo 2

        3- Reação tipo 1 e 2

- DTMUDESQ:  Data de mudança do Esquema [date]

- CONTEXAM: Número de contatos examinados [numeric(2)]

- DTALTA_N: Data da alta [date]

- TPALTA_N: Tipo de Saída [varchar(1)]

        1- Cura

        2- transf. p/ mesmo município

        3- transf. p/ outro município

        4- transf. p/ outro Estado

        5- transf. p/ outro país

        6- Óbito

        7- Abandono

        8- Erro diagnóstico

        9- transf. não especificada

- IN_VINCULA: Vinculação [varchar(1)]

        0 - Não Vinculada

        1 - Vinculada
        
- NU_LOTE_IA: Transferência vertical da investigação e do acompanhamento [varchar(7)]
