"""
Repositório de vendas
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session, joinedload

from app.infrastructure.database.models.product import Product
from app.infrastructure.database.models.sale import Sale, SaleItem, SaleStatus
from app.infrastructure.database.models.user import User


class SaleRepository:
    """Repositório para operações com vendas"""

    def __init__(self, db: Session):
        self.db = db

    def create_sale(self, sale_data: Dict[str, Any]) -> Sale:
        items_data = sale_data.pop("items", [])
        db_sale = Sale(**sale_data)
        db_sale.status = SaleStatus.COMPLETED
        self.db.add(db_sale)
        self.db.flush()
        for item_data in items_data:
            item_data["sale_id"] = db_sale.id
            db_item = SaleItem(**item_data)
            self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_sale)
        return db_sale

    def get_by_id(self, sale_id: int) -> Optional[Sale]:
        return (
            self.db.query(Sale)
            .options(
                joinedload(Sale.items).joinedload(SaleItem.product),
                joinedload(Sale.user),
                joinedload(Sale.customer),
            )
            .filter(Sale.id == sale_id)
            .first()
        )

    def get_sales_by_filters(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        user_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Sale]:
        query = self.db.query(Sale).options(
            joinedload(Sale.user), joinedload(Sale.items)
        )
        if start_date:
            query = query.filter(func.date(Sale.created_at) >= start_date)
        if end_date:
            query = query.filter(func.date(Sale.created_at) <= end_date)
        if user_id:
            query = query.filter(Sale.user_id == user_id)
        if status:
            query = query.filter(Sale.status == status)
        return query.order_by(desc(Sale.created_at)).offset(skip).limit(limit).all()

    def cancel_sale(self, sale_id: int, user_id: int) -> bool:
        sale = self.get_by_id(sale_id)
        if not sale:
            return False
        if sale.status == SaleStatus.CANCELLED:
            return False
        for item in sale.items:
            product = (
                self.db.query(Product).filter(Product.id == item.product_id).first()
            )
            if product:
                quantity_to_return = item.weight if item.weight else item.quantity
                product.stock_quantity += quantity_to_return
        sale.status = SaleStatus.CANCELLED
        self.db.commit()
        return True

    def get_sales_summary(self, start_date: date, end_date: date) -> Dict[str, Any]:
        sales = (
            self.db.query(Sale)
            .filter(
                and_(
                    func.date(Sale.created_at) >= start_date,
                    func.date(Sale.created_at) <= end_date,
                    Sale.status == SaleStatus.COMPLETED,
                )
            )
            .all()
        )
        total_sales = len(sales)
        total_revenue = sum(sale.final_amount for sale in sales)
        total_items = sum(len(sale.items) for sale in sales)
        total_discount = sum(
            sale.discount_amount + sale.bulk_discount_amount for sale in sales
        )
        return {
            "total_sales": total_sales,
            "total_revenue": total_revenue,
            "total_items": total_items,
            "total_discount": total_discount,
            "average_ticket": total_revenue / total_sales if total_sales > 0 else 0,
        }
