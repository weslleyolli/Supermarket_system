#!/bin/bash

# Script para executar verificação do banco no WSL
# Usage: ./run_db_check_wsl.sh

echo "🚀 Iniciando verificação do banco de dados no WSL..."
echo "📂 Diretório atual: $(pwd)"
echo ""

# Verificar se estamos no diretório correto
if [ ! -f "check_database_structure_wsl.py" ]; then
    echo "❌ Erro: Arquivo check_database_structure_wsl.py não encontrado"
    echo "💡 Execute este script no diretório do projeto supermarket-system"
    exit 1
fi

# Verificar se Python3 está disponível
if ! command -v python3 &> /dev/null; then
    echo "❌ Erro: python3 não encontrado"
    echo "💡 Instale python3: sudo apt update && sudo apt install python3 python3-pip"
    exit 1
fi

# Verificar se pip está disponível
if ! command -v pip3 &> /dev/null; then
    echo "❌ Erro: pip3 não encontrado"
    echo "💡 Instale pip3: sudo apt install python3-pip"
    exit 1
fi

# Instalar dependências se necessário
echo "📦 Verificando dependências..."
python3 -c "import sqlalchemy" 2>/dev/null || {
    echo "📦 Instalando SQLAlchemy..."
    pip3 install sqlalchemy psycopg2-binary
}

python3 -c "import pydantic" 2>/dev/null || {
    echo "📦 Instalando Pydantic..."
    pip3 install pydantic
}

# Verificar se arquivo .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Aviso: Arquivo .env não encontrado"
    echo "💡 Certifique-se de que as variáveis de ambiente do banco estão configuradas"
fi

echo ""
echo "🔍 Executando verificação da estrutura do banco..."
echo "=================================================="
python3 check_database_structure_wsl.py

echo ""
echo "✅ Verificação concluída!"
echo ""
echo "💡 Para resolver problemas de Foreign Key:"
echo "   1. Se supplier_id não existir em products:"
echo "      alembic revision --autogenerate -m 'add_supplier_id_to_products'"
echo "      alembic upgrade head"
echo ""
echo "   2. Se as tabelas não existirem:"
echo "      alembic upgrade head"
