#!/usr/bin/env python3
"""
Script para limpar TODAS as vendas e começar do zero
"""

import os
import sys

# Adicionar o diretório atual ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


def reset_all_sales():
    try:
        from sqlalchemy import text

        from app.infrastructure.database.connection import SessionLocal

        db = SessionLocal()

        print("🔥 RESETANDO TODAS AS VENDAS...")

        # Mostrar vendas que serão removidas
        print("\n📋 Todas as vendas que serão REMOVIDAS:")
        all_sales = db.execute(
            text(
                """
            SELECT id, final_amount, created_at, status
            FROM sales
            ORDER BY created_at DESC
        """
            )
        )

        total_count = 0
        total_value = 0
        for row in all_sales:
            total_count += 1
            value = float(row[1]) if row[1] else 0
            total_value += value
            time_str = row[2].strftime("%Y-%m-%d %H:%M:%S") if row[2] else "N/A"
            print(f"❌ Venda #{row[0]} - R$ {value:.2f} - {time_str} - {row[3]}")

        print(f"\n📊 RESUMO ANTES DA LIMPEZA:")
        print(f"🛒 Total de vendas: {total_count}")
        print(f"💰 Valor total: R$ {total_value:.2f}")

        if total_count > 0:
            print(f"\n⚠️  ATENÇÃO: Você vai APAGAR {total_count} vendas!")
            print("💡 Depois disso o dashboard vai mostrar R$ 0,00")
            print("🔄 Suas próximas compras serão contadas do zero")

            # Limpar TODAS as vendas
            print(f"\n🗑️  Removendo TODAS as vendas...")

            # Remover sale_items primeiro (Foreign Key)
            result_items = db.execute(text("DELETE FROM sale_items"))
            print(f"🧹 {result_items.rowcount} itens de venda removidos")

            # Remover vendas
            result_sales = db.execute(text("DELETE FROM sales"))
            print(f"🧹 {result_sales.rowcount} vendas removidas")

            # Resetar sequência dos IDs (opcional)
            db.execute(text("ALTER SEQUENCE sales_id_seq RESTART WITH 1"))
            db.execute(text("ALTER SEQUENCE sale_items_id_seq RESTART WITH 1"))

            db.commit()
            print(f"✅ TODAS as vendas foram removidas!")

            # Verificar resultado final
            print(f"\n🎯 VERIFICAÇÃO FINAL:")
            final_check = db.execute(text("SELECT COUNT(*) FROM sales"))
            final_count = final_check.scalar() or 0

            print(f"🛒 Vendas restantes: {final_count}")
            print(f"💰 Dashboard agora deve mostrar: R$ 0,00")
            print(f"🎉 Sistema limpo! Próximas compras serão contadas do zero.")

        else:
            print("\n✅ Nenhuma venda encontrada para remover.")

        db.close()

        return True

    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = reset_all_sales()
    print(f"\n🏆 RESET: {'CONCLUÍDO' if success else 'FALHOU'}")
