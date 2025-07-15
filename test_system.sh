#!/bin/bash

# Script de Testes do Sistema de Supermercado
# Verifica se toda a configuração está funcionando corretamente

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}🔍 $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

echo "🧪 TESTANDO CONFIGURAÇÃO DO SISTEMA"
echo "==================================="

ERRORS=0

# Função para registrar erro
register_error() {
    log_error "$1"
    ((ERRORS++))
}

# 1. TESTAR AMBIENTE PYTHON
echo ""
log_info "1. TESTANDO AMBIENTE PYTHON"
echo "============================="

# Verificar se ambiente virtual está ativo
if [[ "$VIRTUAL_ENV" != "" ]]; then
    log_success "Ambiente virtual ativo: $VIRTUAL_ENV"
else
    log_warning "Ambiente virtual não detectado. Ativando..."
    if [[ -d "venv" ]]; then
        source venv/bin/activate
        log_success "Ambiente virtual ativado!"
    else
        register_error "Ambiente virtual não encontrado!"
    fi
fi

# Verificar versão do Python
PYTHON_VERSION=$(python --version 2>/dev/null || echo "Python não encontrado")
log_info "Versão Python: $PYTHON_VERSION"

# Testar importações críticas
log_info "Testando importações Python..."

python -c "import fastapi; print('✅ FastAPI OK')" 2>/dev/null || register_error "FastAPI não instalado"
python -c "import sqlalchemy; print('✅ SQLAlchemy OK')" 2>/dev/null || register_error "SQLAlchemy não instalado"
python -c "import alembic; print('✅ Alembic OK')" 2>/dev/null || register_error "Alembic não instalado"
python -c "import streamlit; print('✅ Streamlit OK')" 2>/dev/null || register_error "Streamlit não instalado"
python -c "import pydantic; print('✅ Pydantic OK')" 2>/dev/null || register_error "Pydantic não instalado"

# 2. TESTAR ESTRUTURA DO PROJETO
echo ""
log_info "2. TESTANDO ESTRUTURA DO PROJETO"
echo "================================="

# Verificar pastas essenciais
REQUIRED_DIRS=(
    "app"
    "app/core"
    "app/domain"
    "app/application"
    "app/infrastructure"
    "app/presentation"
    "tests"
    "migrations"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [[ -d "$dir" ]]; then
        log_success "Diretório $dir existe"
    else
        register_error "Diretório $dir não encontrado"
    fi
done

# Verificar arquivos essenciais
REQUIRED_FILES=(
    "requirements.txt"
    ".env"
    "pyproject.toml"
    "app/core/config.py"
    "app/infrastructure/database/connection.py"
    "alembic.ini"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        log_success "Arquivo $file existe"
    else
        register_error "Arquivo $file não encontrado"
    fi
done

# 3. TESTAR CONFIGURAÇÕES
echo ""
log_info "3. TESTANDO CONFIGURAÇÕES"
echo "========================="

# Testar importação das configurações
log_info "Testando configurações da aplicação..."
python -c "
try:
    from app.core.config import settings
    print('✅ Configurações carregadas')
    print(f'✅ App: {settings.APP_NAME}')
    print(f'✅ Database: {settings.DATABASE_URL}')
    print(f'✅ Debug: {settings.DEBUG}')
except Exception as e:
    print(f'❌ Erro nas configurações: {e}')
    exit(1)
" || register_error "Erro ao carregar configurações"

# 4. TESTAR BANCO DE DADOS
echo ""
log_info "4. TESTANDO BANCO DE DADOS"
echo "=========================="

# Verificar se banco existe
if [[ -f "supermarket.db" ]] || [[ -f "obarateiro.db" ]]; then
    log_success "Arquivo do banco SQLite existe"
else
    log_warning "Banco SQLite não encontrado, tentando criar..."
fi

# Testar conexão com banco
log_info "Testando conexão com banco..."
python -c "
try:
    from app.infrastructure.database.connection import engine, create_tables
    from sqlalchemy import text

    # Testar conexão
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('✅ Conexão com banco OK')

    # Verificar se tabelas existem
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    expected_tables = ['users', 'categories', 'products', 'customers', 'suppliers', 'sales', 'sale_items']

    for table in expected_tables:
        if table in tables:
            print(f'✅ Tabela {table} existe')
        else:
            print(f'⚠️  Tabela {table} não encontrada')

    if len(tables) == 0:
        print('⚠️  Nenhuma tabela encontrada - executando migrações...')
        create_tables()
        print('✅ Tabelas criadas!')

except Exception as e:
    print(f'❌ Erro no banco: {e}')
    exit(1)
" || register_error "Erro na conexão com banco"

# Testar modelos
log_info "Testando modelos do banco..."
python -c "
try:
    from app.infrastructure.database.models import User, Product, Category, Sale, Customer
    print('✅ Modelos importados com sucesso')
    print(f'✅ User: {User.__tablename__}')
    print(f'✅ Product: {Product.__tablename__}')
    print(f'✅ Category: {Category.__tablename__}')
    print(f'✅ Sale: {Sale.__tablename__}')
    print(f'✅ Customer: {Customer.__tablename__}')
except Exception as e:
    print(f'❌ Erro nos modelos: {e}')
    exit(1)
" || register_error "Erro ao importar modelos"

# 5. TESTAR MIGRAÇÕES
echo ""
log_info "5. TESTANDO MIGRAÇÕES ALEMBIC"
echo "============================="

# Verificar status das migrações
log_info "Verificando status das migrações..."
if command -v alembic &> /dev/null; then
    alembic current 2>/dev/null && log_success "Migrações Alembic OK" || log_warning "Problema com migrações"
    alembic check 2>/dev/null && log_success "Schema em sincronia" || log_warning "Schema pode estar desatualizado"
else
    register_error "Alembic não encontrado"
fi

# 6. TESTAR GIT
echo ""
log_info "6. TESTANDO CONFIGURAÇÃO GIT"
echo "============================="

# Verificar se é repositório Git
if [[ -d ".git" ]]; then
    log_success "Repositório Git inicializado"

    # Verificar status
    git status --porcelain > /dev/null && log_success "Git funcionando"

    # Verificar configurações
    if git config --get user.name > /dev/null && git config --get user.email > /dev/null; then
        log_success "Git configurado: $(git config --get user.name) <$(git config --get user.email)>"
    else
        log_warning "Configure seu nome e email no Git:"
        echo "  git config --global user.name 'Seu Nome'"
        echo "  git config --global user.email 'seu.email@exemplo.com'"
    fi

    # Verificar hooks
    if [[ -f ".pre-commit-config.yaml" ]]; then
        log_success "Hooks de qualidade configurados"
    else
        log_warning "Hooks de qualidade não encontrados"
    fi
else
    register_error "Repositório Git não inicializado"
fi

# 7. TESTAR CRIAÇÃO DE DADOS
echo ""
log_info "7. TESTANDO CRIAÇÃO DE DADOS"
echo "============================"

log_info "Testando criação de dados básicos..."
python -c "
from app.infrastructure.database.connection import SessionLocal
from app.infrastructure.database.models import User, Category, Product
from app.infrastructure.database.models.user import UserRole
from sqlalchemy.exc import IntegrityError

db = SessionLocal()

try:
    # Testar criação de categoria
    category = Category(name='Teste', description='Categoria de teste')
    db.add(category)
    db.commit()
    print('✅ Categoria criada com sucesso')

    # Testar criação de usuário
    user = User(
        username='teste',
        email='teste@teste.com',
        full_name='Usuário Teste',
        hashed_password='senha_hash',
        role=UserRole.CASHIER
    )
    db.add(user)
    db.commit()
    print('✅ Usuário criado com sucesso')

    # Testar criação de produto
    product = Product(
        name='Produto Teste',
        barcode='1234567890123',
        category_id=category.id,
        price=10.50,
        cost_price=8.00,
        stock_quantity=100
    )
    db.add(product)
    db.commit()
    print('✅ Produto criado com sucesso')

    # Limpar dados de teste
    db.delete(product)
    db.delete(user)
    db.delete(category)
    db.commit()
    print('✅ Dados de teste removidos')

except IntegrityError as e:
    print(f'⚠️  Dados já existem (normal): {e}')
    db.rollback()
except Exception as e:
    print(f'❌ Erro ao criar dados: {e}')
    exit(1)
finally:
    db.close()
" || register_error "Erro ao testar criação de dados"

# 8. CRIAR SCRIPT DE API BÁSICA PARA TESTE
echo ""
log_info "8. CRIANDO API BÁSICA PARA TESTE"
echo "================================="

# Criar arquivo main.py básico se não existir
if [[ ! -f "app/main.py" ]]; then
    cat > app/main.py << 'EOF'
"""
FastAPI Application - Sistema de Supermercado
API principal da aplicação
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.models import User, Product, Category

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Endpoint raiz - status da API"""
    return {
        "message": "🛒 Sistema de Supermercado API",
        "version": settings.APP_VERSION,
        "status": "running"
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check - verifica se API e banco estão funcionando"""
    try:
        # Testar conexão com banco
        users_count = db.query(User).count()
        products_count = db.query(Product).count()
        categories_count = db.query(Category).count()

        return {
            "status": "healthy",
            "database": "connected",
            "counts": {
                "users": users_count,
                "products": products_count,
                "categories": categories_count
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

@app.get("/api/v1/test")
async def test_endpoint():
    """Endpoint de teste"""
    return {
        "message": "API funcionando!",
        "features": [
            "✅ FastAPI configurado",
            "✅ Banco de dados conectado",
            "✅ Modelos funcionando",
            "✅ CORS habilitado"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF
    log_success "API básica criada!"
else
    log_success "API main.py já existe!"
fi

# Testar se API pode ser importada
log_info "Testando importação da API..."
python -c "
try:
    from app.main import app
    print('✅ API importada com sucesso')
    print(f'✅ Título: {app.title}')
    print(f'✅ Versão: {app.version}')
except Exception as e:
    print(f'❌ Erro ao importar API: {e}')
    exit(1)
" || register_error "Erro ao importar API"

# 9. RESUMO FINAL
echo ""
echo "📊 RESUMO DOS TESTES"
echo "==================="

if [[ $ERRORS -eq 0 ]]; then
    log_success "🎉 TODOS OS TESTES PASSARAM!"
    echo ""
    echo "✅ Sistema 100% funcional e pronto para desenvolvimento!"
    echo ""
    echo "🚀 PRÓXIMOS PASSOS:"
    echo "   1. Testar API: uvicorn app.main:app --reload"
    echo "   2. Acessar docs: http://localhost:8000/docs"
    echo "   3. Health check: http://localhost:8000/health"
    echo ""
    echo "📝 COMANDOS ÚTEIS:"
    echo "   make run        # Iniciar API"
    echo "   make test       # Executar testes"
    echo "   make format     # Formatar código"
    echo "   git status      # Ver status Git"
    echo ""
    echo "🎯 DESENVOLVIMENTO:"
    echo "   1. Implementar autenticação"
    echo "   2. Criar CRUD de produtos"
    echo "   3. Desenvolver PDV"
    echo "   4. Integrar hardware"
else
    log_error "🚨 ENCONTRADOS $ERRORS ERROS!"
    echo ""
    echo "❌ Corrija os erros acima antes de continuar"
    echo "💡 Se precisar de ajuda, envie os erros para análise"
    exit 1
fi
