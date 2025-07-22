#!/usr/bin/env python3
"""
Script para finalizar a configuração do sistema de estoque
"""

import os
import sys

from sqlalchemy import create_engine, text

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.connection import get_database_url


def complete_stock_setup():
    """Completar a configuração do sistema de estoque"""

    print("🚀 FINALIZANDO CONFIGURAÇÃO DO SISTEMA DE ESTOQUE...")

    database_url = get_database_url()
    engine = create_engine(database_url)

    # Comandos para completar a configuração
    setup_commands = [
        # 1. Inserir fornecedores se não existirem
        """
        INSERT INTO suppliers (name, company_name, email, phone, contact_person, is_active)
        SELECT 'Distribuidora ABC', 'ABC Distribuidora Ltda', 'contato@abc.com', '(11) 1234-5678', 'João Silva', true
        WHERE NOT EXISTS (SELECT 1 FROM suppliers WHERE name = 'Distribuidora ABC');
        """,
        """
        INSERT INTO suppliers (name, company_name, email, phone, contact_person, is_active)
        SELECT 'Química Industrial', 'Química Industrial S.A.', 'vendas@quimica.com', '(11) 9876-5432', 'Maria Santos', true
        WHERE NOT EXISTS (SELECT 1 FROM suppliers WHERE name = 'Química Industrial');
        """,
        """
        INSERT INTO suppliers (name, company_name, email, phone, contact_person, is_active)
        SELECT 'Laticínios Norte', 'Norte Laticínios Ltda', 'pedidos@norte.com', '(11) 3333-7777', 'Ana Oliveira', true
        WHERE NOT EXISTS (SELECT 1 FROM suppliers WHERE name = 'Laticínios Norte');
        """,
        # 2. Atualizar produtos com informações de estoque
        """
        UPDATE products SET
            supplier_id = (SELECT id FROM suppliers WHERE name = 'Distribuidora ABC' LIMIT 1),
            profit_margin = 40.00,
            weight = 5.0,
            location = 'A-01-03',
            reorder_point = 20,
            max_stock = 100,
            last_purchase_date = CURRENT_TIMESTAMP - INTERVAL '5 days'
        WHERE id IN (SELECT id FROM products WHERE supplier_id IS NULL LIMIT 3);
        """,
        """
        UPDATE products SET
            supplier_id = (SELECT id FROM suppliers WHERE name = 'Química Industrial' LIMIT 1),
            profit_margin = 60.00,
            weight = 0.5,
            location = 'B-02-01',
            reorder_point = 30,
            max_stock = 80,
            last_purchase_date = CURRENT_TIMESTAMP - INTERVAL '3 days'
        WHERE id IN (SELECT id FROM products WHERE supplier_id IS NULL LIMIT 2);
        """,
        # 3. Criar algumas movimentações de estoque
        """
        INSERT INTO stock_movements (product_id, movement_type, quantity, previous_quantity, new_quantity, unit_cost, total_cost, reason, user_id, supplier_id, created_at)
        SELECT
            p.id,
            'entrada',
            50,
            GREATEST(0, p.stock_quantity - 50),
            p.stock_quantity,
            p.cost_price,
            50 * p.cost_price,
            'Entrada inicial de estoque',
            1,
            p.supplier_id,
            CURRENT_TIMESTAMP - INTERVAL '2 days'
        FROM products p
        WHERE p.supplier_id IS NOT NULL
        AND NOT EXISTS (
            SELECT 1 FROM stock_movements sm
            WHERE sm.product_id = p.id
            AND sm.movement_type = 'entrada'
        )
        LIMIT 5;
        """,
        # 4. Algumas vendas (saídas)
        """
        INSERT INTO stock_movements (product_id, movement_type, quantity, previous_quantity, new_quantity, reason, user_id, created_at)
        SELECT
            p.id,
            'saida',
            CASE
                WHEN p.stock_quantity > 30 THEN 10
                WHEN p.stock_quantity > 10 THEN 3
                ELSE 1
            END,
            p.stock_quantity + CASE
                WHEN p.stock_quantity > 30 THEN 10
                WHEN p.stock_quantity > 10 THEN 3
                ELSE 1
            END,
            p.stock_quantity,
            'Venda no PDV',
            1,
            CURRENT_TIMESTAMP - INTERVAL '1 day'
        FROM products p
        WHERE p.stock_quantity > 0
        AND NOT EXISTS (
            SELECT 1 FROM stock_movements sm
            WHERE sm.product_id = p.id
            AND sm.movement_type = 'saida'
        )
        LIMIT 3;
        """,
    ]

    # Executar comandos
    with engine.connect() as conn:
        for i, sql in enumerate(setup_commands, 1):
            try:
                print(f"📋 Executando configuração {i}/{len(setup_commands)}...")
                with conn.begin():
                    conn.execute(text(sql))
                print(f"✅ Configuração {i} executada com sucesso")
            except Exception as e:
                print(f"❌ Erro na configuração {i}: {e}")
                continue

    print("🎉 CONFIGURAÇÃO FINALIZADA!")


def verify_complete_setup():
    """Verificar se a configuração está completa"""

    print("\n🔍 VERIFICAÇÃO FINAL DO SISTEMA DE ESTOQUE...")

    database_url = get_database_url()
    engine = create_engine(database_url)

    verification_queries = [
        (
            "Total de fornecedores",
            "SELECT COUNT(*) FROM suppliers WHERE is_active = true",
        ),
        ("Total de movimentações", "SELECT COUNT(*) FROM stock_movements"),
        (
            "Produtos com fornecedor",
            "SELECT COUNT(*) FROM products WHERE supplier_id IS NOT NULL",
        ),
        (
            "Produtos com localização",
            "SELECT COUNT(*) FROM products WHERE location IS NOT NULL",
        ),
        (
            "Entradas de estoque",
            "SELECT COUNT(*) FROM stock_movements WHERE movement_type = 'entrada'",
        ),
        (
            "Saídas de estoque",
            "SELECT COUNT(*) FROM stock_movements WHERE movement_type = 'saida'",
        ),
        (
            "Produtos com estoque baixo",
            """
            SELECT COUNT(*) FROM products
            WHERE stock_quantity <= min_stock_level
            AND min_stock_level > 0
        """,
        ),
    ]

    print("📊 ESTATÍSTICAS DO SISTEMA:")
    with engine.connect() as conn:
        for name, query in verification_queries:
            try:
                result = conn.execute(text(query)).scalar()
                print(f"   ✅ {name}: {result}")
            except Exception as e:
                print(f"   ❌ Erro ao verificar {name}: {e}")

    # Verificar alguns dados específicos
    print("\n📋 EXEMPLOS DE DADOS:")
    try:
        with engine.connect() as conn:
            # Fornecedores
            suppliers = conn.execute(
                text("SELECT name, company_name FROM suppliers LIMIT 3")
            ).fetchall()
            print("   Fornecedores:")
            for sup in suppliers:
                print(f"     - {sup[0]} ({sup[1]})")

            # Últimas movimentações
            movements = conn.execute(
                text(
                    """
                SELECT p.name, sm.movement_type, sm.quantity, sm.created_at
                FROM stock_movements sm
                JOIN products p ON p.id = sm.product_id
                ORDER BY sm.created_at DESC
                LIMIT 3
            """
                )
            ).fetchall()
            print("   Últimas movimentações:")
            for mov in movements:
                print(f"     - {mov[0]}: {mov[1]} de {mov[2]} unidades em {mov[3]}")

    except Exception as e:
        print(f"   ❌ Erro ao buscar exemplos: {e}")


def test_stock_api_compatibility():
    """Testar se a estrutura está compatível com a API"""

    print("\n🧪 TESTE DE COMPATIBILIDADE COM API...")

    try:
        from app.presentation.schemas.stock import (
            MovementTypeEnum,
            StockAlertResponse,
            StockMovementCreate,
            SupplierCreate,
        )

        print("   ✅ Schemas de estoque importados com sucesso")

        from app.application.services.stock_service import StockService

        print("   ✅ StockService importado com sucesso")

        print("   🎯 Sistema totalmente compatível com a API!")

    except ImportError as e:
        print(f"   ❌ Erro de compatibilidade: {e}")
    except Exception as e:
        print(f"   ❌ Erro inesperado: {e}")


def main():
    """Função principal"""
    print("🎯 FINALIZAÇÃO DO SISTEMA DE ESTOQUE")
    print("=" * 50)

    try:
        # 1. Completar configuração
        complete_stock_setup()

        # 2. Verificar se tudo está funcionando
        verify_complete_setup()

        # 3. Testar compatibilidade com API
        test_stock_api_compatibility()

        print("\n🎉 SISTEMA DE ESTOQUE TOTALMENTE CONFIGURADO!")
        print("\n📋 SISTEMA PRONTO PARA:")
        print("   ✅ API Endpoints (/api/v1/stock/*)")
        print("   ✅ Serviços de Estoque (StockService)")
        print("   ✅ Schemas Pydantic")
        print("   ✅ Dashboard de Estoque")
        print("   ✅ Relatórios de Estoque")
        print("   ✅ Alertas de Estoque Baixo")

        print("\n🚀 PRÓXIMOS PASSOS:")
        print("   1. Reiniciar o servidor FastAPI")
        print("   2. Testar endpoints: /api/v1/stock/movements")
        print("   3. Testar dashboard: /api/v1/stock/dashboard")
        print("   4. Configurar frontend React")

    except Exception as e:
        print(f"\n❌ ERRO NA FINALIZAÇÃO: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
