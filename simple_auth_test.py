#!/usr/bin/env python3
"""
Teste simples de autenticação
"""

import requests


def test_simple_auth():
    """Teste simples de autenticação"""
    print("🧪 TESTE SIMPLES DE AUTENTICAÇÃO")

    try:
        # Dados de login
        login_data = {"username": "admin", "password": "admin123"}

        # Fazer request
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
        )

        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.text}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Login realizado com sucesso!")
            return data.get("access_token")
        else:
            print("❌ Erro no login")
            return None

    except Exception as e:
        print(f"❌ Erro: {e}")
        return None


if __name__ == "__main__":
    test_simple_auth()
