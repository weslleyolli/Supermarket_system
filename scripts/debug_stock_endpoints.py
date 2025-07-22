#!/usr/bin/env python3
"""
Debug específico dos endpoints com erro 500
"""

import json

import requests


def test_dashboard_detailed():
    """Testar dashboard com mais detalhes do erro"""

    # Fazer login primeiro
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

        print("🧪 TESTANDO DASHBOARD COM DETALHES...")

        # Testar dashboard
        response = requests.get(
            "http://localhost:8000/api/v1/stock/dashboard", headers=headers
        )

        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")

        if response.status_code == 500:
            print(f"Erro 500 - Conteúdo da resposta:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(f"Texto da resposta: {response.text}")
        else:
            print("✅ Dashboard funcionando!")
            data = response.json()
            print(
                f"Dados retornados: {list(data.keys()) if isinstance(data, dict) else type(data)}"
            )

    except Exception as e:
        print(f"❌ Erro: {e}")


def test_movements_detailed():
    """Testar movimentações com detalhes"""

    # Fazer login primeiro
    login_data = {"username": "admin", "password": "admin123"}

    try:
        login_response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
        )

        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}

        print("\n🧪 TESTANDO MOVIMENTAÇÕES COM DETALHES...")

        # Testar movimentações
        response = requests.get(
            "http://localhost:8000/api/v1/stock/movements", headers=headers
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 500:
            print(f"Erro 500 - Conteúdo da resposta:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(f"Texto da resposta: {response.text}")
        else:
            print("✅ Movimentações funcionando!")
            data = response.json()
            print(
                f"Total de movimentações: {len(data) if isinstance(data, list) else 'N/A'}"
            )

    except Exception as e:
        print(f"❌ Erro: {e}")


if __name__ == "__main__":
    test_dashboard_detailed()
    test_movements_detailed()
