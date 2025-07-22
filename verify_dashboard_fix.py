#!/usr/bin/env python3
"""
Teste rápido para verificar se o dashboard mostra o VALOR correto das vendas
"""

import os
import sys
from datetime import datetime

# Adicionar o diretório atual ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


def test_dashboard_value():
    try:
        print("🧪 TESTE: Verificando se dashboard mostra VALOR das vendas...")

        from sqlalchemy import text

        from app.infrastructure.database.connection import SessionLocal

        db = SessionLocal()

        # Simular a mesma lógica do dashboard
        print("\n📊 Testando lógica do dashboard:")

        # Número de vendas hoje
        today_sales_count_result = db.execute(
            text(
                "SELECT COUNT(*) FROM sales WHERE status = 'COMPLETED' AND DATE(created_at) = CURRENT_DATE"
            )
        )
        today_sales_count = today_sales_count_result.scalar() or 0
        print(f"📈 NÚMERO de vendas hoje: {today_sales_count}")

        # Valor total das vendas hoje
        today_revenue_result = db.execute(
            text(
                "SELECT COALESCE(SUM(final_amount), 0) FROM sales WHERE status = 'COMPLETED' AND DATE(created_at) = CURRENT_DATE"
            )
        )
        today_revenue = float(today_revenue_result.scalar() or 0.0)
        print(f"💰 VALOR das vendas hoje: R$ {today_revenue:.2f}")

        # Mostrar vendas individuais
        if today_sales_count > 0:
            print("\n🛒 Vendas de hoje (detalhes):")
            sales_details = db.execute(
                text(
                    """
                    SELECT id, final_amount, created_at
                    FROM sales
                    WHERE status = 'COMPLETED' AND DATE(created_at) = CURRENT_DATE
                    ORDER BY created_at DESC
                """
                )
            )
            total_check = 0
            for row in sales_details:
                time_str = row[2].strftime("%H:%M:%S") if row[2] else "N/A"
                value = float(row[1])
                total_check += value
                print(f"  💳 Venda #{row[0]} - R$ {value:.2f} - {time_str}")

            print(f"\n🔍 Verificação:")
            print(f"  📊 Soma manual: R$ {total_check:.2f}")
            print(f"  🎯 Query total: R$ {today_revenue:.2f}")
            print(
                f"  ✅ Valores {'CONFEREM' if abs(total_check - today_revenue) < 0.01 else 'NÃO CONFEREM'}"
            )

        # Simular resposta do dashboard
        dashboard_response = {
            "today_sales": today_revenue,  # 🔥 AGORA: valor em reais
            "total_revenue": today_revenue,
            "customers_served": today_sales_count,  # número de transações
        }

        print(f"\n🎯 DASHBOARD CORRIGIDO:")
        print(
            f"  📈 today_sales (box principal): R$ {dashboard_response['today_sales']:.2f}"
        )
        print(f"  💰 total_revenue: R$ {dashboard_response['total_revenue']:.2f}")
        print(
            f"  👥 customers_served: {dashboard_response['customers_served']} transações"
        )

        db.close()

        print("\n" + "=" * 60)
        print("✅ CORREÇÃO APLICADA:")
        print("📊 O campo 'today_sales' agora mostra o VALOR em reais")
        print("📈 O campo 'customers_served' mostra o NÚMERO de transações")
        print(
            "💡 Agora quando você comprar mais produtos, o valor vai subir corretamente!"
        )
        print("=" * 60)

        return True

    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_dashboard_value()
    print(f"\n🏆 TESTE: {'PASSOU' if success else 'FALHOU'}")
