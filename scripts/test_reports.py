"""
Script para testar os endpoints de relatório
"""
import json
from datetime import date

import requests


def test_dashboard():
    """Testar endpoint de dashboard"""
    try:
        # Primeiro fazer login para obter token
        print("🔐 Fazendo login...")
        login_response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"},
        )
        print(f"Login status: {login_response.status_code}")
        if login_response.status_code == 200:
            print("✅ Login realizado com sucesso!")
        else:
            print(f"❌ Erro no login: {login_response.text}")

        if login_response.status_code != 200:
            print(f"❌ Erro no login: {login_response.status_code}")
            print(login_response.text)
            return

        token_data = login_response.json()
        token = token_data["access_token"]

        headers = {"Authorization": f"Bearer {token}"}

        # Testar endpoint de dashboard
        print("🔍 Testando endpoint de dashboard...")
        dashboard_response = requests.get(
            "http://localhost:8000/api/v1/reports/dashboard", headers=headers
        )

        print(f"Status: {dashboard_response.status_code}")
        if dashboard_response.status_code == 200:
            data = dashboard_response.json()
            print("✅ Dashboard funcionando!")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Erro no dashboard: {dashboard_response.text}")

        # Testar endpoint de KPIs
        print("\n🔍 Testando endpoint de KPIs...")
        kpis_response = requests.get(
            "http://localhost:8000/api/v1/reports/kpis", headers=headers
        )

        print(f"Status: {kpis_response.status_code}")
        if kpis_response.status_code == 200:
            data = kpis_response.json()
            print("✅ KPIs funcionando!")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Erro nos KPIs: {kpis_response.text}")

        # Testar endpoint de vendas
        print("\n🔍 Testando endpoint de vendas...")
        sales_response = requests.get(
            "http://localhost:8000/api/v1/reports/sales", headers=headers
        )

        print(f"Status: {sales_response.status_code}")
        if sales_response.status_code == 200:
            data = sales_response.json()
            print("✅ Relatório de vendas funcionando!")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Erro no relatório de vendas: {sales_response.text}")

    except requests.exceptions.ConnectionError:
        print(
            "❌ Erro: Servidor não está rodando. Execute 'uvicorn app.main:app --reload' primeiro."
        )
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")


if __name__ == "__main__":
    test_dashboard()
