#!/bin/bash

# Script para popular o banco de dados com dados de exemplo
# Este script configura o PYTHONPATH e executa o populate_sample_data.py

# Definir o diretório atual como PYTHONPATH
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Executar o script de população
python scripts/populate_sample_data.py
