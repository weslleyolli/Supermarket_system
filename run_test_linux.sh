#!/bin/bash
# Script para testar o StockService no Linux/macOS

echo "🐧 EXECUTANDO TESTE NO LINUX/UNIX..."
echo "=================================="

# Navegar para o diretório do projeto
cd "$(dirname "$0")"

# Verificar se Python está disponível
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Instale o Python3 primeiro."
    exit 1
fi

# Executar o teste
python3 test_stock_service_implementation.py

echo ""
echo "💡 Para executar diretamente:"
echo "   chmod +x test_stock_service_implementation.py"
echo "   ./test_stock_service_implementation.py"
