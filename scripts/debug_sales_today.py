#!/usr/bin/env python3
"""
Script para verificar vendas de hoje e corrigir valores se necessário
"""

import os
import sys
from datetime import datetime

# Adicionar o diretório atual ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


def check_today_sales():
    try:
        from sqlalchemy import text

        from app.infrastructure.database.connection import SessionLocal

        db = SessionLocal()

        print("🔍 VERIFICANDO VENDAS DE HOJE:")
        sales = db.execute(
            text(
                """
            SELECT id, final_amount, created_at
            FROM sales
            WHERE status = 'COMPLETED' AND DATE(created_at) = CURRENT_DATE
            ORDER BY created_at DESC
        """
            )
        )

        total = 0
        sale_count = 0
        for row in sales:
            sale_count += 1
            value = float(row[1])
            total += value
            time_str = row[2].strftime("%H:%M:%S") if row[2] else "N/A"
            print(f"💳 Venda #{row[0]} - R$ {value:.2f} - {time_str}")

        print(f"\n📊 RESUMO:")
        print(f"🛒 Número de vendas: {sale_count}")
        print(f"💰 TOTAL ATUAL: R$ {total:.2f}")
        print(f"🎯 DEVERIA SER: R$ 13,99 (5,00 + 8,99)")
        print(f"❌ DIFERENÇA: R$ {13.99 - total:.2f}")

        # Verificar preço da Coca-Cola no produto
        print(f"\n🥤 VERIFICANDO PREÇO DA COCA-COLA:")
        coca_price = db.execute(
            text(
                """
            SELECT name, price, stock_quantity
            FROM products
            WHERE LOWER(name) LIKE '%coca%'
        """
            )
        )

        for row in coca_price:
            print(f"📦 {row[0]} - Preço: R$ {float(row[1]):.2f} - Estoque: {row[2]}")

        db.close()

        return total, sale_count

    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
        return 0, 0


if __name__ == "__main__":
    check_today_sales()
