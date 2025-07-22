#!/usr/bin/env python3
"""
Script para verificar a estrutura atual do banco de dados
"""

import os
import sys

from sqlalchemy import create_engine, text

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.connection import get_database_url


def check_database_structure():
    """Verificar a estrutura atual do banco de dados"""

    print("🔍 VERIFICANDO ESTRUTURA DO BANCO DE DADOS...")

    database_url = get_database_url()
    engine = create_engine(database_url)

    queries = [
        (
            "Tabelas existentes",
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """,
        ),
        (
            "Colunas da tabela products",
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'products'
            ORDER BY ordinal_position;
        """,
        ),
        (
            "Colunas da tabela suppliers",
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'suppliers'
            ORDER BY ordinal_position;
        """,
        ),
        ("Contagem de produtos", "SELECT COUNT(*) FROM products;"),
        ("Contagem de fornecedores", "SELECT COUNT(*) FROM suppliers;"),
    ]

    with engine.connect() as conn:
        for name, query in queries:
            try:
                print(f"\n📋 {name}:")
                result = conn.execute(text(query))

                if "SELECT COUNT" in query:
                    count = result.scalar()
                    print(f"   Total: {count}")
                else:
                    rows = result.fetchall()
                    for row in rows:
                        print(f"   {row}")

            except Exception as e:
                print(f"❌ Erro ao executar {name}: {e}")


def main():
    """Função principal"""
    print("🔍 DIAGNÓSTICO DO BANCO DE DADOS")
    print("=" * 50)

    try:
        check_database_structure()
        print("\n✅ DIAGNÓSTICO CONCLUÍDO!")

    except Exception as e:
        print(f"\n❌ ERRO NO DIAGNÓSTICO: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
