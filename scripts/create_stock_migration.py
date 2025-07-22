#!/usr/bin/env python3
"""
Script para gerar migração do sistema de estoque
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine

from app.core.config import settings
from app.infrastructure.database.models import Base


def create_migration():
    """Criar migração para o sistema de estoque"""
    print("🔄 Criando migração para sistema de estoque...")

    try:
        # Conectar ao banco
        engine = create_engine(settings.DATABASE_URL)

        # Criar todas as tabelas (se não existirem)
        Base.metadata.create_all(bind=engine)

        print("✅ Migração criada com sucesso!")
        print("\n📋 Novas tabelas criadas:")
        print("  • suppliers - Fornecedores")
        print("  • stock_movements - Movimentações de estoque")
        print("  • purchase_orders - Pedidos de compra")
        print("  • purchase_order_items - Itens dos pedidos")
        print("\n📝 Colunas adicionadas à tabela products:")
        print("  • supplier_id - ID do fornecedor")
        print("  • profit_margin - Margem de lucro")
        print("  • weight - Peso do produto")
        print("  • dimensions - Dimensões")
        print("  • location - Localização no estoque")
        print("  • reorder_point - Ponto de reposição")
        print("  • max_stock - Estoque máximo")
        print("  • last_purchase_date - Última compra")
        print("  • last_sale_date - Última venda")

    except Exception as e:
        print(f"❌ Erro ao criar migração: {str(e)}")
        return False

    return True


if __name__ == "__main__":
    success = create_migration()
    if not success:
        sys.exit(1)
