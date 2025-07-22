#!/usr/bin/env python3
"""
Script para verificar produtos com estoque baixo
"""

import os
import sys

# Adicionar o diretório atual ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


def check_low_stock():
    try:
        from sqlalchemy import text

        from app.infrastructure.database.connection import SessionLocal

        print("🔍 VERIFICANDO PRODUTOS COM ESTOQUE BAIXO:")
        print("=" * 60)

        db = SessionLocal()

        # Query detalhada dos produtos com estoque baixo teste
        result = db.execute(
            text(
                """
            SELECT
                name,
                stock_quantity,
                min_stock_level,
                price,
                (min_stock_level - stock_quantity) as deficit,
                CASE
                    WHEN stock_quantity <= 0 THEN 'CRÍTICO'
                    WHEN stock_quantity <= min_stock_level * 0.5 THEN 'URGENTE'
                    ELSE 'ATENÇÃO'
                END as urgency_level
            FROM products
            WHERE stock_quantity <= min_stock_level
            AND is_active = true
            ORDER BY
                CASE
                    WHEN stock_quantity <= 0 THEN 1
                    WHEN stock_quantity <= min_stock_level * 0.5 THEN 2
                    ELSE 3
                END,
                stock_quantity ASC
        """
            )
        )

        alerts = list(result)

        if not alerts:
            print("✅ Nenhum produto com estoque baixo!")
            return

        print(f"⚠️  Encontrados {len(alerts)} produtos com estoque baixo:")
        print()

        for i, row in enumerate(alerts, 1):
            name = row[0]
            current = float(row[1])
            min_level = float(row[2])
            price = float(row[3])
            deficit = float(row[4])
            urgency = row[5]

            urgency_emoji = {"CRÍTICO": "🔴", "URGENTE": "🟡", "ATENÇÃO": "🟠"}

            print(f"{i}. {urgency_emoji.get(urgency, '⚠️')} {name}")
            print(f"   📦 Estoque atual: {current}")
            print(f"   📊 Mínimo necessário: {min_level}")
            print(f"   ⬇️  Déficit: {deficit} unidades")
            print(f"   💰 Preço unitário: R$ {price:.2f}")
            print(f"   💸 Custo para repor: R$ {price * deficit:.2f}")
            print(f"   🚨 Urgência: {urgency}")
            print()

        # Resumo
        total_cost = sum(float(row[3]) * float(row[4]) for row in alerts)
        critical = len([r for r in alerts if r[5] == "CRÍTICO"])
        urgent = len([r for r in alerts if r[5] == "URGENTE"])
        attention = len([r for r in alerts if r[5] == "ATENÇÃO"])

        print("=" * 60)
        print("📊 RESUMO:")
        print(f"🔴 Críticos: {critical}")
        print(f"🟡 Urgentes: {urgent}")
        print(f"🟠 Atenção: {attention}")
        print(f"💰 Custo total para repor: R$ {total_cost:.2f}")
        print("=" * 60)

        db.close()

    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    check_low_stock()
