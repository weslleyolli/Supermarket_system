"""
Script para verificar se os dados do dashboard estão sendo carregados corretamente
do banco de dados e se a API está retornando dados reais.
"""

import asyncio
import json
import os
import sys
from datetime import datetime

import httpx

# Adicionar o diretório raiz ao path para importar módulos da aplicação
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text

from app.core.config import settings


def verify_database_connection():
    """Verificar conexão direta com o banco de dados"""
    print("🔍 VERIFICANDO CONEXÃO COM BANCO DE DADOS...")

    try:
        # Obter URL do banco
        database_url = settings.DATABASE_URL
        engine = create_engine(database_url)

        # Testar conexão
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Conexão com banco OK")

            # Verificar tabelas existentes (SQLite)
            if "sqlite" in database_url:
                tables_result = conn.execute(
                    text(
                        """
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """
                    )
                )
            else:
                # PostgreSQL
                tables_result = conn.execute(
                    text(
                        """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                """
                    )
                )
            tables = [row[0] for row in tables_result]
            print(f"📋 Tabelas encontradas: {tables}")

            # Contar registros nas tabelas principais
            counts = {}
            for table in ["users", "products", "sales", "categories", "customers"]:
                if table in tables:
                    count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    counts[table] = count_result.scalar()

            print("📊 CONTAGEM DE REGISTROS:")
            for table, count in counts.items():
                print(f"   {table}: {count} registros")

            # Verificar vendas específicas
            if "sales" in tables:
                # Primeiro, verificar quais status existem
                status_check = conn.execute(text("SELECT DISTINCT status FROM sales"))
                available_statuses = [row[0] for row in status_check]
                print(f"   Status disponíveis: {available_statuses}")

                # Contar todas as vendas primeiro
                all_sales = conn.execute(text("SELECT COUNT(*) FROM sales"))
                total_all_sales = all_sales.scalar()
                print(f"   Total de todas as vendas: {total_all_sales}")

                # Tentar buscar vendas com status 'COMPLETED' (maiúsculo)
                try:
                    sales_result = conn.execute(
                        text(
                            """
                        SELECT
                            COUNT(*) as total_sales,
                            SUM(final_amount) as total_revenue,
                            AVG(final_amount) as avg_ticket
                        FROM sales
                        WHERE status = 'COMPLETED'
                    """
                        )
                    )
                    sales_data = sales_result.fetchone()

                    print("\n💰 DADOS DE VENDAS REAIS (STATUS=COMPLETED):")
                    print(f"   Total de vendas: {sales_data[0]}")
                    print(f"   Receita total: R$ {sales_data[1]:.2f}")
                    print(f"   Ticket médio: R$ {sales_data[2]:.2f}")

                except Exception as status_error:
                    print(f"   ⚠️ Erro com status 'COMPLETED': {status_error}")

                    # Tentar com todos os registros
                    sales_result = conn.execute(
                        text(
                            """
                        SELECT
                            COUNT(*) as total_sales,
                            SUM(final_amount) as total_revenue,
                            AVG(final_amount) as avg_ticket
                        FROM sales
                    """
                        )
                    )
                    sales_data = sales_result.fetchone()

                    print("\n💰 DADOS DE TODAS AS VENDAS:")
                    print(f"   Total de vendas: {sales_data[0]}")
                    print(f"   Receita total: R$ {sales_data[1]:.2f}")
                    print(f"   Ticket médio: R$ {sales_data[2]:.2f}")

            return True, counts

    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False, {}


async def test_api_endpoints():
    """Testar endpoints da API diretamente"""
    print("\n🌐 TESTANDO ENDPOINTS DA API...")

    base_url = "http://localhost:8000/api/v1"

    # Primeiro, fazer login para obter token
    async with httpx.AsyncClient() as client:
        try:
            # Login
            login_response = await client.post(
                f"{base_url}/auth/login",
                json={"username": "admin", "password": "admin123"},
            )

            if login_response.status_code != 200:
                print(f"❌ Erro no login: {login_response.status_code}")
                print(f"   Response: {login_response.text}")
                return False

            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Login realizado com sucesso")

            # Testar endpoints
            endpoints = [
                "/reports/dashboard",
                "/reports/kpis",
                "/reports/sales",
                "/reports/stock-alerts",
            ]

            results = {}
            for endpoint in endpoints:
                try:
                    response = await client.get(
                        f"{base_url}{endpoint}", headers=headers
                    )

                    if response.status_code == 200:
                        data = response.json()
                        results[endpoint] = {"status": "✅ OK", "data": data}
                        print(f"✅ {endpoint}: OK")

                        # Mostrar dados principais do dashboard
                        if endpoint == "/reports/dashboard":
                            print(
                                f"   📊 Total vendas: {data.get('total_sales', 'N/A')}"
                            )
                            print(
                                f"   💰 Receita total: R$ {data.get('total_revenue', 'N/A')}"
                            )
                            print(
                                f"   📦 Total produtos: {data.get('total_products', 'N/A')}"
                            )
                            print(
                                f"   ⚠️ Alertas estoque: {data.get('low_stock_alerts', 'N/A')}"
                            )

                    else:
                        results[endpoint] = {
                            "status": f"❌ ERROR {response.status_code}",
                            "data": response.text,
                        }
                        print(f"❌ {endpoint}: ERROR {response.status_code}")

                except Exception as e:
                    results[endpoint] = {"status": f"❌ EXCEPTION", "data": str(e)}
                    print(f"❌ {endpoint}: EXCEPTION {e}")

            return results

        except Exception as e:
            print(f"❌ Erro geral na API: {e}")
            return False


def compare_db_vs_api(db_counts, api_results):
    """Comparar dados do banco vs API"""
    print("\n🔄 COMPARANDO DADOS DO BANCO vs API...")

    if not api_results or "/reports/dashboard" not in api_results:
        print("❌ Não foi possível obter dados da API para comparação")
        return

    dashboard_data = api_results["/reports/dashboard"]["data"]

    print("📊 COMPARAÇÃO:")
    print(f"   Vendas no banco: {db_counts.get('sales', 'N/A')}")
    print(f"   Vendas na API: {dashboard_data.get('total_sales', 'N/A')}")

    print(f"   Produtos no banco: {db_counts.get('products', 'N/A')}")
    print(f"   Produtos na API: {dashboard_data.get('total_products', 'N/A')}")

    # Verificar se os números batem
    sales_match = db_counts.get("sales", 0) == dashboard_data.get("total_sales", -1)
    products_match = db_counts.get("products", 0) == dashboard_data.get(
        "total_products", -1
    )

    print(f"\n🎯 RESULTADO:")
    print(f"   Vendas coincidem: {'✅ SIM' if sales_match else '❌ NÃO'}")
    print(f"   Produtos coincidem: {'✅ SIM' if products_match else '❌ NÃO'}")

    if sales_match and products_match:
        print("🎉 DADOS REAIS CONFIRMADOS! A API está buscando do banco.")
    else:
        print("⚠️ POSSÍVEL PROBLEMA: API pode estar usando dados mock.")


async def main():
    print("🚀 VERIFICAÇÃO COMPLETA - DASHBOARD DATA")
    print("=" * 50)

    # 1. Verificar banco de dados
    db_connected, db_counts = verify_database_connection()

    if not db_connected:
        print("❌ Não foi possível conectar ao banco. Verifique a configuração.")
        return

    # 2. Testar API
    api_results = await test_api_endpoints()

    if not api_results:
        print("❌ Não foi possível testar a API. Verifique se está rodando.")
        return

    # 3. Comparar resultados
    compare_db_vs_api(db_counts, api_results)

    # 4. Salvar relatório
    report = {
        "timestamp": datetime.now().isoformat(),
        "database": {"connected": db_connected, "counts": db_counts},
        "api": api_results,
    }

    with open("dashboard_verification_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n📄 Relatório salvo em: dashboard_verification_report.json")
    print("\n🔚 Verificação concluída!")


if __name__ == "__main__":
    asyncio.run(main())
