#!/usr/bin/env python3
"""
Script para criar usuário admin e testar autenticação
"""

import os
import sys

from passlib.context import CryptContext
from sqlalchemy import create_engine, text

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.connection import get_database_url

# Configuração de hash de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def check_users():
    """Verificar usuários existentes"""

    print("🔍 VERIFICANDO USUÁRIOS EXISTENTES...")

    database_url = get_database_url()
    engine = create_engine(database_url)

    with engine.connect() as conn:
        try:
            # Verificar se a tabela users existe
            result = conn.execute(
                text(
                    """
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_name = 'users'
            """
                )
            ).scalar()

            if result == 0:
                print("❌ Tabela 'users' não encontrada")
                return False

            # Contar usuários
            user_count = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
            print(f"📊 Total de usuários: {user_count}")

            if user_count > 0:
                # Listar usuários
                users = conn.execute(
                    text(
                        """
                    SELECT id, username, email, is_active
                    FROM users
                    LIMIT 5
                """
                    )
                ).fetchall()

                print("👥 Usuários encontrados:")
                for user in users:
                    status = "🟢 Ativo" if user[3] else "🔴 Inativo"
                    print(f"   ID: {user[0]} | {user[1]} | {user[2]} | {status}")

                return True
            else:
                print("❌ Nenhum usuário encontrado")
                return False

        except Exception as e:
            print(f"❌ Erro ao verificar usuários: {e}")
            return False


def create_admin_user():
    """Criar usuário administrador"""

    print("\n🔧 CRIANDO USUÁRIO ADMINISTRADOR...")

    database_url = get_database_url()
    engine = create_engine(database_url)

    # Dados do admin
    admin_data = {
        "username": "admin",
        "email": "admin@supermarket.com",
        "password": "admin123",  # Senha padrão
        "full_name": "Administrador do Sistema",
    }

    # Hash da senha
    hashed_password = pwd_context.hash(admin_data["password"])

    try:
        with engine.connect() as conn:
            with conn.begin():
                # Verificar se admin já existe
                existing = conn.execute(
                    text(
                        """
                    SELECT id FROM users
                    WHERE username = :username OR email = :email
                """
                    ),
                    {"username": admin_data["username"], "email": admin_data["email"]},
                ).fetchone()

                if existing:
                    print(f"✅ Usuário admin já existe (ID: {existing[0]})")
                    return existing[0]

                # Criar usuário admin
                result = conn.execute(
                    text(
                        """
                    INSERT INTO users (username, email, hashed_password, full_name, is_active, is_superuser)
                    VALUES (:username, :email, :password, :full_name, true, true)
                    RETURNING id
                """
                    ),
                    {
                        "username": admin_data["username"],
                        "email": admin_data["email"],
                        "password": hashed_password,
                        "full_name": admin_data["full_name"],
                    },
                )

                user_id = result.scalar()
                print(f"✅ Usuário admin criado com sucesso (ID: {user_id})")
                print(f"📋 Credenciais:")
                print(f"   Usuário: {admin_data['username']}")
                print(f"   Email: {admin_data['email']}")
                print(f"   Senha: {admin_data['password']}")

                return user_id

    except Exception as e:
        print(f"❌ Erro ao criar usuário admin: {e}")
        return None


def test_login_endpoint():
    """Testar o endpoint de login"""

    print("\n🧪 TESTANDO ENDPOINT DE LOGIN...")

    try:
        import requests

        # Dados de login
        login_data = {"username": "admin", "password": "admin123"}

        # Testar login
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if response.status_code == 200:
            data = response.json()
            print("✅ Login realizado com sucesso!")
            print(f"📋 Token: {data.get('access_token', 'N/A')[:50]}...")
            print(f"📋 Tipo: {data.get('token_type', 'N/A')}")
            return True
        else:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"📋 Resposta: {response.text}")
            return False

    except ImportError:
        print("❌ Biblioteca 'requests' não encontrada")
        print("💡 Execute: pip install requests")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar login: {e}")
        return False


def test_stock_endpoints():
    """Testar endpoints de estoque"""

    print("\n🧪 TESTANDO ENDPOINTS DE ESTOQUE...")

    try:
        import requests

        # Primeiro fazer login para obter token
        login_response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            data={"username": "admin", "password": "admin123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if login_response.status_code != 200:
            print("❌ Não foi possível fazer login para testar endpoints")
            return False

        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Testar endpoints de estoque
        endpoints = [
            ("GET", "/api/v1/stock/suppliers", "Fornecedores"),
            ("GET", "/api/v1/stock/dashboard", "Dashboard de Estoque"),
            ("GET", "/api/v1/stock/movements", "Movimentações"),
            ("GET", "/api/v1/stock/alerts", "Alertas de Estoque"),
        ]

        for method, endpoint, description in endpoints:
            try:
                response = requests.get(
                    f"http://localhost:8000{endpoint}", headers=headers
                )
                if response.status_code == 200:
                    print(f"✅ {description}: {response.status_code}")
                else:
                    print(f"❌ {description}: {response.status_code}")
            except Exception as e:
                print(f"❌ {description}: Erro - {e}")

        print("🎯 Teste de endpoints concluído!")
        return True

    except Exception as e:
        print(f"❌ Erro ao testar endpoints: {e}")
        return False


def main():
    """Função principal"""
    print("🔐 CONFIGURAÇÃO DE AUTENTICAÇÃO E TESTE DE ENDPOINTS")
    print("=" * 60)

    # 1. Verificar usuários existentes
    users_exist = check_users()

    # 2. Criar admin se necessário
    if not users_exist:
        admin_id = create_admin_user()
        if not admin_id:
            print("❌ Falha ao criar usuário admin")
            sys.exit(1)

    # 3. Testar login
    login_success = test_login_endpoint()

    # 4. Testar endpoints de estoque se login funcionou
    if login_success:
        test_stock_endpoints()

    print(f"\n🎉 CONFIGURAÇÃO CONCLUÍDA!")
    print(f"\n📋 PARA ACESSAR O SISTEMA:")
    print(f"   🌐 API Docs: http://localhost:8000/docs")
    print(f"   🔐 Login: admin / admin123")
    print(f"   📊 Stock API: http://localhost:8000/api/v1/stock/")


if __name__ == "__main__":
    main()
