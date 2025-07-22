#!/usr/bin/env python3
"""
Script de emergência para investigar o que aconteceu com as vendas
"""

import os
import sys

# Adicionar o diretório atual ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


def investigate_sales_issue():
    try:
        from sqlalchemy import text

        from app.infrastructure.database.connection import SessionLocal

        db = SessionLocal()

        print("🔍 INVESTIGAÇÃO DE EMERGÊNCIA - O QUE ACONTECEU?")

        # 1. Verificar quantas vendas existem REALMENTE
        print("\n📊 1. CONTAGEM REAL DE VENDAS:")

        total_sales = db.execute(text("SELECT COUNT(*) FROM sales"))
        total_count = total_sales.scalar() or 0
        print(f"🛒 Total de vendas na tabela: {total_count}")

        completed_sales = db.execute(
            text("SELECT COUNT(*) FROM sales WHERE status = 'COMPLETED'")
        )
        completed_count = completed_sales.scalar() or 0
        print(f"✅ Vendas completadas: {completed_count}")

        # 2. Verificar vendas de hoje
        print("\n📅 2. VENDAS DE HOJE:")

        today_count = db.execute(
            text("SELECT COUNT(*) FROM sales WHERE DATE(created_at) = CURRENT_DATE")
        )
        today_total = today_count.scalar() or 0
        print(f"📈 Vendas criadas hoje: {today_total}")

        today_completed = db.execute(
            text(
                "SELECT COUNT(*) FROM sales WHERE status = 'COMPLETED' AND DATE(created_at) = CURRENT_DATE"
            )
        )
        today_completed_count = today_completed.scalar() or 0
        print(f"✅ Vendas completadas hoje: {today_completed_count}")

        # 3. Valor total das vendas de hoje
        print("\n💰 3. VALORES DE HOJE:")

        today_revenue = db.execute(
            text(
                "SELECT COALESCE(SUM(final_amount), 0) FROM sales WHERE status = 'COMPLETED' AND DATE(created_at) = CURRENT_DATE"
            )
        )
        revenue_value = float(today_revenue.scalar() or 0)
        print(f"💵 Receita de hoje (COMPLETED): R$ {revenue_value:.2f}")

        all_today_revenue = db.execute(
            text(
                "SELECT COALESCE(SUM(final_amount), 0) FROM sales WHERE DATE(created_at) = CURRENT_DATE"
            )
        )
        all_revenue = float(all_today_revenue.scalar() or 0)
        print(f"💸 Receita de hoje (TODAS): R$ {all_revenue:.2f}")

        # 4. Verificar se existem vendas em status diferentes
        print("\n📋 4. STATUS DAS VENDAS DE HOJE:")

        status_check = db.execute(
            text(
                """
            SELECT status, COUNT(*), COALESCE(SUM(final_amount), 0)
            FROM sales
            WHERE DATE(created_at) = CURRENT_DATE
            GROUP BY status
        """
            )
        )

        for row in status_check:
            status = row[0] or "NULL"
            count = row[1] or 0
            amount = float(row[2] or 0)
            print(f'📊 Status "{status}": {count} vendas - R$ {amount:.2f}')

        # 5. Mostrar as últimas vendas criadas
        print("\n🕒 5. ÚLTIMAS VENDAS CRIADAS:")

        recent_sales = db.execute(
            text(
                """
            SELECT id, status, final_amount, created_at
            FROM sales
            ORDER BY created_at DESC
            LIMIT 10
        """
            )
        )

        for row in recent_sales:
            sale_id = row[0]
            status = row[1] or "NULL"
            amount = float(row[2] or 0)
            created = row[3].strftime("%Y-%m-%d %H:%M:%S") if row[3] else "N/A"
            print(f"🛒 Venda #{sale_id} - {status} - R$ {amount:.2f} - {created}")

        # 6. Verificar se há problemas de timezone
        print("\n🌍 6. VERIFICAÇÃO DE TIMEZONE:")

        current_date = db.execute(text("SELECT CURRENT_DATE, NOW()"))
        date_info = current_date.fetchone()
        print(f"📅 CURRENT_DATE no banco: {date_info[0]}")
        print(f"🕒 NOW() no banco: {date_info[1]}")

        db.close()

        print("\n" + "=" * 60)
        print("🎯 RESUMO DA INVESTIGAÇÃO:")
        print(f"📊 Frontend mostra: R$ 12.266,63 com 83 transações")
        print(f"🔧 API retorna: R$ 0,00 com 0 transações")
        print(
            f"💾 Banco tem: {today_completed_count} vendas completadas hoje = R$ {revenue_value:.2f}"
        )
        print("=" * 60)

        # Sugestão de correção
        if revenue_value > 0 and today_completed_count > 0:
            print(
                "💡 PROBLEMA IDENTIFICADO: API funcionando, mas frontend com cache antigo"
            )
            print("🔄 SOLUÇÃO: Recarregue a página do frontend (F5 ou Ctrl+F5)")
        elif today_total > today_completed_count:
            print("💡 PROBLEMA IDENTIFICADO: Há vendas não completadas")
            print("🔄 SOLUÇÃO: Verificar status das vendas")
        else:
            print("💡 PROBLEMA IDENTIFICADO: Inconsistência de dados")
            print("🔄 SOLUÇÃO: Verificar sincronização frontend-backend")

        return True

    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    investigate_sales_issue()
