from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

from app.infrastructure.database.models.product import Product
from app.infrastructure.database.models.stock import (
    MovementType,
    StockMovement,
    Supplier,
)


class StockService:
    def __init__(self, db: Session):
        self.db = db

    # ==================== MOVIMENTAÇÕES DE ESTOQUE ====================

    def create_stock_movement(
        self,
        product_id: int,
        movement_type: MovementType,
        quantity: int,
        user_id: int,
        unit_cost: Optional[Decimal] = None,
        reason: Optional[str] = None,
        notes: Optional[str] = None,
        sale_id: Optional[int] = None,
        supplier_id: Optional[int] = None,
    ) -> StockMovement:
        """Criar movimentação de estoque"""

        # Buscar produto atual
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError(f"Produto {product_id} não encontrado")

        previous_quantity = product.stock_quantity

        # Calcular nova quantidade baseada no tipo de movimento
        if movement_type in [MovementType.ENTRADA, MovementType.DEVOLUCAO]:
            new_quantity = previous_quantity + quantity
        elif movement_type in [MovementType.SAIDA, MovementType.PERDA]:
            new_quantity = previous_quantity - quantity
            if new_quantity < 0:
                raise ValueError(
                    f"Estoque insuficiente. Atual: {previous_quantity}, Tentativa: {quantity}"
                )
        elif movement_type == MovementType.AJUSTE:
            new_quantity = quantity  # Para ajustes, quantity é o valor final
            quantity = (
                new_quantity - previous_quantity
            )  # Ajustar a quantidade da movimentação
        else:
            new_quantity = previous_quantity

        # Calcular custo total
        total_cost = None
        if unit_cost and quantity:
            total_cost = unit_cost * abs(quantity)

        # Criar movimentação
        movement = StockMovement(
            product_id=product_id,
            movement_type=movement_type,
            quantity=abs(quantity),
            previous_quantity=previous_quantity,
            new_quantity=new_quantity,
            unit_cost=unit_cost,
            total_cost=total_cost,
            reason=reason,
            notes=notes,
            user_id=user_id,
            sale_id=sale_id,
            supplier_id=supplier_id,
        )

        # Atualizar quantidade do produto
        product.stock_quantity = new_quantity

        # Atualizar datas
        if movement_type == MovementType.ENTRADA:
            product.last_purchase_date = datetime.now()
        elif movement_type == MovementType.SAIDA:
            product.last_sale_date = datetime.now()

        self.db.add(movement)
        self.db.commit()
        self.db.refresh(movement)

        return movement

    def get_stock_movements(
        self,
        product_id: Optional[int] = None,
        movement_type: Optional[MovementType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[StockMovement]:
        """Buscar movimentações de estoque"""

        query = self.db.query(StockMovement)

        if product_id:
            query = query.filter(StockMovement.product_id == product_id)

        if movement_type:
            query = query.filter(StockMovement.movement_type == movement_type)

        if start_date:
            query = query.filter(StockMovement.created_at >= start_date)

        if end_date:
            query = query.filter(StockMovement.created_at <= end_date)

        return (
            query.order_by(desc(StockMovement.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    # ==================== ALERTAS DE ESTOQUE ====================

    def get_low_stock_alerts(self) -> List[Dict[str, Any]]:
        """Obter produtos com estoque baixo"""

        products = (
            self.db.query(Product)
            .filter(
                and_(
                    Product.is_active, Product.stock_quantity <= Product.min_stock_level
                )
            )
            .all()
        )

        alerts = []
        for product in products:
            alert_level = "critical" if product.stock_quantity == 0 else "warning"
            if product.stock_quantity <= (product.min_stock_level * 0.5):
                alert_level = "critical"

            alerts.append(
                {
                    "product_id": product.id,
                    "product_name": product.name,
                    "current_quantity": product.stock_quantity,
                    "min_stock": product.min_stock_level,
                    "reorder_point": product.reorder_point,
                    "alert_level": alert_level,
                    "days_without_stock": self._calculate_days_without_stock(product),
                }
            )

        return sorted(alerts, key=lambda x: x["current_quantity"])

    def _calculate_days_without_stock(self, product: Product) -> Optional[int]:
        """Calcular quantos dias até ficar sem estoque"""
        if product.stock_quantity == 0:
            return 0

        # Calcular média de vendas dos últimos 30 dias
        thirty_days_ago = datetime.now() - timedelta(days=30)

        movements = (
            self.db.query(StockMovement)
            .filter(
                and_(
                    StockMovement.product_id == product.id,
                    StockMovement.movement_type == MovementType.SAIDA,
                    StockMovement.created_at >= thirty_days_ago,
                )
            )
            .all()
        )

        if not movements:
            return None

        total_sold = sum(m.quantity for m in movements)
        avg_daily_sales = total_sold / 30

        if avg_daily_sales == 0:
            return None

        return int(product.stock_quantity / avg_daily_sales)

    # ==================== RELATÓRIOS DE ESTOQUE ====================

    def get_stock_report(self) -> Dict[str, Any]:
        """Relatório geral de estoque"""

        # Estatísticas gerais
        total_products = self.db.query(Product).filter(Product.is_active).count()

        products_out_of_stock = (
            self.db.query(Product)
            .filter(and_(Product.is_active, Product.stock_quantity == 0))
            .count()
        )

        low_stock_count = len(self.get_low_stock_alerts())

        # Valor total do estoque
        total_stock_value = (
            self.db.query(func.sum(Product.stock_quantity * Product.cost_price))
            .filter(and_(Product.is_active, Product.cost_price.isnot(None)))
            .scalar()
            or 0
        )

        # Contar movimentações de hoje
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        movements_today = (
            self.db.query(StockMovement)
            .filter(StockMovement.created_at >= today_start)
            .count()
        )

        # Contar movimentações da semana
        week_start = today_start - timedelta(days=7)
        movements_week = (
            self.db.query(StockMovement)
            .filter(StockMovement.created_at >= week_start)
            .count()
        )

        # Buscar produtos com informações básicas para o relatório
        products_query = self.db.query(Product).filter(Product.is_active).all()

        # Montar items do relatório
        report_items = []
        for product in products_query:
            stock_value = float(
                (product.stock_quantity or 0) * (product.cost_price or 0)
            )

            # Determinar status
            if product.stock_quantity == 0:
                status = "out_of_stock"
            elif (
                product.min_stock_level
                and product.stock_quantity <= product.min_stock_level
            ):
                status = "low_stock"
            elif product.max_stock and product.stock_quantity >= product.max_stock:
                status = "overstock"
            else:
                status = "ok"

            report_items.append(
                {
                    "product_id": product.id,
                    "product_name": product.name,
                    "barcode": product.barcode,
                    "category_name": "Categoria Geral",  # Simplificado por enquanto
                    "supplier_name": None,  # Pode ser implementado depois
                    "current_stock": int(product.stock_quantity or 0),
                    "min_stock": int(product.min_stock_level or 0),
                    "max_stock": int(product.max_stock) if product.max_stock else None,
                    "reorder_point": None,  # Pode ser calculado depois
                    "cost_price": float(product.cost_price)
                    if product.cost_price
                    else None,
                    "sale_price": float(product.price),
                    "stock_value": stock_value,
                    "location": None,  # Pode ser implementado depois
                    "last_movement_date": None,  # Pode ser implementado depois
                    "movement_count": 0,  # Pode ser implementado depois
                    "status": status,
                }
            )

        # Montar summary
        summary = {
            "total_products": total_products,
            "total_stock_value": float(total_stock_value),
            "low_stock_items": low_stock_count,
            "out_of_stock_items": products_out_of_stock,
            "overstocked_items": 0,  # Implementar depois
            "total_movements_today": movements_today,
            "total_movements_week": movements_week,
        }

        return {
            "summary": summary,
            "items": report_items,
            "generated_at": datetime.now(),
        }

    def _calculate_stock_turnover(self) -> float:
        """Calcular giro de estoque"""
        # Implementação simplificada do giro de estoque
        thirty_days_ago = datetime.now() - timedelta(days=30)

        total_sales_cost = (
            self.db.query(func.sum(StockMovement.total_cost))
            .filter(
                and_(
                    StockMovement.movement_type == MovementType.SAIDA,
                    StockMovement.created_at >= thirty_days_ago,
                    StockMovement.total_cost.isnot(None),
                )
            )
            .scalar()
            or 0
        )

        total_stock_value = (
            self.db.query(func.sum(Product.stock_quantity * Product.cost_price))
            .filter(and_(Product.is_active, Product.cost_price.isnot(None)))
            .scalar()
            or 1
        )

        # Giro mensal
        turnover = (
            float(total_sales_cost) / float(total_stock_value)
            if total_stock_value > 0
            else 0
        )
        return round(turnover, 2)

    # ==================== GESTÃO DE FORNECEDORES ====================

    def create_supplier(
        self,
        name: str,
        company_name: Optional[str] = None,
        document: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        contact_person: Optional[str] = None,
    ) -> Supplier:
        """Criar fornecedor"""

        supplier = Supplier(
            name=name,
            company_name=company_name,
            document=document,
            email=email,
            phone=phone,
            address=address,
            contact_person=contact_person,
        )

        self.db.add(supplier)
        self.db.commit()
        self.db.refresh(supplier)

        return supplier

    def get_suppliers(self, skip: int = 0, limit: int = 100) -> List[Supplier]:
        """Listar fornecedores"""
        return (
            self.db.query(Supplier)
            .filter(Supplier.is_active)
            .offset(skip)
            .limit(limit)
            .all()
        )

    # ==================== ENTRADA DE ESTOQUE ====================

    def stock_entry(
        self,
        product_id: int,
        quantity: int,
        unit_cost: Decimal,
        user_id: int,
        supplier_id: Optional[int] = None,
        reason: str = "Entrada de estoque",
        notes: Optional[str] = None,
    ) -> StockMovement:
        """Entrada de estoque"""

        return self.create_stock_movement(
            product_id=product_id,
            movement_type=MovementType.ENTRADA,
            quantity=quantity,
            user_id=user_id,
            unit_cost=unit_cost,
            reason=reason,
            notes=notes,
            supplier_id=supplier_id,
        )

    def stock_adjustment(
        self,
        product_id: int,
        new_quantity: int,
        user_id: int,
        reason: str = "Ajuste de estoque",
        notes: Optional[str] = None,
    ) -> StockMovement:
        """Ajuste de estoque"""

        return self.create_stock_movement(
            product_id=product_id,
            movement_type=MovementType.AJUSTE,
            quantity=new_quantity,
            user_id=user_id,
            reason=reason,
            notes=notes,
        )
