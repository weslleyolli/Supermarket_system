#!/usr/bin/env python3
"""
Script para verificar a estrutura da tabela suppliers
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text

from app.core.config import settings


def check_suppliers_table():
    """Verificar estrutura da tabela suppliers"""
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            # Verificar se a tabela existe
            result = conn.execute(
                text(
                    """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'suppliers'
                );
            """
                )
            )
            table_exists = result.fetchone()[0]
            print(f"Tabela 'suppliers' existe: {table_exists}")

            if table_exists:
                # Listar colunas
                result = conn.execute(
                    text(
                        """
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = 'suppliers'
                    ORDER BY ordinal_position;
                """
                    )
                )

                print("\nColunas da tabela 'suppliers':")
                for row in result:
                    print(
                        f"  - {row[0]} ({row[1]}) {'NULL' if row[2] == 'YES' else 'NOT NULL'}"
                    )

            # Verificar outras tabelas de estoque
            tables = ["stock_movements", "purchase_orders", "purchase_order_items"]
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
                print(f"Tabela '{table}' existe: {exists}")

    except Exception as e:
        print(f"Erro: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    check_suppliers_table()
