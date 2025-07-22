#!/usr/bin/env python3
"""
Script para corrigir a estrutura das tabelas de estoque
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text

from app.core.config import settings


def fix_stock_tables():
    """Corrigir e criar tabelas de estoque"""
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            print("🔄 Corrigindo estrutura das tabelas de estoque...")

            # 1. Corrigir tabela suppliers
            print("📝 Atualizando tabela suppliers...")

            # Adicionar colunas que estão faltando
            try:
                conn.execute(
                    text(
                        "ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS company_name VARCHAR(255)"
                    )
                )
                print("  ✅ Coluna company_name adicionada")
            except Exception as e:
                print(f"  ⚠️  company_name: {e}")

            try:
                conn.execute(
                    text(
                        "ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS document VARCHAR(20)"
                    )
                )
                print("  ✅ Coluna document adicionada")
            except Exception as e:
                print(f"  ⚠️  document: {e}")

            try:
                conn.execute(
                    text(
                        "ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true"
                    )
                )
                print("  ✅ Coluna is_active adicionada")
            except Exception as e:
                print(f"  ⚠️  is_active: {e}")

            # Migrar dados de cnpj para document se necessário
            try:
                result = conn.execute(
                    text(
                        "SELECT COUNT(*) FROM suppliers WHERE cnpj IS NOT NULL AND document IS NULL"
                    )
                )
                count = result.fetchone()[0]
                if count > 0:
                    conn.execute(
                        text(
                            "UPDATE suppliers SET document = cnpj WHERE cnpj IS NOT NULL AND document IS NULL"
                        )
                    )
                    print(f"  ✅ Migrados {count} registros de cnpj para document")
            except Exception as e:
                print(f"  ⚠️  Migração cnpj->document: {e}")

            # 2. Criar tabela stock_movements
            print("📝 Criando tabela stock_movements...")
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS stock_movements (
                    id SERIAL PRIMARY KEY,
                    product_id INTEGER NOT NULL REFERENCES products(id),
                    movement_type VARCHAR(20) NOT NULL,
                    quantity INTEGER NOT NULL,
                    previous_quantity INTEGER NOT NULL,
                    new_quantity INTEGER NOT NULL,
                    unit_cost NUMERIC(10, 2),
                    total_cost NUMERIC(10, 2),
                    reason VARCHAR(255),
                    notes TEXT,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    sale_id INTEGER REFERENCES sales(id),
                    supplier_id INTEGER REFERENCES suppliers(id),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """
                )
            )
            print("  ✅ Tabela stock_movements criada")

            # 3. Criar tabela purchase_orders
            print("📝 Criando tabela purchase_orders...")
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS purchase_orders (
                    id SERIAL PRIMARY KEY,
                    supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
                    order_number VARCHAR(50) UNIQUE NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    total_amount NUMERIC(10, 2) NOT NULL DEFAULT 0,
                    notes TEXT,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    order_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    expected_delivery TIMESTAMP WITH TIME ZONE,
                    delivery_date TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """
                )
            )
            print("  ✅ Tabela purchase_orders criada")

            # 4. Criar tabela purchase_order_items
            print("📝 Criando tabela purchase_order_items...")
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS purchase_order_items (
                    id SERIAL PRIMARY KEY,
                    purchase_order_id INTEGER NOT NULL REFERENCES purchase_orders(id),
                    product_id INTEGER NOT NULL REFERENCES products(id),
                    quantity_ordered INTEGER NOT NULL,
                    quantity_received INTEGER DEFAULT 0,
                    unit_cost NUMERIC(10, 2) NOT NULL,
                    total_cost NUMERIC(10, 2) NOT NULL
                )
            """
                )
            )
            print("  ✅ Tabela purchase_order_items criada")

            # 5. Verificar se as colunas de estoque existem na tabela products
            print("📝 Verificando colunas de estoque na tabela products...")

            # Verificar se as colunas existem
            result = conn.execute(
                text(
                    """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'products' AND column_name IN (
                    'supplier_id', 'profit_margin', 'weight', 'dimensions',
                    'location', 'reorder_point', 'max_stock', 'last_purchase_date', 'last_sale_date'
                )
            """
                )
            )
            existing_columns = [row[0] for row in result]

            # Adicionar colunas que estão faltando
            new_columns = [
                ("supplier_id", "INTEGER REFERENCES suppliers(id)"),
                ("profit_margin", "REAL"),
                ("weight", "REAL"),
                ("dimensions", "VARCHAR(100)"),
                ("location", "VARCHAR(100)"),
                ("reorder_point", "INTEGER"),
                ("max_stock", "INTEGER"),
                ("last_purchase_date", "TIMESTAMP WITH TIME ZONE"),
                ("last_sale_date", "TIMESTAMP WITH TIME ZONE"),
            ]

            for col_name, col_type in new_columns:
                if col_name not in existing_columns:
                    try:
                        conn.execute(
                            text(
                                f"ALTER TABLE products ADD COLUMN {col_name} {col_type}"
                            )
                        )
                        print(f"  ✅ Coluna {col_name} adicionada à tabela products")
                    except Exception as e:
                        print(f"  ⚠️  {col_name}: {e}")
                else:
                    print(f"  ✅ Coluna {col_name} já existe na tabela products")

            # Confirmar as mudanças
            conn.commit()

            print("\n🎉 Estrutura das tabelas de estoque corrigida com sucesso!")

            # Verificar estrutura final
            print("\n📋 Verificação final:")
            tables = [
                "suppliers",
                "stock_movements",
                "purchase_orders",
                "purchase_order_items",
            ]
            for table in tables:
                result = conn.execute(
                    text(
                        f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = '{table}'
                    );
                """
                    )
                )
                exists = result.fetchone()[0]
                print(f"  • {table}: {'✅ OK' if exists else '❌ ERRO'}")

    except Exception as e:
        print(f"❌ Erro ao corrigir tabelas: {str(e)}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = fix_stock_tables()
    if not success:
        sys.exit(1)
