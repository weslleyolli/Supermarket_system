#!/usr/bin/env python3
"""
Script para testar o endpoint /api/v1/reports/dashboard
"""

import json
import os
import sys

# Adicionar o diretório atual ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


def test_dashboard_endpoint():
    try:
        from unittest.mock import MagicMock

        from fastapi import Depends

        from app.core.deps import get_current_user, get_db
        from app.infrastructure.database.connection import SessionLocal
        from app.presentation.api.v1.reports import router

        print("🧪 TESTANDO ENDPOINT /api/v1/reports/dashboard")

        # Simular uma chamada ao endpoint
        db = SessionLocal()

        # Criar um mock user
        mock_user = MagicMock()
        mock_user.username = "test_user"

        # Chamar a função do endpoint diretamente
        from app.presentation.api.v1.reports import get_dashboard

        print("\n📡 Chamando get_dashboard()...")
        result = await get_dashboard(db=db, current_user=mock_user)

        print("\n📊 RESULTADO DO ENDPOINT:")
        print(json.dumps(result, indent=2, default=str))

        # Verificar campos obrigatórios
        print("\n✅ VERIFICAÇÃO DE CAMPOS:")
        required_fields = [
            "today_sales",
            "total_revenue",
            "products_sold",
            "customers_served",
            "average_ticket",
            "low_stock_alerts",
            "recent_sales",
            "top_products",
            "sales_by_period",
        ]

        missing_fields = []
        for field in required_fields:
            if field in result:
                field_value = result[field]
                print(f"✅ {field}: {field_value} ({type(field_value).__name__})")
            else:
                missing_fields.append(field)
                print(f"❌ {field}: CAMPO FALTANDO")

        if missing_fields:
            print(f"\n❌ CAMPOS FALTANDO: {missing_fields}")
            return False
        else:
            print(f"\n🎉 TODOS OS CAMPOS PRESENTES!")

            # Verificar tipos
            print(f"\n🔍 VERIFICAÇÃO DE TIPOS:")
            print(
                f'📈 today_sales: {type(result["today_sales"])} = {result["today_sales"]}'
            )
            print(
                f'💰 total_revenue: {type(result["total_revenue"])} = {result["total_revenue"]}'
            )
            print(
                f'🛒 customers_served: {type(result["customers_served"])} = {result["customers_served"]}'
            )
            print(
                f'📦 top_products: {type(result["top_products"])} com {len(result["top_products"])} itens'
            )

            return True

    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        if "db" in locals():
            db.close()


async def main():
    success = await test_dashboard_endpoint()
    print(f"\n🏆 TESTE: {'PASSOU' if success else 'FALHOU'}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
