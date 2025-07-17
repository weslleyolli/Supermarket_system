"""
Script para testar especificamente o endpoint de dashboard
"""
import os
import sys

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text

from app.core.config import settings


def test_dashboard_queries():
    """Testar as queries específicas do dashboard"""
    print("🔍 TESTANDO QUERIES DO DASHBOARD...")

    database_url = settings.DATABASE_URL
    engine = create_engine(database_url)

    with engine.connect() as conn:
        print("\n1️⃣ Testando contagem de vendas COMPLETED:")
        result = conn.execute(
            text("SELECT COUNT(*) FROM sales WHERE status = 'COMPLETED'")
        )
        count = result.scalar()
        print(f"   Resultado: {count}")

        print("\n2️⃣ Testando soma da receita:")
        result = conn.execute(
            text(
                "SELECT COALESCE(SUM(final_amount), 0) FROM sales WHERE status = 'COMPLETED'"
            )
        )
        revenue = result.scalar()
        print(f"   Resultado: R$ {revenue}")

        print("\n3️⃣ Testando contagem de produtos:")
        result = conn.execute(text("SELECT COUNT(*) FROM products"))
        products = result.scalar()
        print(f"   Resultado: {products}")

        print("\n4️⃣ Testando produtos com estoque baixo:")
        result = conn.execute(
            text("SELECT COUNT(*) FROM products WHERE stock_quantity < 10")
        )
        low_stock = result.scalar()
        print(f"   Resultado: {low_stock}")

        print("\n5️⃣ Testando vendas recentes:")
        result = conn.execute(
            text(
                """
            SELECT id, final_amount, created_at
            FROM sales
            WHERE status = 'COMPLETED'
            ORDER BY created_at DESC
            LIMIT 5
        """
            )
        )

        sales = []
        for row in result:
            sales.append(
                {"id": row[0], "total": float(row[1]), "created_at": str(row[2])}
            )

        print(f"   Resultado: {len(sales)} vendas encontradas")
        for sale in sales:
            print(f"     - Venda {sale['id']}: R$ {sale['total']}")


if __name__ == "__main__":
    test_dashboard_queries()
