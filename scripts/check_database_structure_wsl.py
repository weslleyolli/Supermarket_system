#!/usr/bin/env python3
"""
Script para verificar a estrutura do banco de dados no WSL/Linux
Execute com: python3 check_database_structure_wsl.py
"""

import os
import sys

import sqlalchemy as sa
from sqlalchemy import create_engine, inspect


def main():
    try:
        # Adicionar o diretório atual ao path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)

        # Importar configurações
        from app.core.config import settings

        print("=== VERIFICAÇÃO DA ESTRUTURA DO BANCO DE DADOS ===\n")

        # Conectar ao banco
        engine = create_engine(settings.DATABASE_URL)
        inspector = inspect(engine)

        print("📋 TABELAS NO BANCO DE DADOS:")
        tables = inspector.get_table_names()
        for i, table in enumerate(tables, 1):
            print(f"  {i}. {table}")

        print(f"\n✅ Total de tabelas: {len(tables)}\n")

        # Verificar tabela products
        if "products" in tables:
            print("🔍 ESTRUTURA DA TABELA 'products':")
            columns = inspector.get_columns("products")
            for col in columns:
                nullable = "NULL" if col.get("nullable", True) else "NOT NULL"
                print(f"  📄 {col['name']}: {col['type']} ({nullable})")

            print("\n🔗 FOREIGN KEYS NA TABELA 'products':")
            fks = inspector.get_foreign_keys("products")
            if fks:
                for fk in fks:
                    constrained = ", ".join(fk["constrained_columns"])
                    referred = (
                        f"{fk['referred_table']}.{', '.join(fk['referred_columns'])}"
                    )
                    print(f"  🔗 {constrained} -> {referred}")
            else:
                print("  ❌ Nenhuma foreign key encontrada")
        else:
            print("❌ Tabela 'products' não encontrada!")

        # Verificar tabela suppliers
        if "suppliers" in tables:
            print("\n🔍 ESTRUTURA DA TABELA 'suppliers':")
            columns = inspector.get_columns("suppliers")
            for col in columns:
                nullable = "NULL" if col.get("nullable", True) else "NOT NULL"
                print(f"  📄 {col['name']}: {col['type']} ({nullable})")
        else:
            print("\n❌ Tabela 'suppliers' não encontrada!")

        # Verificar se supplier_id existe em products
        if "products" in tables:
            print("\n🔍 VERIFICANDO COLUNA 'supplier_id' EM 'products':")
            columns = inspector.get_columns("products")
            supplier_col = next(
                (col for col in columns if col["name"] == "supplier_id"), None
            )

            if supplier_col:
                print(f"  ✅ Coluna 'supplier_id' encontrada: {supplier_col['type']}")
            else:
                print("  ❌ Coluna 'supplier_id' NÃO encontrada na tabela products")
                print("  💡 Isso explica o erro de Foreign Key!")

        # Verificar dados
        print("\n📊 CONTAGEM DE DADOS:")
        with engine.connect() as conn:
            for table in ["products", "suppliers", "sales", "categories", "users"]:
                if table in tables:
                    result = conn.execute(sa.text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"  📈 {table}: {count} registros")

        print("\n🎯 DIAGNÓSTICO:")
        if "products" in tables and "suppliers" in tables:
            # Verificar se supplier_id existe
            columns = inspector.get_columns("products")
            has_supplier_id = any(col["name"] == "supplier_id" for col in columns)

            if has_supplier_id:
                print("  ✅ Estrutura do banco parece correta")
            else:
                print("  ❌ PROBLEMA IDENTIFICADO:")
                print(
                    "     - Tabela 'products' existe mas não tem coluna 'supplier_id'"
                )
                print(
                    "     - Modelo Product.py tem supplier_id mas migração não criou a coluna"
                )
                print("     - Precisa criar nova migração para adicionar a coluna")
                print("\n💡 SOLUÇÃO:")
                print(
                    "     1. Criar nova migração: alembic revision --autogenerate -m 'add_supplier_id_to_products'"
                )
                print("     2. Aplicar migração: alembic upgrade head")
        else:
            print("  ❌ Tabelas essenciais não encontradas")

    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
