"""
Script para adicionar vendas de exemplo com status completed
"""
import random
from datetime import datetime, timedelta

from app.infrastructure.database.connection import get_db
from app.infrastructure.database.models.customer import Customer
from app.infrastructure.database.models.product import Product
from app.infrastructure.database.models.sale import (
    PaymentMethod,
    Sale,
    SaleItem,
    SaleStatus,
)
from app.infrastructure.database.models.user import User


def add_completed_sales():
    """Adicionar vendas com status completed"""
    db_gen = get_db()
    db = next(db_gen)

    try:
        # Buscar usuários e produtos existentes
        users = db.query(User).all()
        products = db.query(Product).all()
        customers = db.query(Customer).all()

        if not users or not products:
            print("❌ É necessário ter usuários e produtos no banco primeiro!")
            return

        print(f"🔄 Adicionando vendas completed...")
        payment_methods = [
            PaymentMethod.CASH,
            PaymentMethod.DEBIT_CARD,
            PaymentMethod.CREDIT_CARD,
            PaymentMethod.PIX,
        ]

        sales_created = 0
        for day_offset in range(7):  # Últimos 7 dias
            sale_date = datetime.now() - timedelta(days=day_offset)

            # Criar 2-5 vendas por dia
            daily_sales = random.randint(2, 5)
            for _ in range(daily_sales):
                # Criar venda
                sale = Sale(
                    user_id=random.choice([u.id for u in users]),
                    customer_id=random.choice([None] + [c.id for c in customers]),
                    payment_method=random.choice(payment_methods),
                    status=SaleStatus.COMPLETED,
                    created_at=sale_date.replace(
                        hour=random.randint(8, 20), minute=random.randint(0, 59)
                    ),
                )

                # Adicionar itens à venda (1-3 produtos por venda)
                num_items = random.randint(1, 3)
                selected_products = random.sample(
                    products, min(num_items, len(products))
                )

                subtotal = 0
                sale_items = []

                for product in selected_products:
                    if product.requires_weighing:
                        quantity = round(random.uniform(0.2, 1.5), 3)  # 200g a 1.5kg
                        weight = quantity
                    else:
                        quantity = random.randint(1, 3)
                        weight = None

                    unit_price = product.price
                    original_total = quantity * unit_price

                    # Aplicar desconto aleatório em 10% dos itens
                    discount = (
                        round(random.uniform(0.05, 0.20), 2)
                        if random.random() < 0.1
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

                # Calcular valores finais
                sale.subtotal_amount = subtotal
                sale.discount_amount = 0
                sale.final_amount = subtotal

                db.add(sale)
                db.flush()  # Para obter o ID da venda

                # Adicionar itens à venda
                for item in sale_items:
                    item.sale_id = sale.id
                    db.add(item)

                sales_created += 1

        db.commit()
        print(f"✅ {sales_created} vendas completed adicionadas!")

        # Mostrar resumo final
        total_sales = db.query(Sale).count()
        completed_sales = (
            db.query(Sale).filter(Sale.status == SaleStatus.COMPLETED).count()
        )
        print(f"\n📊 Resumo:")
        print(f"• Total de vendas: {total_sales}")
        print(f"• Vendas completed: {completed_sales}")

    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao criar vendas: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    add_completed_sales()
