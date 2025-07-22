#!/usr/bin/env python3
"""
Script para limpar vendas de teste e manter apenas vendas reais
"""

import os
import sys

# Adicionar o diretório atual ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


def clean_test_sales():
    try:
        from sqlalchemy import text

        from app.infrastructure.database.connection import SessionLocal

        db = SessionLocal()

        print("🧹 LIMPANDO VENDAS DE TESTE...")

        # Mostrar vendas que serão removidas
        print("\n📋 Vendas que serão REMOVIDAS (vendas de teste de R$ 368,59):")
        test_sales = db.execute(
            text(
                """
            SELECT id, final_amount, created_at
            FROM sales
            WHERE status = 'COMPLETED'
            AND DATE(created_at) = CURRENT_DATE
            AND final_amount = 368.59
            ORDER BY created_at
        """
            )
        )

        test_count = 0
        test_ids = []
        for row in test_sales:
            test_count += 1
            test_ids.append(row[0])
            time_str = row[2].strftime("%H:%M:%S") if row[2] else "N/A"
            print(f"❌ Venda #{row[0]} - R$ {float(row[1]):.2f} - {time_str}")

        # Mostrar vendas que serão MANTIDAS
        print("\n📋 Vendas que serão MANTIDAS (suas vendas reais):")
        real_sales = db.execute(
            text(
                """
            SELECT id, final_amount, created_at
            FROM sales
            WHERE status = 'COMPLETED'
            AND DATE(created_at) = CURRENT_DATE
            AND final_amount != 368.59
            ORDER BY created_at
        """
            )
        )

        real_count = 0
        real_total = 0
        for row in real_sales:
            real_count += 1
            value = float(row[1])
            real_total += value
            time_str = row[2].strftime("%H:%M:%S") if row[2] else "N/A"
            print(f"✅ Venda #{row[0]} - R$ {value:.2f} - {time_str}")

        print(f"\n📊 RESUMO DA LIMPEZA:")
        print(f"❌ Vendas de teste para remover: {test_count}")
        print(f"✅ Vendas reais para manter: {real_count}")
        print(f"💰 Total das vendas reais: R$ {real_total:.2f}")

        if test_count > 0:
            # Confirmar a limpeza
            print(f"\n⚠️  ATENÇÃO: Você quer remover {test_count} vendas de teste?")
            print("💡 Isso vai fazer o dashboard mostrar apenas suas vendas reais.")

            # Remover as vendas de teste
            if test_ids:
                ids_str = ",".join(map(str, test_ids))
                print(f"\n🗑️  Removendo vendas de teste...")

                result = db.execute(
                    text(
                        f"""
                    DELETE FROM sales
                    WHERE id IN ({ids_str})
                """
                    )
                )

                db.commit()
                print(f"✅ {result.rowcount} vendas de teste removidas!")

                # Verificar resultado final
                print(f"\n🎯 VERIFICAÇÃO FINAL:")
                final_check = db.execute(
                    text(
                        """
                    SELECT COUNT(*), COALESCE(SUM(final_amount), 0)
                    FROM sales
                    WHERE status = 'COMPLETED' AND DATE(created_at) = CURRENT_DATE
                """
                    )
                )

                row = final_check.fetchone()
                final_count = row[0] or 0
                final_total = float(row[1] or 0)

                print(f"🛒 Vendas restantes hoje: {final_count}")
                print(f"💰 Total de vendas hoje: R$ {final_total:.2f}")
                print(f"🎉 Dashboard agora deve mostrar: R$ {final_total:.2f}")

        else:
            print("\n✅ Nenhuma venda de teste encontrada para remover.")

        db.close()

        return True

    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = clean_test_sales()
    print(f"\n🏆 LIMPEZA: {'CONCLUÍDA' if success else 'FALHOU'}")
