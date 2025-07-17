"""
Script para popular o banco de dados com dados de exemplo
"""
import random
from datetime import datetime, timedelta

from app.core.security import get_password_hash
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.models.customer import Customer
from app.infrastructure.database.models.product import Category, Product
from app.infrastructure.database.models.sale import (
    PaymentMethod,
    Sale,
    SaleItem,
    SaleStatus,
)
from app.infrastructure.database.models.user import User, UserRole


def create_sample_data():
    """Criar dados de exemplo no banco"""
    db_gen = get_db()
    db = next(db_gen)

    try:
        # Criar usuário admin se não existir
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@supermarket.com",
                full_name="Administrador",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN,
                is_active=True,
            )
            db.add(admin_user)
            db.commit()
            print("✓ Usuário admin criado")

        # Criar operador se não existir
        operator_user = db.query(User).filter(User.username == "operador").first()
        if not operator_user:
            operator_user = User(
                username="operador",
                email="operador@supermarket.com",
                full_name="João Silva",
                hashed_password=get_password_hash("op123"),
                role=UserRole.CASHIER,
                is_active=True,
            )
            db.add(operator_user)
            db.commit()
            print("✓ Usuário operador criado")

        # Criar categorias se não existirem
        categories_data = [
            {"name": "Bebidas", "description": "Refrigerantes, sucos, águas"},
            {"name": "Laticínios", "description": "Leite, queijo, iogurte"},
            {"name": "Padaria", "description": "Pães, bolos, biscoitos"},
            {"name": "Limpeza", "description": "Produtos de limpeza"},
            {"name": "Higiene", "description": "Produtos de higiene pessoal"},
        ]

        categories = []
        for cat_data in categories_data:
            category = (
                db.query(Category).filter(Category.name == cat_data["name"]).first()
            )
            if not category:
                category = Category(**cat_data)
                db.add(category)
                db.commit()
                print(f"✓ Categoria {cat_data['name']} criada")
            categories.append(category)

        # Criar produtos se não existirem
        products_data = [
            {
                "name": "Coca-Cola 2L",
                "barcode": "7894900011517",
                "category_id": categories[0].id,
                "price": 8.99,
                "cost_price": 6.50,
                "stock_quantity": 50,
                "min_stock_level": 10,
            },
            {
                "name": "Leite Integral 1L",
                "barcode": "7891000100103",
                "category_id": categories[1].id,
                "price": 4.50,
                "cost_price": 3.20,
                "stock_quantity": 30,
                "min_stock_level": 5,
            },
            {
                "name": "Pão Francês (kg)",
                "barcode": "7890000000001",
                "category_id": categories[2].id,
                "price": 12.90,
                "cost_price": 8.00,
                "stock_quantity": 25,
                "min_stock_level": 5,
                "requires_weighing": True,
            },
            {
                "name": "Detergente Ypê",
                "barcode": "7896098900234",
                "category_id": categories[3].id,
                "price": 2.49,
                "cost_price": 1.80,
                "stock_quantity": 40,
                "min_stock_level": 8,
            },
            {
                "name": "Shampoo Seda 400ml",
                "barcode": "7891150000456",
                "category_id": categories[4].id,
                "price": 15.90,
                "cost_price": 11.20,
                "stock_quantity": 20,
                "min_stock_level": 3,
            },
            {
                "name": "Água Mineral 1,5L",
                "barcode": "7894900555001",
                "category_id": categories[0].id,
                "price": 2.99,
                "cost_price": 1.50,
                "stock_quantity": 60,
                "min_stock_level": 15,
            },
            {
                "name": "Queijo Mussarela (kg)",
                "barcode": "7891234567890",
                "category_id": categories[1].id,
                "price": 32.90,
                "cost_price": 24.00,
                "stock_quantity": 8,
                "min_stock_level": 2,
                "requires_weighing": True,
            },
        ]

        products = []
        for prod_data in products_data:
            product = (
                db.query(Product)
                .filter(Product.barcode == prod_data["barcode"])
                .first()
            )
            if not product:
                product = Product(**prod_data)
                db.add(product)
                db.commit()
                print(f"✓ Produto {prod_data['name']} criado")
            products.append(product)

        # Criar clientes se não existirem
        customers_data = [
            {
                "name": "Maria Silva",
                "email": "maria@email.com",
                "phone": "(11) 99999-1111",
            },
            {
                "name": "João Santos",
                "email": "joao@email.com",
                "phone": "(11) 99999-2222",
            },
            {"name": "Ana Costa", "email": "ana@email.com", "phone": "(11) 99999-3333"},
        ]

        customers = []
        for cust_data in customers_data:
            customer = (
                db.query(Customer).filter(Customer.email == cust_data["email"]).first()
            )
            if not customer:
                customer = Customer(**cust_data)
                db.add(customer)
                db.commit()
                print(f"✓ Cliente {cust_data['name']} criado")
            customers.append(customer)

        # Criar vendas de exemplo dos últimos 30 dias
        print("\n🔄 Criando vendas de exemplo...")
        payment_methods = [
            PaymentMethod.CASH,
            PaymentMethod.DEBIT_CARD,
            PaymentMethod.CREDIT_CARD,
            PaymentMethod.PIX,
        ]

        # Verificar se já existem vendas
        existing_sales = db.query(Sale).count()
        if existing_sales > 0:
            print(
                f"⚠️  Já existem {existing_sales} vendas no banco. Pulando criação de vendas de exemplo."
            )
        else:
            sales_created = 0
            for day_offset in range(30):  # Últimos 30 dias
                sale_date = datetime.now() - timedelta(days=day_offset)

                # Criar 3-8 vendas por dia
                daily_sales = random.randint(3, 8)
                for _ in range(daily_sales):
                    # Criar venda
                    sale = Sale(
                        user_id=random.choice([admin_user.id, operator_user.id]),
                        customer_id=random.choice([None] + [c.id for c in customers]),
                        payment_method=random.choice(payment_methods),
                        status=SaleStatus.COMPLETED,
                        created_at=sale_date.replace(
                            hour=random.randint(8, 20), minute=random.randint(0, 59)
                        ),
                    )

                    # Adicionar itens à venda (1-5 produtos por venda)
                    num_items = random.randint(1, 5)
                    selected_products = random.sample(
                        products, min(num_items, len(products))
                    )

                    subtotal = 0
                    sale_items = []

                    for product in selected_products:
                        if product.requires_weighing:
                            quantity = round(random.uniform(0.2, 2.0), 3)  # 200g a 2kg
                            weight = quantity
                        else:
                            quantity = random.randint(1, 4)
                            weight = None

                        unit_price = product.price
                        original_total = quantity * unit_price

                        # Aplicar desconto aleatório em 20% dos itens
                        discount = (
                            round(random.uniform(0.10, 0.50), 2)
                            if random.random() < 0.2
                            else 0
                        )
                        discount_applied = original_total * discount
                        final_total = original_total - discount_applied

                        sale_item = SaleItem(
                            product_id=product.id,
                            quantity=quantity,
                            weight=weight,
                            unit_price=unit_price,
                            original_total_price=original_total,
                            discount_applied=discount_applied,
                            final_total_price=final_total,
                        )
                        sale_items.append(sale_item)
                        subtotal += final_total

                    # Aplicar desconto geral em 10% das vendas
                    general_discount = (
                        round(subtotal * 0.05, 2) if random.random() < 0.1 else 0
                    )

                    sale.subtotal_amount = subtotal
                    sale.discount_amount = general_discount
                    sale.final_amount = subtotal - general_discount

                    db.add(sale)
                    db.flush()  # Para obter o ID da venda

                    # Adicionar itens à venda
                    for item in sale_items:
                        item.sale_id = sale.id
                        db.add(item)

                    sales_created += 1

            db.commit()
            print(f"✓ {sales_created} vendas de exemplo criadas!")

        print("\n✅ Dados de exemplo criados com sucesso!")
        print("\nResumo:")
        print(f"• Usuários: {db.query(User).count()}")
        print(f"• Categorias: {db.query(Category).count()}")
        print(f"• Produtos: {db.query(Product).count()}")
        print(f"• Clientes: {db.query(Customer).count()}")
        print(f"• Vendas: {db.query(Sale).count()}")
        print(
            f"• Vendas completed: {db.query(Sale).filter(Sale.status == SaleStatus.COMPLETED).count()}"
        )

    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao criar dados: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_sample_data()
