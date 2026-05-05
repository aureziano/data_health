#!/bin/bash
mkdir -p scripts_artigo/logs

# Desabilitar GPU para evitar conflitos de cuFFT/cuDNN se necessário
export CUDA_VISIBLE_DEVICES="-1"
export TF_CPP_MIN_LOG_LEVEL="2"

echo "Iniciando análise de incapacidade..."
.venv/bin/python3 scripts_artigo/analise_incapacidade.py > scripts_artigo/logs/analise_incapacidade.log 2>&1
echo "Status: $?"

echo "Iniciando comparativo de projeções..."
.venv/bin/python3 scripts_artigo/comparativo_projecoes.py > scripts_artigo/logs/comparativo_projecoes.log 2>&1
echo "Status: $?"

echo "Iniciando comparativo de forecast..."
.venv/bin/python3 scripts_artigo/comparativo_total_forecast.py > scripts_artigo/logs/comparativo_total_forecast.log 2>&1
echo "Status: $?"

echo "Sincronizando com Overleaf..."
make sync
