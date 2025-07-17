#!/usr/bin/env python3

from sqlalchemy import text

from app.infrastructure.database.connection import get_db


def check_database():
    print("=== Verificando dados no banco ===")

    db = next(get_db())

    try:
        # Contar vendas
        sales_count = db.execute(text("SELECT COUNT(*) FROM sales")).scalar()
        print(f"Total de vendas: {sales_count}")

        # Contar vendas completed
        completed_sales = db.execute(
            text("SELECT COUNT(*) FROM sales WHERE status = 'completed'")
        ).scalar()
        print(f"Vendas completed: {completed_sales}")

        # Contar produtos
        products_count = db.execute(text("SELECT COUNT(*) FROM products")).scalar()
        print(f"Total de produtos: {products_count}")

        # Listar algumas vendas
        print("\n=== Primeiras 5 vendas ===")
        sales_result = db.execute(
            text("SELECT id, total, status, created_at FROM sales LIMIT 5")
        )
        for row in sales_result:
            print(f"ID: {row[0]}, Total: {row[1]}, Status: {row[2]}, Data: {row[3]}")

        # Verificar status disponíveis
        print("\n=== Status de vendas únicos ===")
        status_result = db.execute(text("SELECT DISTINCT status FROM sales"))
        for row in status_result:
            print(f"Status: {row[0]}")

    except Exception as e:
        print(f"Erro: {e}")
        import traceback

        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    check_database()
