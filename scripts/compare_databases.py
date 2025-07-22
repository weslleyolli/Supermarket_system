#!/usr/bin/env python3
"""
Testar qual banco a aplicação FastAPI está usando
"""

import requests


def test_database_in_use():
    """Verificar qual banco está sendo usado pela API"""

    # Fazer login
    login_data = {"username": "admin", "password": "admin123"}

    try:
        login_response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
        )

        if login_response.status_code != 200:
            print(f"❌ Erro no login: {login_response.status_code}")
            return

        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}

        print("🧪 TESTANDO DADOS DA API vs BANCO DIRETO...\n")

        # Testar dashboard do estoque
        response = requests.get(
            "http://localhost:8000/api/v1/stock/dashboard", headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            print("📊 DADOS DO DASHBOARD DE ESTOQUE (API):")
            print(f"  Total de produtos: {data['summary']['total_products']}")
            print(f"  Produtos em estoque: {data['summary']['products_in_stock']}")
            print(f"  Produtos sem estoque: {data['summary']['products_out_of_stock']}")
            print(f"  Alertas de estoque baixo: {data['summary']['low_stock_alerts']}")
            print(
                f"  Valor total do estoque: R$ {data['summary']['total_stock_value']}"
            )

            print(f"\n📋 TOP PRODUTOS (API):")
            for i, product in enumerate(data.get("top_products", [])[:5]):
                print(
                    f"  {i+1}. {product.get('product_name', 'N/A')} - Estoque: {product.get('current_stock', 0)}"
                )
        else:
            print(f"❌ Erro no dashboard: {response.status_code}")

        # Testar relatório detalhado
        response = requests.get(
            "http://localhost:8000/api/v1/stock/report", headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            print(f"\n📄 RELATÓRIO DETALHADO (API):")
            print(f"  Total de itens no relatório: {len(data['items'])}")
            print(f"  Valor total calculado: R$ {data['summary']['total_stock_value']}")

            print("\n📦 PRIMEIROS 5 PRODUTOS NO RELATÓRIO:")
            for i, item in enumerate(data["items"][:5]):
                stock_value = float(item["stock_value"]) if item["stock_value"] else 0.0
                print(
                    f"  {i+1}. ID: {item['product_id']} | {item['product_name']} | Estoque: {item['current_stock']} | Valor: R$ {stock_value:.2f}"
                )

        else:
            print(f"❌ Erro no relatório: {response.status_code}")

        print("\n" + "=" * 60)
        print("🏁 COMPARAÇÃO:")
        print("📊 Banco direto (PostgreSQL): 10 produtos")
        print(
            f"📡 API Dashboard: {data['summary']['total_products'] if 'data' in locals() else 'ERRO'} produtos"
        )
        print("👆 Se os números forem diferentes, a API está usando outro banco!")

    except Exception as e:
        print(f"❌ Erro: {e}")


if __name__ == "__main__":
    test_database_in_use()
