#!/bin/bash

# Script de Setup Completo do Ambiente
# Sistema de Gestão de Supermercado

set -e  # Para o script se houver erro

echo "🚀 SETUP DO AMBIENTE - SISTEMA DE SUPERMERCADO"
echo "================================================"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Verificar se estamos no diretório correto
if [[ ! -f "requirements.txt" ]]; then
    log_error "Execute este script no diretório raiz do projeto (onde está o requirements.txt)"
    exit 1
fi


# 2. CONFIGURAR BANCO DE DADOS
echo ""
log_info "2. CONFIGURANDO BANCO DE DADOS"
echo "==============================="

# Criar arquivo de configuração do banco
cat > app/__init__.py << 'EOF'
"""
Sistema de Gestão de Supermercado
Aplicação principal
"""

__version__ = "1.0.0"
__author__ = "Equipe de Desenvolvimento"
EOF

# Configuração principal da aplicação
cat > app/core/__init__.py << 'EOF'
"""
Core module - Configurações centrais da aplicação
"""
EOF

cat > app/core/config.py << 'EOF'
"""
Configurações da aplicação
"""

from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """Configurações da aplicação"""

    # Informações da aplicação
    APP_NAME: str = "Sistema de Gestão de Supermercado"
    APP_VERSION: str = "1.0.0"
    DESCRIPTION: str = "Sistema completo para gestão de supermercado"

    # API
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # Segurança
    SECRET_KEY: str = "sua-chave-secreta-super-segura-mude-em-producao"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Banco de dados
    DATABASE_URL: str = "sqlite:///./supermarket.db"
    DATABASE_URL_DEV: str = "sqlite:///./supermarket_dev.db"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8501",
    ]

    # Hardware
    BARCODE_READER_ENABLED: bool = False
    BARCODE_READER_PORT: str = "auto"
    SCALE_ENABLED: bool = False
    SCALE_PORT: str = "COM1"
    SCALE_BAUDRATE: int = 9600
    PRINTER_ENABLED: bool = False
    PRINTER_PORT: str = "COM2"

    # Logs
    LOG_LEVEL: str = "INFO"

    # Campos extras do .env
    PAYMENT_TERMINAL_ENABLED: bool = False
    ENVIRONMENT: str = "development"
    BACKUP_ENABLED: bool = True
    BACKUP_INTERVAL_HOURS: int = 24

    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Retorna instância singleton das configurações"""
    return Settings()


# Instância global das configurações
settings = get_settings()
EOF

# Configuração do banco de dados
cat > app/infrastructure/database/__init__.py << 'EOF'
"""
Database infrastructure
"""
EOF

cat > app/infrastructure/database/connection.py << 'EOF'
"""
Configuração da conexão com banco de dados
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Engine do SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG  # Log SQL queries em desenvolvimento
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()


def get_db():
    """
    Dependency para obter sessão do banco de dados
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Cria todas as tabelas no banco de dados
    """
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    Remove todas as tabelas do banco de dados
    """
    Base.metadata.drop_all(bind=engine)
EOF

# Modelo base
cat > app/infrastructure/database/models/__init__.py << 'EOF'
"""
Database models
"""

from .base import Base
from .user import User
from .product import Product, Category
from .sale import Sale, SaleItem
from .customer import Customer
from .supplier import Supplier

__all__ = [
    "Base",
    "User",
    "Product",
    "Category",
    "Sale",
    "SaleItem",
    "Customer",
    "Supplier"
]
EOF

cat > app/infrastructure/database/models/base.py << 'EOF'
"""
Modelo base para todos os modelos da aplicação
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseModel(Base):
    """
    Modelo base com campos comuns
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
EOF

cat > app/infrastructure/database/models/user.py << 'EOF'
"""
Modelo de usuário
"""

from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class UserRole(str, enum.Enum):
    """Tipos de usuário"""
    ADMIN = "admin"
    MANAGER = "manager"
    CASHIER = "cashier"
    SUPERVISOR = "supervisor"


class User(BaseModel):
    """Modelo de usuário do sistema"""
    __tablename__ = "users"

    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CASHIER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    sales = relationship("Sale", back_populates="user")
EOF

cat > app/infrastructure/database/models/product.py << 'EOF'
"""
Modelos de produto e categoria
"""

from sqlalchemy import Column, String, Float, Integer, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import BaseModel


class Category(BaseModel):
    """Categoria de produtos"""
    __tablename__ = "categories"

    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    products = relationship("Product", back_populates="category")


class Product(BaseModel):
    """Produto"""
    __tablename__ = "products"

    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    barcode = Column(String(50), unique=True, index=True, nullable=False)

    # Categoria
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    # Preços
    price = Column(Float, nullable=False)  # Preço de venda
    cost_price = Column(Float, nullable=False)  # Preço de custo

    # Estoque
    stock_quantity = Column(Float, default=0, nullable=False)
    min_stock_level = Column(Float, default=0, nullable=False)

    # Tipo de produto
    unit_type = Column(String(20), default="unidade", nullable=False)  # unidade, peso, volume
    requires_weighing = Column(Boolean, default=False, nullable=False)
    tare_weight = Column(Float, default=0)  # Peso da embalagem

    # Promoções
    bulk_discount_enabled = Column(Boolean, default=False, nullable=False)
    bulk_min_quantity = Column(Float, default=10)
    bulk_discount_percentage = Column(Float, default=5.0)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    category = relationship("Category", back_populates="products")
    sale_items = relationship("SaleItem", back_populates="product")
EOF

cat > app/infrastructure/database/models/sale.py << 'EOF'
"""
Modelos de venda
"""

from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel
import enum


class PaymentMethod(str, enum.Enum):
    """Métodos de pagamento"""
    CASH = "cash"
    DEBIT_CARD = "debit_card"
    CREDIT_CARD = "credit_card"
    PIX = "pix"


class SaleStatus(str, enum.Enum):
    """Status da venda"""
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Sale(BaseModel):
    """Venda"""
    __tablename__ = "sales"

    # Cliente (opcional)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)

    # Funcionário responsável
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Valores
    subtotal_amount = Column(Float, default=0, nullable=False)
    discount_amount = Column(Float, default=0, nullable=False)
    bulk_discount_amount = Column(Float, default=0, nullable=False)
    final_amount = Column(Float, default=0, nullable=False)

    # Pagamento
    payment_method = Column(Enum(PaymentMethod), nullable=False)

    # Status
    status = Column(Enum(SaleStatus), default=SaleStatus.PENDING, nullable=False)

    # Relacionamentos
    user = relationship("User", back_populates="sales")
    customer = relationship("Customer", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")


class SaleItem(BaseModel):
    """Item de venda"""
    __tablename__ = "sale_items"

    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    quantity = Column(Float, nullable=False)
    weight = Column(Float, nullable=True)  # Para produtos por peso

    unit_price = Column(Float, nullable=False)
    original_total_price = Column(Float, nullable=False)
    discount_applied = Column(Float, default=0, nullable=False)
    bulk_discount_applied = Column(Float, default=0, nullable=False)
    final_total_price = Column(Float, nullable=False)

    # Relacionamentos
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")
EOF

cat > app/infrastructure/database/models/customer.py << 'EOF'
"""
Modelo de cliente
"""

from sqlalchemy import Column, String, Float
from sqlalchemy.orm import relationship
from .base import BaseModel


class Customer(BaseModel):
    """Cliente"""
    __tablename__ = "customers"

    name = Column(String(200), nullable=False, index=True)
    email = Column(String(100), unique=True, index=True)
    phone = Column(String(20))
    cpf = Column(String(14), unique=True, index=True)
    address = Column(String(500))

    # Programa de fidelidade
    loyalty_points = Column(Float, default=0, nullable=False)

    # Relacionamentos
    sales = relationship("Sale", back_populates="customer")
EOF

cat > app/infrastructure/database/models/supplier.py << 'EOF'
"""
Modelo de fornecedor
"""

from sqlalchemy import Column, String
from .base import BaseModel


class Supplier(BaseModel):
    """Fornecedor"""
    __tablename__ = "suppliers"

    name = Column(String(200), nullable=False, index=True)
    contact_person = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    cnpj = Column(String(18), unique=True, index=True)
    address = Column(String(500))
EOF

# Configuração do Alembic
cat > alembic.ini << 'EOF'
# A generic, single database configuration.

[alembic]
# path to migration scripts
script_location = migrations

# template used to generate migration file names; The default value is %%(rev)s_%%(slug)s
# Uncomment the line below if you want the files to be prepended with date and time
# file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
# defaults to the current working directory.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
# as well as the filename.
# If specified, requires the python-dateutil library that can be
# installed by adding `alembic[tz]` to the pip requirements
# string value is passed to dateutil.tz.gettz()
# leave blank for localtime
# timezone =

# max length of characters to apply to the
# "slug" field
# truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version number format (uses % string formatting)
version_num_format = %04d

# version path separator; As mentioned above, this is the character used to split
# version_path_specification into a list
# version_path_separator = :

# set to 'true' to search source files recursively
# in each "version_locations" directory
# recursive_version_locations = false

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

sqlalchemy.url = sqlite:///./supermarket.db


[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts.  See the documentation for further
# detail and examples

# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks = black
# black.type = console_scripts
# black.entrypoint = black
# black.options = -l 79 REVISION_SCRIPT_FILENAME

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
EOF

# Inicializar migrações do Alembic
log_info "Inicializando migrações do banco de dados..."
if [[ ! -d "migrations" ]]; then
    alembic init migrations

    # Configurar env.py do Alembic
    cat > migrations/env.py << 'EOF'
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.infrastructure.database.models import Base
from app.core.config import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Set the sqlalchemy.url from our settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
EOF

    log_success "Migrações inicializadas!"
else
    log_info "Migrações já inicializadas"
fi

# Criar primeira migração
log_info "Criando migração inicial..."
alembic revision --autogenerate -m "Initial migration"

# Aplicar migrações
log_info "Aplicando migrações..."
alembic upgrade head

log_success "Banco de dados configurado!"

# 3. CONFIGURAR GIT E VERSIONAMENTO
echo ""
log_info "3. CONFIGURANDO GIT E VERSIONAMENTO"
echo "==================================="

# Verificar se Git está instalado
if ! command -v git &> /dev/null; then
    log_error "Git não encontrado. Instale o Git primeiro."
    exit 1
fi

# Inicializar repositório se não existir
if [[ ! -d ".git" ]]; then
    log_info "Inicializando repositório Git..."
    git init
    log_success "Repositório Git inicializado!"
else
    log_info "Repositório Git já existe"
fi

# Configurar hooks do pre-commit
log_info "Configurando hooks de qualidade de código..."
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: debug-statements
EOF

# Instalar hooks
pre-commit install
log_success "Hooks de qualidade instalados!"

# Configurações Git adicionais
cat > .gitattributes << 'EOF'
# Handle line endings automatically for files detected as text
# and leave all files detected as binary untouched.
* text=auto

# Force the following filetypes to have unix eols, so Windows does not break them
*.* text eol=lf

# Windows forced line-endings
*.bat text eol=crlf

# Binary files
*.png binary
*.jpg binary
*.jpeg binary
*.gif binary
*.ico binary
*.pdf binary
*.zip binary
*.tar.gz binary
*.db binary
*.sqlite binary
*.sqlite3 binary
EOF

# Template de commit
cat > .gitmessage << 'EOF'
# <tipo>(<escopo>): <descrição>
#
# <corpo da mensagem>
#
# <rodapé>
#
# Tipos:
# feat: nova funcionalidade
# fix: correção de bug
# docs: documentação
# style: formatação
# refactor: refatoração
# test: testes
# chore: tarefas de manutenção
#
# Exemplos:
# feat(auth): adiciona sistema de login
# fix(pdv): corrige cálculo de desconto
# docs(api): atualiza documentação da API
EOF

# Configurar template de commit
git config commit.template .gitmessage

# Adicionar arquivos ao Git
log_info "Adicionando arquivos ao controle de versão..."
git add .
git commit -m "feat: configuração inicial do projeto

- Estrutura completa do projeto
- Configuração do ambiente Python
- Setup do banco de dados com SQLAlchemy
- Modelos de dados completos
- Configuração do Alembic para migrações
- Hooks de qualidade de código
- Configuração Git"

log_success "Projeto adicionado ao Git!"

# Criar arquivo de status
cat > PROJECT_STATUS.md << 'EOF'
# Status do Projeto - Sistema de Supermercado

## ✅ Concluído

### Ambiente e Estrutura
- [x] Estrutura completa do projeto
- [x] Ambiente virtual Python configurado
- [x] Dependências instaladas
- [x] Configuração Git e versionamento
- [x] Hooks de qualidade de código

### Banco de Dados
- [x] Configuração SQLAlchemy
- [x] Modelos de dados completos
- [x] Sistema de migrações (Alembic)
- [x] Banco SQLite configurado

### Modelos Implementados
- [x] User (usuários/funcionários)
- [x] Product (produtos)
- [x] Category (categorias)
- [x] Sale (vendas)
- [x] SaleItem (itens de venda)
- [x] Customer (clientes)
- [x] Supplier (fornecedores)

## 🚧 Próximos Passos

1. **Sistema de Autenticação**
   - [ ] Endpoints de login/logout
   - [ ] Geração e validação JWT
   - [ ] Middleware de autorização

2. **API REST**
   - [ ] Configuração FastAPI
   - [ ] CRUD de produtos
   - [ ] CRUD de categorias
   - [ ] Endpoints de vendas

3. **Integração Hardware**
   - [ ] Leitor código de barras
   - [ ] Balança eletrônica
   - [ ] Impressora térmica

4. **Sistema de Promoções**
   - [ ] Motor de cálculo de descontos
   - [ ] Regras de negócio
   - [ ] Interface de configuração

5. **Interface do Usuário**
   - [ ] PDV (Ponto de Venda)
   - [ ] Dashboard administrativo
   - [ ] Relatórios gerenciais

## 📊 Progresso Geral: 25%

- Fundação: ✅ 100%
- Backend: 🚧 15%
- Frontend: ⏳ 0%
- Hardware: ⏳ 0%
- Testes: ⏳ 0%
EOF

echo ""
log_success "🎉 SETUP COMPLETO!"
echo "=================="
echo ""
echo "📁 Estrutura criada:"
echo "   ✅ Ambiente Python configurado"
echo "   ✅ Banco de dados SQLite criado"
echo "   ✅ Modelos de dados implementados"
echo "   ✅ Sistema de migrações configurado"
echo "   ✅ Git e controle de versão"
echo "   ✅ Hooks de qualidade de código"
echo ""
echo "🚀 Para continuar o desenvolvimento:"
echo "   make run          # Iniciar API (quando implementada)"
echo "   make test         # Executar testes"
echo "   make format       # Formatar código"
echo "   git status        # Ver status do Git"
echo ""
echo "📋 Próximo passo: Implementar sistema de autenticação"
echo "📖 Ver PROJECT_STATUS.md para roadmap completo"
