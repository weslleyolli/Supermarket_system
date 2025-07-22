#!/usr/bin/env python3
"""
Debug detalhado para identificar o erro específico
"""

import json

import requests


def test_all_endpoints():
    """Testar todos os endpoints para identificar qual está falhando"""

    # Fazer login primeiro
    login_data = {"username": "admin", "password": "admin123"}

    try:
        print("🔐 Fazendo login...")
        login_response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
        )

        if login_response.status_code != 200:
            print(f"❌ Erro no login: {login_response.status_code}")
            print(f"Resposta: {login_response.text}")
            return

        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login realizado com sucesso")

        # Lista de endpoints para testar
        endpoints = [
            "/api/v1/stock/dashboard",
            "/api/v1/stock/movements",
            "/api/v1/stock/suppliers",
            "/api/v1/stock/alerts",
            "/api/v1/stock/report",
        ]

        for endpoint in endpoints:
            print(f"\n🧪 TESTANDO: {endpoint}")
            try:
                response = requests.get(
                    f"http://localhost:8000{endpoint}", headers=headers, timeout=10
                )
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    print(f"✅ {endpoint} - OK")
                    data = response.json()
                    print(f"Tipo de resposta: {type(data)}")
                    if isinstance(data, dict):
                        print(f"Chaves: {list(data.keys())}")
                    elif isinstance(data, list):
                        print(f"Lista com {len(data)} itens")
                elif response.status_code == 500:
                    print(f"❌ {endpoint} - ERRO 500")
                    print("Conteúdo da resposta:")
                    print(response.text[:1000])  # Primeiros 1000 caracteres
                else:
                    print(f"⚠️ {endpoint} - Status {response.status_code}")
                    print(f"Resposta: {response.text[:500]}")
            except requests.exceptions.Timeout:
                print(f"⏰ {endpoint} - TIMEOUT")
            except Exception as e:
                print(f"💥 {endpoint} - ERRO: {e}")

        # Teste de POST para criação de produto
        print("\n🧪 TESTANDO: POST /api/v1/products/")
        product_payload = {
            "name": "Coca-Cola 2L",
            "barcode": "07892840814540",
            "price": 8.99,
            "cost_price": 6.00,
            "category_id": 1,
            "supplier_id": 1,
            "stock_quantity": 10,
            "min_stock_level": 2,
            "is_active": True,
        }
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/products/",
                headers={**headers, "Content-Type": "application/json"},
                json=product_payload,
                timeout=10,
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 201:
                print("✅ Produto criado com sucesso!")
                print(response.json())
            else:
                print(f"⚠️ Erro ao criar produto - Status {response.status_code}")
                try:
                    print("Resposta detalhada:")
                    print(response.json())
                except Exception:
                    print(response.text)
        except Exception as e:
            print(f"💥 Erro no POST de produto: {e}")

        print("\n" + "=" * 50)
        print("RESUMO DOS TESTES CONCLUÍDO")

    except Exception as e:
        print(f"💥 Erro geral: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_all_endpoints()
