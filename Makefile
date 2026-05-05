# Makefile para automação da Dissertação (Build Persistente)

CONTAINER_NAME=data_health-dissertacao-latex-1
SERVICE_NAME=dissertacao-latex

.PHONY: pdf clean logs bash sync stop start all force dados_over

all: pdf

# Orquestra a geração de todos os dados do Overleaf (rodando no ambiente virtual ativado)
dados_over:
	.venv/bin/python3 gerar_dados_overleaf.py

# Sincroniza artefatos gerados pelos scripts Python
sync:
	mkdir -p overleaf/tabs overleaf/fig overleaf/compilado
	# Copiar tabelas
	cp -r scripts_artigo/relatorios/*.tex overleaf/tabs/ 2>/dev/null || true
	# Copiar gráficos
	cp -r scripts_artigo/graficos/modelagem_avancada/*.png overleaf/fig/ 2>/dev/null || true
	cp -r scripts_artigo/graficos/comparativo_projecoes/*.png overleaf/fig/ 2>/dev/null || true
	cp -r scripts_artigo/graficos/series_temporais/*.png overleaf/fig/ 2>/dev/null || true
	cp -r scripts_artigo/graficos/clinica/*.png overleaf/fig/ 2>/dev/null || true
	cp -r overleaf/fig/incapacidade/*.png overleaf/fig/ 2>/dev/null || true
	# Limpeza ESTRITAMENTE isolada apenas para arquivos de TABELAS gerados
	@for f in overleaf/tabs/*.tex; do \
		if [ -f "$$f" ]; then \
			# Escapar underscores em texto (apenas se não houver um \ antes) \
			sed -i 's/\([^\\]\)_/\1\\_/g' "$$f" 2>/dev/null || true; \
			# Escapar porcentagem em texto \
			sed -i 's/\([^\\]\)%/\1\\%/g' "$$f" 2>/dev/null || true; \
			# Limpar labels/captions duplicados que alguns scripts colocam no .tex \
			sed -i '/\\label/d' "$$f" 2>/dev/null || true; \
			sed -i '/\\caption/d' "$$f" 2>/dev/null || true; \
			sed -i '/\\begin{table}/d' "$$f" 2>/dev/null || true; \
			sed -i '/\\end{table}/d' "$$f" 2>/dev/null || true; \
			sed -i '/\\centering/d' "$$f" 2>/dev/null || true; \
		fi; \
	done

# Garante que o container está rodando
start:
	@if [ -z "$$(docker ps -q -f name=$(CONTAINER_NAME))" ]; then \
		echo "Iniciando container..."; \
		docker compose up -d; \
		sleep 2; \
	fi

# Gera o PDF via docker exec
pdf: sync start
	docker exec $(CONTAINER_NAME) /bin/bash -c "latexmk -pdf -g -interaction=nonstopmode -synctex=1 -file-line-error -output-directory=compilado main_dis.tex"

# Gera os Slides de Apresentação
pres: sync start
	docker exec $(CONTAINER_NAME) /bin/bash -c "latexmk -pdf -g -interaction=nonstopmode -synctex=1 -file-line-error -output-directory=compilado apresentacao.tex"

# Limpa o cache do LaTeX
clean: start
	docker exec $(CONTAINER_NAME) /bin/bash -c "latexmk -C -output-directory=compilado main_dis.tex"
	docker exec $(CONTAINER_NAME) /bin/bash -c "latexmk -C -output-directory=compilado apresentacao.tex"
	cd overleaf && rm -f *.aux *.bbl *.bcf *.blg *.fdb_latexmk *.fls *.lof *.lot *.out *.run.xml *.toc *.synctex.gz *.log
	rm -rf overleaf/compilado/*

# Encerra o container
stop:
	docker compose stop

# Acompanha logs
logs:
	docker logs -f $(CONTAINER_NAME)

# Bash interativo
bash: start
	docker exec -it $(CONTAINER_NAME) /bin/bash
