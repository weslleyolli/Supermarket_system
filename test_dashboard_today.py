#!/usr/bin/env python3
"""
Script para testar vendas de hoje no dashboard
Execute no WSL: python3 test_dashboard_today.py
"""

import os
import sys
from datetime import datetime

# Adicionar o diretório atual ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


def test_dashboard_today():
    try:
        print("🧪 TESTE: Dashboard vendas de hoje...")

        from sqlalchemy import text

        from app.infrastructure.database.connection import SessionLocal

        db = SessionLocal()

        print(f"📅 Data atual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Teste 1: Vendas de hoje
        print("\n📊 Testando vendas de hoje...")
        today_sales_result = db.execute(
            text(
                "SELECT COUNT(*) FROM sales WHERE status = 'COMPLETED' AND DATE(created_at) = CURRENT_DATE"
            )
        )
        today_sales = today_sales_result.scalar() or 0
        print(f"✅ Vendas de hoje: {today_sales}")

        # Teste 2: Receita de hoje
        today_revenue_result = db.execute(
            text(
                "SELECT COALESCE(SUM(final_amount), 0) FROM sales WHERE status = 'COMPLETED' AND DATE(created_at) = CURRENT_DATE"
            )
        )
        today_revenue = float(today_revenue_result.scalar() or 0.0)
        print(f"✅ Receita de hoje: R$ {today_revenue:.2f}")

        # Teste 3: Detalhes das vendas de hoje
        if today_sales > 0:
            print("\n📋 Detalhes das vendas de hoje:")
            sales_details = db.execute(
                text(
                    """
                    SELECT id, final_amount, created_at, customer_id
                    FROM sales
                    WHERE status = 'COMPLETED' AND DATE(created_at) = CURRENT_DATE
                    ORDER BY created_at DESC
                """
                )
            )
            for row in sales_details:
                time_str = row[2].strftime("%H:%M:%S") if row[2] else "N/A"
                customer = f"Cliente {row[3]}" if row[3] else "Sem cliente"
                print(
                    f"  🛒 Venda #{row[0]} - R$ {row[1]:.2f} - {time_str} - {customer}"
                )
        else:
            print("⚠️  Nenhuma venda registrada hoje")

            # Verificar se há vendas em outros dias
            all_sales = db.execute(
                text("SELECT COUNT(*) FROM sales WHERE status = 'COMPLETED'")
            )
            total_all_sales = all_sales.scalar() or 0
            print(f"📈 Total de vendas de todos os tempos: {total_all_sales}")

            if total_all_sales > 0:
                print("💡 Há vendas em outros dias. Vamos ver as mais recentes:")
                recent_sales = db.execute(
                    text(
                        """
                        SELECT id, final_amount, created_at, DATE(created_at) as sale_date
                        FROM sales
                        WHERE status = 'COMPLETED'
                        ORDER BY created_at DESC
                        LIMIT 3
                    """
                    )
                )
                for row in recent_sales:
                    date_str = row[3].strftime("%Y-%m-%d") if row[3] else "N/A"
                    time_str = row[2].strftime("%H:%M:%S") if row[2] else "N/A"
                    print(
                        f"  📅 Venda #{row[0]} - R$ {row[1]:.2f} - {date_str} {time_str}"
                    )

        # Teste 4: Ticket médio
        if today_sales > 0:
            avg_ticket = today_revenue / today_sales
            print(f"\n💰 Ticket médio de hoje: R$ {avg_ticket:.2f}")

        # Teste 5: Alertas de estoque (relacionado à sua compra de Coca-Cola)
        print("\n🔔 Alertas de estoque:")
        alerts_result = db.execute(
            text(
                "SELECT name, stock_quantity FROM products WHERE stock_quantity < 10 ORDER BY stock_quantity ASC"
            )
        )
        alerts_count = 0
        for row in alerts_result:
            alerts_count += 1
            print(f"  ⚠️  {row[0]}: {row[1]} unidades restantes")

        if alerts_count == 0:
            print("  ✅ Nenhum produto com estoque baixo")
        else:
            print(f"  📊 Total de alertas: {alerts_count}")

        db.close()

        print("\n" + "=" * 50)
        print("📈 RESUMO DO TESTE:")
        print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d')}")
        print(f"🛒 Vendas hoje: {today_sales}")
        print(f"💰 Receita hoje: R$ {today_revenue:.2f}")
        print(f"🔔 Alertas: {alerts_count}")
        print("=" * 50)

        return True

    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_dashboard_today()
    print(f"\n🏆 TESTE: {'PASSOU' if success else 'FALHOU'}")
    sys.exit(0 if success else 1)
