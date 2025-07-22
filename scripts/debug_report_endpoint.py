#!/usr/bin/env python3
"""
Debug específico do endpoint de relatório
"""

import requests


def test_report_detailed():
    """Testar relatório com mais detalhes do erro"""

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

        print("🧪 TESTANDO RELATÓRIO COM DETALHES...")

        # Testar relatório
        response = requests.get(
            "http://localhost:8000/api/v1/stock/report", headers=headers
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 500:
            print("Erro 500 - Conteúdo da resposta:")
            try:
                error_data = response.json()
                print(f"Tipo: {error_data.get('type', 'N/A')}")
                print(f"Erro: {error_data.get('error', 'N/A')}")
                print("Traceback:")
                print(error_data.get("traceback", "N/A"))
            except Exception:
                print(f"Texto da resposta: {response.text[:2000]}...")
        else:
            print("✅ Relatório funcionando!")
            data = response.json()
            print(
                f"Dados retornados: {list(data.keys()) if isinstance(data, dict) else type(data)}"
            )

    except Exception as e:
        print(f"❌ Erro: {e}")


if __name__ == "__main__":
    test_report_detailed()
