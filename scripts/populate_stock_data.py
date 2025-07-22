#!/usr/bin/env python3
"""
Script para popular dados de exemplo do sistema de estoque
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.infrastructure.database.models.product import Product

# Importar apenas os modelos essenciais para evitar problemas de relacionamento
from app.infrastructure.database.models.stock import (
    MovementType,
    PurchaseOrder,
    PurchaseOrderItem,
    StockMovement,
    Supplier,
)
from app.infrastructure.database.models.user import User


def populate_stock_data():
    """Popular dados de exemplo para o sistema de estoque"""
    print("🔄 Populando dados de exemplo do sistema de estoque...")

    try:
        # Conectar ao banco
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()

        # 1. CRIAR FORNECEDORES
        print("📦 Criando fornecedores...")
        suppliers_data = [
            {
                "name": "Distribuidora Central Ltda",
                "company_name": "Central Distribuidora de Alimentos",
                "document": "12.345.678/0001-90",
                "email": "vendas@central.com.br",
                "phone": "(11) 1234-5678",
                "address": "Rua das Industrias, 123 - São Paulo, SP",
                "contact_person": "João Silva",
            },
            {
                "name": "FreshFruit Fornecedores",
                "company_name": "FreshFruit Comércio de Frutas",
                "document": "98.765.432/0001-10",
                "email": "contato@freshfruit.com.br",
                "phone": "(11) 9876-5432",
                "address": "Av. dos Produtores, 456 - São Paulo, SP",
                "contact_person": "Maria Santos",
            },
            {
                "name": "Padaria & Cia",
                "company_name": "Panificadora Moderna Ltda",
                "document": "11.222.333/0001-44",
                "email": "vendas@padariaecia.com.br",
                "phone": "(11) 5555-1234",
                "address": "Rua do Trigo, 789 - São Paulo, SP",
                "contact_person": "Pedro Oliveira",
            },
            {
                "name": "Bebidas Premium",
                "company_name": "Premium Bebidas e Distribuição",
                "document": "33.444.555/0001-77",
                "email": "comercial@bebidaspremium.com.br",
                "phone": "(11) 7777-8888",
                "address": "Estrada das Bebidas, 321 - São Paulo, SP",
                "contact_person": "Ana Costa",
            },
        ]

        suppliers = []
        for supplier_data in suppliers_data:
            # Verificar se já existe
            existing = (
                db.query(Supplier)
                .filter(Supplier.document == supplier_data["document"])
                .first()
            )
            if not existing:
                supplier = Supplier(**supplier_data)
                db.add(supplier)
                suppliers.append(supplier)

        db.commit()
        print(f"✅ {len(suppliers_data)} fornecedores criados!")

        # Buscar todos os fornecedores
        all_suppliers = db.query(Supplier).all()

        # 2. ATUALIZAR PRODUTOS COM FORNECEDORES E DADOS DE ESTOQUE
        print("🏷️ Atualizando produtos com dados de estoque...")
        products = db.query(Product).all()

        for i, product in enumerate(products):
            # Atribuir fornecedor baseado na categoria
            if "Frutas" in product.category.name or "Verduras" in product.category.name:
                supplier = next(
                    (s for s in all_suppliers if "FreshFruit" in s.name),
                    all_suppliers[0],
                )
            elif "Padaria" in product.category.name or "Pães" in product.category.name:
                supplier = next(
                    (s for s in all_suppliers if "Padaria" in s.name), all_suppliers[0]
                )
            elif "Bebidas" in product.category.name:
                supplier = next(
                    (s for s in all_suppliers if "Bebidas" in s.name), all_suppliers[0]
                )
            else:
                supplier = next(
                    (s for s in all_suppliers if "Central" in s.name), all_suppliers[0]
                )

            # Atualizar dados do produto
            product.supplier_id = supplier.id
            product.profit_margin = 25.0 + (i % 20)  # 25% a 45%
            product.weight = 0.1 + (i % 10) * 0.1  # 0.1kg a 1.0kg
            product.dimensions = f"{20 + i % 15}x{15 + i % 10}x{8 + i % 5} cm"
            product.location = f"A{(i % 5) + 1}-{(i % 10) + 1:02d}"
            product.reorder_point = max(5, product.min_stock_level)
            product.max_stock = product.min_stock_level * 5

        db.commit()
        print(f"✅ {len(products)} produtos atualizados!")

        # 3. CRIAR PEDIDOS DE COMPRA
        print("📝 Criando pedidos de compra...")

        # Buscar usuário admin
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = db.query(User).first()

        if admin_user:
            purchase_orders_data = [
                {
                    "supplier": all_suppliers[0],
                    "order_number": "PO-2024-001",
                    "status": "delivered",
                    "products": products[:3],
                    "quantities": [50, 30, 25],
                    "unit_costs": [2.50, 1.80, 3.20],
                },
                {
                    "supplier": all_suppliers[1],
                    "order_number": "PO-2024-002",
                    "status": "confirmed",
                    "products": products[3:6],
                    "quantities": [40, 35, 20],
                    "unit_costs": [1.90, 2.10, 4.50],
                },
                {
                    "supplier": all_suppliers[2],
                    "order_number": "PO-2024-003",
                    "status": "pending",
                    "products": products[6:9],
                    "quantities": [60, 45, 30],
                    "unit_costs": [1.50, 2.80, 3.90],
                },
            ]

            orders_created = 0
            for order_data in purchase_orders_data:
                # Verificar se já existe
                existing = (
                    db.query(PurchaseOrder)
                    .filter(PurchaseOrder.order_number == order_data["order_number"])
                    .first()
                )

                if not existing:
                    # Calcular valor total
                    total_amount = sum(
                        qty * cost
                        for qty, cost in zip(
                            order_data["quantities"], order_data["unit_costs"]
                        )
                    )

                    # Criar pedido
                    order = PurchaseOrder(
                        supplier_id=order_data["supplier"].id,
                        order_number=order_data["order_number"],
                        status=order_data["status"],
                        total_amount=Decimal(str(total_amount)),
                        user_id=admin_user.id,
                        order_date=datetime.utcnow()
                        - timedelta(days=orders_created * 2),
                        expected_delivery=datetime.utcnow()
                        + timedelta(days=7 - orders_created),
                        delivery_date=datetime.utcnow() - timedelta(days=1)
                        if order_data["status"] == "delivered"
                        else None,
                    )

                    db.add(order)
                    db.flush()  # Para obter o ID

                    # Criar itens do pedido
                    for product, qty, cost in zip(
                        order_data["products"],
                        order_data["quantities"],
                        order_data["unit_costs"],
                    ):
                        item = PurchaseOrderItem(
                            purchase_order_id=order.id,
                            product_id=product.id,
                            quantity_ordered=qty,
                            quantity_received=qty
                            if order_data["status"] == "delivered"
                            else 0,
                            unit_cost=Decimal(str(cost)),
                            total_cost=Decimal(str(qty * cost)),
                        )
                        db.add(item)

                    orders_created += 1

            db.commit()
            print(f"✅ {orders_created} pedidos de compra criados!")

            # 4. CRIAR MOVIMENTAÇÕES DE ESTOQUE
            print("📊 Criando movimentações de estoque...")

            movements_created = 0
            base_date = datetime.utcnow() - timedelta(days=30)

            for i, product in enumerate(products[:10]):  # Apenas primeiros 10 produtos
                # Movimentação de entrada inicial
                initial_stock = 20 + (i * 5)

                entry_movement = StockMovement(
                    product_id=product.id,
                    movement_type=MovementType.ENTRADA,
                    quantity=initial_stock,
                    previous_quantity=0,
                    new_quantity=initial_stock,
                    unit_cost=Decimal(str(2.00 + i * 0.5)),
                    total_cost=Decimal(str(initial_stock * (2.00 + i * 0.5))),
                    reason="Estoque inicial",
                    notes="Carga inicial do sistema",
                    user_id=admin_user.id,
                    supplier_id=product.supplier_id,
                    created_at=base_date + timedelta(days=i),
                )
                db.add(entry_movement)

                # Atualizar estoque do produto
                product.stock_quantity = initial_stock
                movements_created += 1

                # Algumas movimentações de saída (vendas)
                if i % 3 == 0:  # A cada 3 produtos
                    sale_quantity = 5 + (i % 8)

                    sale_movement = StockMovement(
                        product_id=product.id,
                        movement_type=MovementType.SAIDA,
                        quantity=sale_quantity,
                        previous_quantity=initial_stock,
                        new_quantity=initial_stock - sale_quantity,
                        reason="Venda",
                        notes="Saída por venda no PDV",
                        user_id=admin_user.id,
                        created_at=base_date + timedelta(days=i + 5),
                    )
                    db.add(sale_movement)

                    # Atualizar estoque
                    product.stock_quantity = initial_stock - sale_quantity
                    product.last_sale_date = sale_movement.created_at
                    movements_created += 1

                # Alguns ajustes de estoque
                if i % 5 == 0:  # A cada 5 produtos
                    adjustment_movement = StockMovement(
                        product_id=product.id,
                        movement_type=MovementType.AJUSTE,
                        quantity=int(product.stock_quantity) + 2,  # Ajustar para +2
                        previous_quantity=int(product.stock_quantity),
                        new_quantity=int(product.stock_quantity) + 2,
                        reason="Ajuste de inventário",
                        notes="Correção após contagem física",
                        user_id=admin_user.id,
                        created_at=base_date + timedelta(days=i + 10),
                    )
                    db.add(adjustment_movement)

                    # Atualizar estoque
                    product.stock_quantity = int(product.stock_quantity) + 2
                    movements_created += 1

            db.commit()
            print(f"✅ {movements_created} movimentações de estoque criadas!")

        db.close()

        print("\n🎉 Dados de estoque populados com sucesso!")
        print("\n📋 Resumo:")
        print(f"  • {len(suppliers_data)} fornecedores")
        print(f"  • {len(products)} produtos atualizados")
        print(f"  • {orders_created} pedidos de compra")
        print(f"  • {movements_created} movimentações de estoque")
        print("\n🚀 Sistema de estoque pronto para uso!")

        return True

    except Exception as e:
        print(f"❌ Erro ao popular dados: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = populate_stock_data()
    if not success:
        sys.exit(1)
