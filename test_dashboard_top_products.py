#!/usr/bin/env python3
"""
Script para testar se o dashboard está retornando os top products corretamente
"""

import json
import os
import sys

# Adicionar o diretório atual ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


def test_dashboard_top_products():
    try:
        from sqlalchemy import text

        from app.infrastructure.database.connection import SessionLocal

        print("🧪 TESTANDO DASHBOARD - TOP 5 PRODUTOS:")
        print("=" * 60)

        db = SessionLocal()

        # Testar a mesma query que está no dashboard
        print("📡 Executando query do dashboard...")

        # Query exata do dashboard
        top_products_result = db.execute(
            text(
                """
                SELECT
                    p.name,
                    p.price,
                    COALESCE(SUM(si.quantity), 0) as total_sold,
                    COUNT(DISTINCT s.id) as times_sold
                FROM products p
                LEFT JOIN sale_items si ON p.id = si.product_id
                LEFT JOIN sales s ON si.sale_id = s.id AND s.status = 'COMPLETED'
                WHERE p.is_active = true
                GROUP BY p.id, p.name, p.price
                HAVING SUM(si.quantity) > 0
                ORDER BY total_sold DESC, times_sold DESC
                LIMIT 5
            """
            )
        )

        top_products = []
        for row in top_products_result:
            top_products.append(
                {
                    "name": row[0],
                    "price": float(row[1]) if row[1] else 0.0,
                    "quantity_sold": int(row[2]) if row[2] else 0,
                    "times_sold": int(row[3]) if row[3] else 0,
                }
            )

        print(f"✅ Encontrados {len(top_products)} produtos no top 5")
        print()

        # Mostrar dados como JSON (igual ao que o dashboard retorna)
        print("📊 DADOS PARA O DASHBOARD (formato JSON):")
        print(json.dumps(top_products, indent=2, ensure_ascii=False))
        print()

        # Verificar se os dados estão corretos
        if len(top_products) > 0:
            print("🎯 VERIFICAÇÃO DOS DADOS:")
            for i, product in enumerate(top_products, 1):
                print(f"{i}. Nome: '{product['name']}'")
                print(f"   Preço: R$ {product['price']:.2f}")
                print(f"   Vendido: {product['quantity_sold']} unidades")
                print(f"   Transações: {product['times_sold']}")
                print()

            print("✅ DASHBOARD VAI MOSTRAR:")
            print(
                f"🏆 Top 1: {top_products[0]['name']} ({top_products[0]['quantity_sold']} vendidas)"
            )

            if len(top_products) > 1:
                for i in range(1, len(top_products)):
                    print(
                        f"🏅 Top {i+1}: {top_products[i]['name']} ({top_products[i]['quantity_sold']} vendidas)"
                    )
            else:
                print(
                    "💡 Apenas 1 produto no ranking (precisa de mais vendas para top 5)"
                )
        else:
            print("❌ Nenhum produto no top 5 - verifique se há vendas registradas")

        # Simular resposta completa do dashboard
        print("\n" + "=" * 60)
        print("📈 RESPOSTA COMPLETA DO DASHBOARD:")
        dashboard_response = {
            "top_products": top_products,
            "message": f"Top {len(top_products)} produtos mais vendidos",
        }
        print(json.dumps(dashboard_response, indent=2, ensure_ascii=False))

        db.close()

        return len(top_products) > 0

    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_dashboard_top_products()
    print(f"\n🏆 TESTE: {'✅ PASSOU' if success else '❌ FALHOU'}")

    if success:
        print("\n💡 PRÓXIMOS PASSOS:")
        print("1. ✅ O dashboard já tem os dados corretos")
        print("2. 🔄 Recarregue a página do frontend (F5)")
        print("3. 📊 Verifique se o gráfico de top 5 produtos aparece")
        print("4. 🛒 Faça mais vendas para ver o ranking completo!")
    else:
        print("\n❌ PROBLEMA IDENTIFICADO:")
        print("- Verifique se há vendas registradas no sistema")
        print("- Execute: python3 check_top_products.py")
