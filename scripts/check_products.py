#!/usr/bin/env python3
"""
Verificar quantos produtos existem no banco de dados
"""

import os
import sys

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text

from app.core.config import settings


def check_products():
    """Verificar produtos no banco"""

    # Tentar diferentes URLs de banco
    database_urls = [
        settings.DATABASE_URL,
        "postgresql://postgres:password@localhost:5432/supermarket_system",
        "postgresql://user:password@localhost:5432/supermarket_system",
    ]

    engine = None
    for db_url in database_urls:
        try:
            print(f"🔄 Tentando conectar com: {db_url}")
            engine = create_engine(db_url)
            # Testar conexão
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print(f"✅ Conectado com sucesso!")
            break
        except Exception as e:
            print(f"❌ Falha: {e}")
            continue

    if not engine:
        print("❌ Não foi possível conectar a nenhum banco de dados")
        return

    with engine.connect() as conn:
        print("🔍 VERIFICANDO PRODUTOS NO BANCO DE DADOS...\n")

        # Total de produtos
        result = conn.execute(text("SELECT COUNT(*) FROM products"))
        total_products = result.scalar()
        print(f"📊 Total de produtos na tabela 'products': {total_products}")

        # Produtos ativos
        result = conn.execute(
            text("SELECT COUNT(*) FROM products WHERE is_active = true")
        )
        active_products = result.scalar()
        print(f"✅ Produtos ativos: {active_products}")

        # Produtos inativos
        result = conn.execute(
            text("SELECT COUNT(*) FROM products WHERE is_active = false")
        )
        inactive_products = result.scalar()
        print(f"❌ Produtos inativos: {inactive_products}")

        print("\n" + "=" * 50)

        # Listar os produtos que existem
        if total_products > 0:
            print("📋 LISTA DOS PRODUTOS:")
            result = conn.execute(
                text(
                    """
                SELECT id, name, price, stock_quantity, is_active
                FROM products
                ORDER BY id
            """
                )
            )

            for row in result:
                status = "✅ Ativo" if row[4] else "❌ Inativo"
                print(
                    f"  ID: {row[0]} | Nome: {row[1]} | Preço: R${row[2]} | Estoque: {row[3]} | {status}"
                )
        else:
            print("⚠️  Nenhum produto encontrado na tabela!")

        print("\n" + "=" * 50)

        # Verificar se a tabela existe
        result = conn.execute(
            text(
                """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = 'products'
        """
            )
        )
        table_exists = result.fetchone()

        if table_exists:
            print("✅ Tabela 'products' existe no banco")
        else:
            print("❌ Tabela 'products' NÃO existe no banco")

        # Verificar estrutura da tabela
        print("\n🏗️  ESTRUTURA DA TABELA 'products':")
        result = conn.execute(
            text(
                """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'products'
            ORDER BY ordinal_position
        """
            )
        )

        for row in result:
            nullable = "NULL" if row[2] == "YES" else "NOT NULL"
            print(f"  {row[0]} | {row[1]} | {nullable}")


if __name__ == "__main__":
    try:
        check_products()
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback

        traceback.print_exc()
