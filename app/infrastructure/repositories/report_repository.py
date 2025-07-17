from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple

from sqlalchemy import and_, desc, func, text
from sqlalchemy.orm import Session

from app.infrastructure.database.models.product import Category, Product
from app.infrastructure.database.models.sale import Sale, SaleItem
from app.infrastructure.database.models.user import User


class ReportRepository:
    """Repository para relatórios e dashboard"""

    def __init__(self, db: Session):
        self.db = db

    def get_today_kpis(self, target_date: date = None) -> dict:
        """KPIs do dia atual"""
        if not target_date:
            target_date = date.today()
        # Vendas de hoje
        today_sales = (
            self.db.query(func.sum(Sale.final_amount))
            .filter(
                func.date(Sale.created_at) == target_date, Sale.status == "completed"
            )
            .scalar()
            or 0
        )
        # Transações de hoje
        today_transactions = (
            self.db.query(func.count(Sale.id))
            .filter(
                func.date(Sale.created_at) == target_date, Sale.status == "completed"
            )
            .scalar()
            or 0
        )
        # Produtos vendidos hoje
        products_sold = (
            self.db.query(func.sum(SaleItem.quantity))
            .join(Sale)
            .filter(
                func.date(Sale.created_at) == target_date, Sale.status == "completed"
            )
            .scalar()
            or 0
        )
        # Clientes únicos (aproximação por número de vendas)
        customers_served = today_transactions
        # Ticket médio
        average_ticket = (
            today_sales / today_transactions if today_transactions > 0 else 0
        )
        return {
            "today_sales": float(today_sales),
            "today_transactions": int(today_transactions),
            "products_sold": int(products_sold),
            "customers_served": int(customers_served),
            "average_ticket": float(average_ticket),
        }

    def get_period_comparison(self, current_date: date, days_back: int = 30) -> dict:
        """Compara período atual com anterior"""
        # Período atual
        start_current = current_date - timedelta(days=days_back)
        end_current = current_date
        # Período anterior
        start_previous = start_current - timedelta(days=days_back)
        end_previous = start_current
        # Vendas período atual
        current_sales = (
            self.db.query(func.sum(Sale.final_amount))
            .filter(
                Sale.created_at >= start_current,
                Sale.created_at <= end_current,
                Sale.status == "completed",
            )
            .scalar()
            or 0
        )
        # Vendas período anterior
        previous_sales = (
            self.db.query(func.sum(Sale.final_amount))
            .filter(
                Sale.created_at >= start_previous,
                Sale.created_at < end_previous,
                Sale.status == "completed",
            )
            .scalar()
            or 0
        )
        # Calcular tendências
        sales_trend = (
            ((current_sales - previous_sales) / previous_sales * 100)
            if previous_sales > 0
            else 0
        )
        return {
            "sales_trend": float(sales_trend),
            "transactions_trend": 0.0,  # Implementar similar
            "products_trend": 0.0,  # Implementar similar
            "customers_trend": 0.0,  # Implementar similar
            "ticket_trend": 0.0,  # Implementar similar
        }

    def get_top_products(self, limit: int = 10, days_back: int = 30) -> List[dict]:
        """Produtos mais vendidos"""
        start_date = date.today() - timedelta(days=days_back)
        query = (
            self.db.query(
                Product.id,
                Product.name,
                Category.name.label("category_name"),
                func.sum(SaleItem.quantity).label("quantity_sold"),
                func.sum(SaleItem.final_total_price).label("revenue"),
                func.sum(
                    SaleItem.final_total_price
                    - (SaleItem.quantity * Product.cost_price)
                ).label("profit"),
            )
            .join(SaleItem, Product.id == SaleItem.product_id)
            .join(Sale, SaleItem.sale_id == Sale.id)
            .join(Category, Product.category_id == Category.id)
            .filter(Sale.created_at >= start_date, Sale.status == "completed")
            .group_by(Product.id, Product.name, Category.name)
            .order_by(desc("quantity_sold"))
            .limit(limit)
        )
        return [
            {
                "product_id": row.id,
                "product_name": row.name,
                "category_name": row.category_name,
                "quantity_sold": float(row.quantity_sold),
                "revenue": float(row.revenue),
                "profit": float(row.profit),
            }
            for row in query.all()
        ]

    def get_daily_sales(self, days_back: int = 30) -> List[dict]:
        """Vendas diárias"""
        start_date = date.today() - timedelta(days=days_back)
        query = (
            self.db.query(
                func.date(Sale.created_at).label("sale_date"),
                func.sum(Sale.final_amount).label("total_sales"),
                func.count(Sale.id).label("total_transactions"),
                func.sum(func.coalesce(SaleItem.quantity, 0)).label("total_products"),
            )
            .outerjoin(SaleItem, Sale.id == SaleItem.sale_id)
            .filter(Sale.created_at >= start_date, Sale.status == "completed")
            .group_by(func.date(Sale.created_at))
            .order_by("sale_date")
        )
        results = []
        for row in query.all():
            avg_ticket = (
                row.total_sales / row.total_transactions
                if row.total_transactions > 0
                else 0
            )
            results.append(
                {
                    "date": row.sale_date,
                    "total_sales": float(row.total_sales),
                    "total_transactions": int(row.total_transactions),
                    "total_products": int(row.total_products or 0),
                    "average_ticket": float(avg_ticket),
                }
            )
        return results

    def get_stock_alerts(self, limit: int = 50) -> List[dict]:
        """Alertas de estoque baixo"""
        query = (
            self.db.query(
                Product.id,
                Product.name,
                Category.name.label("category_name"),
                Product.stock_quantity,
                Product.min_stock_level,
            )
            .join(Category, Product.category_id == Category.id)
            .filter(
                Product.stock_quantity <= Product.min_stock_level,
                Product.is_active == True,
            )
            .order_by((Product.stock_quantity / Product.min_stock_level))
            .limit(limit)
        )
        results = []
        for row in query.all():
            # Calcular status
            ratio = (
                row.stock_quantity / row.min_stock_level
                if row.min_stock_level > 0
                else 0
            )
            if ratio <= 0.2:
                status = "critical"
            elif ratio <= 0.5:
                status = "low"
            else:
                status = "ok"
            results.append(
                {
                    "product_id": row.id,
                    "product_name": row.name,
                    "category_name": row.category_name,
                    "current_stock": float(row.stock_quantity),
                    "min_stock": float(row.min_stock_level),
                    "stock_status": status,
                    "days_to_stockout": None,  # Implementar cálculo baseado em vendas médias
                }
            )
        return results

    def get_category_performance(self, days_back: int = 30) -> List[dict]:
        """Performance por categoria"""
        start_date = date.today() - timedelta(days=days_back)
        query = (
            self.db.query(
                Category.id,
                Category.name,
                func.sum(SaleItem.final_total_price).label("total_sales"),
                func.sum(SaleItem.quantity).label("total_products"),
                func.avg(
                    (
                        SaleItem.final_total_price
                        - (SaleItem.quantity * Product.cost_price)
                    )
                    / SaleItem.final_total_price
                    * 100
                ).label("profit_margin"),
            )
            .join(Product, Category.id == Product.category_id)
            .join(SaleItem, Product.id == SaleItem.product_id)
            .join(Sale, SaleItem.sale_id == Sale.id)
            .filter(Sale.created_at >= start_date, Sale.status == "completed")
            .group_by(Category.id, Category.name)
            .order_by(desc("total_sales"))
        )
        return [
            {
                "category_id": row.id,
                "category_name": row.name,
                "total_sales": float(row.total_sales),
                "total_products": int(row.total_products),
                "profit_margin": float(row.profit_margin or 0),
                "growth_percentage": 0.0,  # Implementar comparação com período anterior
            }
            for row in query.all()
        ]

    def get_hourly_analysis(self, target_date: date = None) -> List[dict]:
        """Análise por hora do dia"""
        if not target_date:
            target_date = date.today()
        query = (
            self.db.query(
                func.extract("hour", Sale.created_at).label("hour"),
                func.sum(Sale.final_amount).label("sales_amount"),
                func.count(Sale.id).label("transactions_count"),
            )
            .filter(
                func.date(Sale.created_at) == target_date, Sale.status == "completed"
            )
            .group_by(func.extract("hour", Sale.created_at))
            .order_by("hour")
        )
        results = []
        for row in query.all():
            avg_ticket = (
                row.sales_amount / row.transactions_count
                if row.transactions_count > 0
                else 0
            )
            results.append(
                {
                    "hour": int(row.hour),
                    "sales_amount": float(row.sales_amount),
                    "transactions_count": int(row.transactions_count),
                    "average_ticket": float(avg_ticket),
                }
            )
        return results
