import os
import subprocess
import sys
import time

def run_script(script_path, description):
    """
    Executa um script Python individual e mensura seu tempo de execução.
    """
    print(f"\n{'='*80}")
    print(f"🚀 INICIANDO: {description}")
    print(f"📄 Arquivo: {script_path}")
    print(f"{'='*80}")
    
    start_time = time.time()
    
    try:
        # Executa o script usando o interpretador do ambiente virtual ativado
        # O PYTHONPATH é ajustado dinamicamente caso o script precise importar módulos na raiz (como config.py)
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            env={"PYTHONPATH": ".", **os.environ}
        )
        
        elapsed = time.time() - start_time
        print(f"\n✅ SUCESSO: {description} concluído em {elapsed:.2f} segundos.")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ ERRO: Falha ao executar {script_path}.")
        print(f"Código de retorno: {e.returncode}")
        return False

def main():
    """
    Script principal que orquestra a geração de todos os dados (figuras e tabelas) 
    para o documento no Overleaf. Organizado por etapas que seguem a linha lógica da dissertação.
    """
    print("Iniciando o Pipeline Geral de Geração de Dados para a Dissertação...\n")
    start_total = time.time()

    # Estrutura do pipeline dividida em fases essenciais.
    pipeline = [
        {
            "fase": "FASE 1: Preparação de Dados",
            "scripts": [
                ("scripts_artigo/tratamento_variaveis.py", "Tratamento de Dados Base (Prepara dados_tratados.csv)"),
                # eda.py pode ser opcional aqui, adiciono para garantir geração, se aplicável, ou focamos só nos obrigatórios de figures
            ]
        },
        {
            "fase": "FASE 2: Clusterização e Perfis (Capítulo 4)",
            "scripts": [
                ("scripts_artigo/gerar_comparativo_validacao.py", "Validação Cruzada vs Walk-Forward (Figuras Didáticas)"),
                ("scripts_artigo/analise_regional_populacao.py", "Geração de Indicadores Normalizados de G2D por População (Tabela/Gráfico)"),
                ("scripts_artigo/analise_incapacidade.py", "Clusterização UMAP + K-Means e Justificativas de Gravidade"),
                ("scripts_artigo/comparativo_projecoes.py", "Geração de métricas de Projeção Comparativas (PCA vs t-SNE vs UMAP)"),
                ("scripts_artigo/perfil_cluster_gravidade.py", "Geração da Tabela e Gráficos de Perfil Extendido de Clusters"),
                ("scripts_artigo/gerar_analise_silhueta.py", "Validação Silhouette K=2 vs K=3"),
                ("scripts_artigo/ilustracoes_refinamento.py", "Geração de Ilustrações Conceituais (Sliding Window, etc.)")
            ]
        },
        {
            "fase": "FASE 3: Modelagem Preditiva e Séries Temporais (Capítulo 5)",
            "scripts": [
                ("scripts_artigo/analise_completa_series.py", "Modelagem Comparativa de Séries Temporais (SARIMA, Prophet, XGBoost, etc.)"),
                ("scripts_artigo/analise_paradoxo_pandemia.py", "Validação ITS e Falsa Cura do Paradoxo da Gravidade Pandêmica [Ref: 72]"),
                ("scripts_artigo/modelagem_avancada.py", "Modelagem com LightGBM + SMOTE e Exportação de Resultados"),
                ("scripts_artigo/gerar_shap_beeswarm.py", "Explicabilidade SHAP Expandida (Beeswarm, Bar, Waterfall)")
            ]
        },
        {
            "fase": "FASE 4: Apêndice Socio-Clínico (Apêndice A)",
            "scripts": [
                ("scripts_artigo/analise_variaveis_avancada.py", "Transparência Metodológica e Relatório de Imputação/Associação (MI e KW) [Ref: 210, 254]"),
                ("scripts_artigo/analise_incapacidade_v3.py", "Preparação das Estatísticas por Microrregião e Classe (V3)"),
                ("scripts_artigo/visualizar_incapacidade_v3.py", "Geração de Mapas Regionais e Painéis Socio-clínicos (V3)")
            ]
        }
    ]

    # Cria diretórios necessários para saídas globais apenas por segurança, embora os scripts devam fazer isso
    os.makedirs("overleaf/fig/incapacidade", exist_ok=True)
    os.makedirs("overleaf/tabs", exist_ok=True)
    os.makedirs("overleaf/compilado", exist_ok=True)

    for etapa in pipeline:
        print(f"\n{'#'*80}")
        print(f" {etapa['fase'].upper()} ")
        print(f"{'#'*80}")
        
        for filepath, desc in etapa['scripts']:
            if not os.path.exists(filepath):
                print(f"⚠️ AVISO: O arquivo {filepath} não foi encontrado. Ignorando...")
                continue
                
            sucesso = run_script(filepath, desc)
            
            if not sucesso:
                print("\n⛔ FALHA NO PIPELINE: Parando execução para evitar propagação de erros.")
                sys.exit(1)

    elapsed_total = time.time() - start_total
    print(f"\n{'='*80}")
    print(f"🎉 PIPELINE CONCLUÍDO COM SUCESSO!")
    print(f"⏱️  Tempo Total de Execução: {elapsed_total / 60:.2f} minutos.")
    print("📍 Todos os artefatos visuais e tabulares estão prontos nas pastas 'overleaf/fig/' e 'overleaf/tabs/'.")
    print("📝 Você já pode executar o comando 'make pdf' de forma segura.")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
