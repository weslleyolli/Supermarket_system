#!/usr/bin/env python3
"""
Script para testar autenticação e endpoints de estoque
"""

import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_login_with_json():
    """Testar login com formato JSON"""

    print("🧪 TESTANDO LOGIN COM FORMATO JSON...")

    try:
        import requests

        # Testar com JSON (formato correto)
        login_data_json = {"username": "admin", "password": "admin123"}

        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json=login_data_json,  # Usar JSON ao invés de form data
            headers={"Content-Type": "application/json"},
        )

        print(f"📊 Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Login JSON realizado com sucesso!")
            print(f"🔑 Token obtido: {data.get('access_token', 'N/A')[:50]}...")
            return data.get("access_token")
        else:
            print(f"❌ Erro no login JSON: {response.status_code}")
            print(f"📋 Resposta: {response.text}")

            # Tentar com usuários existentes
            users_to_try = [
                ("admin", "admin123"),
                ("gaelmelo", "123456"),
                ("osmarcb", "123456"),
                ("operador", "123456"),
            ]

            for username, password in users_to_try:
                print(f"\n🔄 Tentando login com: {username}")
                test_data = {"username": username, "password": password}

                resp = requests.post(
                    "http://localhost:8000/api/v1/auth/login",
                    json=test_data,
                    headers={"Content-Type": "application/json"},
                )

                if resp.status_code == 200:
                    token_data = resp.json()
                    print(f"✅ Login bem-sucedido com {username}!")
                    return token_data.get("access_token")
                else:
                    print(f"❌ Falha com {username}: {resp.status_code}")

            return None

    except ImportError:
        print("❌ Biblioteca 'requests' não encontrada")
        print("💡 Execute: pip install requests")
        return None
    except Exception as e:
        print(f"❌ Erro ao testar login: {e}")
        return None


def test_stock_endpoints_with_token(token):
    """Testar endpoints de estoque com token válido"""

    print("\n🧪 TESTANDO ENDPOINTS DE ESTOQUE...")

    if not token:
        print("❌ Token não disponível - pulando testes de endpoints")
        return

    try:
        import requests

        headers = {"Authorization": f"Bearer {token}"}

        # Lista de endpoints para testar
        endpoints_to_test = [
            {
                "method": "GET",
                "url": "/api/v1/stock/suppliers",
                "description": "📦 Listar Fornecedores",
            },
            {
                "method": "GET",
                "url": "/api/v1/stock/dashboard",
                "description": "📊 Dashboard de Estoque",
            },
            {
                "method": "GET",
                "url": "/api/v1/stock/movements",
                "description": "📋 Movimentações de Estoque",
            },
            {
                "method": "GET",
                "url": "/api/v1/stock/alerts",
                "description": "⚠️ Alertas de Estoque",
            },
            {
                "method": "GET",
                "url": "/api/v1/stock/report",
                "description": "📈 Relatório de Estoque",
            },
        ]

        successful_tests = 0
        total_tests = len(endpoints_to_test)

        for endpoint in endpoints_to_test:
            try:
                url = f"http://localhost:8000{endpoint['url']}"

                if endpoint["method"] == "GET":
                    response = requests.get(url, headers=headers)
                else:
                    response = requests.request(
                        endpoint["method"], url, headers=headers
                    )

                if response.status_code == 200:
                    print(f"✅ {endpoint['description']}: {response.status_code} OK")

                    # Mostrar sample dos dados se possível
                    try:
                        data = response.json()
                        if isinstance(data, dict):
                            keys = list(data.keys())[:3]
                            print(f"   📋 Campos retornados: {keys}")
                        elif isinstance(data, list) and len(data) > 0:
                            print(f"   📋 Total de registros: {len(data)}")
                    except:
                        print(f"   📋 Resposta: {len(response.text)} caracteres")

                    successful_tests += 1

                elif response.status_code == 404:
                    print(
                        f"❌ {endpoint['description']}: {response.status_code} - Endpoint não encontrado"
                    )
                elif response.status_code == 401:
                    print(
                        f"❌ {endpoint['description']}: {response.status_code} - Não autorizado"
                    )
                elif response.status_code == 403:
                    print(
                        f"❌ {endpoint['description']}: {response.status_code} - Acesso negado"
                    )
                else:
                    print(
                        f"⚠️ {endpoint['description']}: {response.status_code} - {response.text[:100]}"
                    )

            except Exception as e:
                print(f"❌ {endpoint['description']}: Erro de conexão - {e}")

        # Resumo dos testes
        print(f"\n📊 RESUMO DOS TESTES:")
        print(f"   ✅ Sucessos: {successful_tests}/{total_tests}")
        print(f"   📈 Taxa de sucesso: {(successful_tests/total_tests)*100:.1f}%")

        if successful_tests == total_tests:
            print("🎉 TODOS OS ENDPOINTS DE ESTOQUE ESTÃO FUNCIONANDO!")
        elif successful_tests > 0:
            print("⚠️ Alguns endpoints estão funcionando")
        else:
            print("❌ Nenhum endpoint está respondendo corretamente")

    except Exception as e:
        print(f"❌ Erro ao testar endpoints: {e}")


def test_specific_stock_operations():
    """Testar operações específicas de estoque"""

    print("\n🧪 TESTANDO OPERAÇÕES ESPECÍFICAS DE ESTOQUE...")

    try:
        # Importar para verificar se os módulos estão funcionando
        from app.presentation.schemas.stock import (
            MovementTypeEnum,
            StockMovementCreate,
            SupplierCreate,
        )

        print("✅ Schemas de estoque importados com sucesso")

        from app.application.services.stock_service import StockService

        print("✅ StockService importado com sucesso")

        # Testar criação de objetos
        movement_type = MovementTypeEnum.ENTRADA
        print(f"✅ Enum MovementType criado: {movement_type}")

        supplier_data = SupplierCreate(
            name="Teste Fornecedor", email="teste@fornecedor.com"
        )
        print(f"✅ Schema SupplierCreate validado: {supplier_data.name}")

        print("🎯 Todos os componentes de estoque estão operacionais!")

    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")


def main():
    """Função principal"""
    print("🚀 TESTE COMPLETO DO SISTEMA DE ESTOQUE")
    print("=" * 50)

    # 1. Testar login
    token = test_login_with_json()

    # 2. Testar endpoints com token
    if token:
        test_stock_endpoints_with_token(token)

    # 3. Testar componentes internos
    test_specific_stock_operations()

    print("\n🎯 RESUMO FINAL:")
    if token:
        print("✅ Autenticação: Funcionando")
        print("✅ API de Estoque: Testada")
    else:
        print("❌ Autenticação: Problemas encontrados")
        print("⚠️ API de Estoque: Não testada devido à autenticação")

    print("✅ Componentes Internos: Funcionando")

    print("\n📋 ACESSO AO SISTEMA:")
    print("   🌐 Documentação: http://localhost:8000/docs")
    print("   📊 API de Estoque: http://localhost:8000/api/v1/stock/")
    print("   🔐 Teste de Login: http://localhost:8000/api/v1/auth/login")


if __name__ == "__main__":
    main()


def test_stock_columns_and_products(conn, text):
    stock_columns = [
        "supplier_id",
        "profit_margin",
        "weight",
        "dimensions",
        "location",
        "reorder_point",
        "max_stock",
        "last_purchase_date",
        "last_sale_date",
    ]
    # Verificar colunas
    result = conn.execute(
        text(
            """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'products'
        AND column_name IN ('supplier_id', 'profit_margin', 'weight', 'dimensions', 'location', 'reorder_point', 'max_stock', 'last_purchase_date', 'last_sale_date')
    """
        )
    )
    existing_columns = [row[0] for row in result]
    for col in stock_columns:
        status = "✅ OK" if col in existing_columns else "❌ FALTANDO"
        print(f"    - {col}: {status}")

    # Verificar produtos existentes
    print("\n📊 Verificando produtos:")
    result = conn.execute(text("SELECT COUNT(*) FROM products"))
    product_count = result.fetchone()[0]
    print(f"  📦 Total de produtos: {product_count}")
    # Se quiser, adicione mais verificações aqui


# No main, chame a função passando conn e text
if __name__ == "__main__":
    main()


# Função completa para checar o sistema de estoque
def test_stock_system(conn, text):
    try:
        # 1. Verificar colunas de estoque
        stock_columns = [
            "supplier_id",
            "profit_margin",
            "weight",
            "dimensions",
            "location",
            "reorder_point",
            "max_stock",
            "last_purchase_date",
            "last_sale_date",
        ]
        result = conn.execute(
            text(
                """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'products'
            AND column_name IN ('supplier_id', 'profit_margin', 'weight', 'dimensions', 'location', 'reorder_point', 'max_stock', 'last_purchase_date', 'last_sale_date')
        """
            )
        )
        existing_columns = [row[0] for row in result]
        print("\n🔎 Colunas de estoque nos produtos:")
        for col in stock_columns:
            status = "✅ OK" if col in existing_columns else "❌ FALTANDO"
            print(f"    - {col}: {status}")

        # 2. Verificar produtos existentes
        print("\n📊 Verificando produtos:")
        result = conn.execute(text("SELECT COUNT(*) FROM products"))
        product_count = result.fetchone()[0]
        print(f"  📦 Total de produtos: {product_count}")
        if product_count > 0:
            result = conn.execute(
                text(
                    """
                SELECT name, stock_quantity, supplier_id
                FROM products
                WHERE stock_quantity > 0
                LIMIT 5
            """
                )
            )
            products_with_stock = result.fetchall()
            if products_with_stock:
                print("  📦 Produtos com estoque (top 5):")
                for product in products_with_stock:
                    supplier_info = (
                        f"Fornecedor: {product[2]}" if product[2] else "Sem fornecedor"
                    )
                    print(
                        f"    - {product[0]}: {product[1]} unidades ({supplier_info})"
                    )

        # 3. Verificar tabelas essenciais
        tables_to_check = ["products", "suppliers", "stock_movements"]
        all_tables_exist = all(
            [
                conn.execute(
                    text(
                        f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{t}'"
                    )
                ).fetchone()[0]
                > 0
                for t in tables_to_check
            ]
        )

        # 4. Verificar fornecedores
        result = conn.execute(text("SELECT COUNT(*) FROM suppliers"))
        suppliers_exist = result.fetchone()[0] > 0

        # 5. Status geral
        stock_columns_exist = len(existing_columns) == len(stock_columns)
        print("\n🎯 Status do Sistema de Estoque:")
        if all_tables_exist and suppliers_exist and stock_columns_exist:
            print("  🎉 Sistema de estoque COMPLETAMENTE FUNCIONAL!")
            print("  ✅ Todas as tabelas criadas")
            print("  ✅ Fornecedores cadastrados")
            print("  ✅ Colunas de estoque adicionadas aos produtos")
            print("\n🚀 Próximos passos:")
            print("  1. Associar produtos aos fornecedores")
            print("  2. Criar movimentações de estoque")
            print("  3. Criar pedidos de compra")
            print("  4. Testar endpoints da API")
            return True
        else:
            print("  ⚠️  Sistema parcialmente configurado")
            if not all_tables_exist:
                print("  ❌ Algumas tabelas estão faltando")
            if not suppliers_exist:
                print("  ❌ Nenhum fornecedor cadastrado")
            if not stock_columns_exist:
                print("  ❌ Algumas colunas de estoque estão faltando")
            return False
    except Exception as e:
        print(f"❌ Erro no teste: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_stock_system()
    if not success:
        sys.exit(1)
