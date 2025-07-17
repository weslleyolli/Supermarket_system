from app.infrastructure.database.connection import get_db
from app.infrastructure.database.models.sale import Sale


def debug_sales_completed(db):
    sales = db.query(Sale).filter(Sale.status == "completed").all()
    for sale in sales:
        print(
            f"ID: {sale.id}, Status: {sale.status}, Valor: {sale.final_amount}, Criado em: {sale.created_at}"
        )
    if not sales:
        print("Nenhuma venda com status 'completed' encontrada.")


if __name__ == "__main__":
    db_gen = get_db()
    db = next(db_gen)
    debug_sales_completed(db)
    db_gen.close()
