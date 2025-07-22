"""
Repositório para operações de estoque
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import and_, asc, desc, func
from sqlalchemy.orm import Session, joinedload

from app.infrastructure.database.models.product import Category, Product
from app.infrastructure.database.models.stock import (
    MovementType,
    PurchaseOrder,
    PurchaseOrderItem,
    StockMovement,
    Supplier,
)
from app.infrastructure.database.models.user import User
from app.presentation.schemas.stock import (
    PurchaseOrderCreate,
    PurchaseOrderUpdate,
    StockMovementCreate,
    StockReportItem,
    StockSummary,
    SupplierCreate,
    SupplierUpdate,
)


class StockRepository:
    """Repositório para operações de estoque"""

    def __init__(self, db: Session):
        self.db = db

    # =================== SUPPLIER OPERATIONS ===================
    def get_suppliers(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        active_only: bool = True,
    ) -> List[Supplier]:
        """Buscar fornecedores"""
        query = self.db.query(Supplier)

        if active_only:
            query = query.filter(Supplier.is_active == True)

        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                Supplier.name.ilike(search_filter)
                | Supplier.company_name.ilike(search_filter)
                | Supplier.document.ilike(search_filter)
            )

        return query.offset(skip).limit(limit).all()

    def get_supplier_by_id(self, supplier_id: int) -> Optional[Supplier]:
        """Buscar fornecedor por ID"""
        return self.db.query(Supplier).filter(Supplier.id == supplier_id).first()

    def create_supplier(self, supplier_data: SupplierCreate) -> Supplier:
        """Criar novo fornecedor"""
        supplier = Supplier(**supplier_data.dict())
        self.db.add(supplier)
        self.db.commit()
        self.db.refresh(supplier)
        return supplier

    def update_supplier(
        self, supplier_id: int, supplier_data: SupplierUpdate
    ) -> Optional[Supplier]:
        """Atualizar fornecedor"""
        supplier = self.get_supplier_by_id(supplier_id)
        if not supplier:
            return None

        update_data = supplier_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(supplier, field, value)

        self.db.commit()
        self.db.refresh(supplier)
        return supplier

    # =================== STOCK MOVEMENT OPERATIONS ===================
    def get_stock_movements(
        self,
        skip: int = 0,
        limit: int = 100,
        product_id: Optional[int] = None,
        movement_type: Optional[MovementType] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[StockMovement]:
        """Buscar movimentações de estoque"""
        query = self.db.query(StockMovement).options(
            joinedload(StockMovement.product),
            joinedload(StockMovement.user),
            joinedload(StockMovement.supplier),
        )

        if product_id:
            query = query.filter(StockMovement.product_id == product_id)

        if movement_type:
            query = query.filter(StockMovement.movement_type == movement_type)

        if start_date:
            query = query.filter(func.date(StockMovement.created_at) >= start_date)

        if end_date:
            query = query.filter(func.date(StockMovement.created_at) <= end_date)

        return (
            query.order_by(desc(StockMovement.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_stock_movement(
        self, movement_data: StockMovementCreate, user_id: int
    ) -> StockMovement:
        """Criar movimentação de estoque"""
        # Buscar produto atual
        product = (
            self.db.query(Product)
            .filter(Product.id == movement_data.product_id)
            .first()
        )
        if not product:
            raise ValueError("Produto não encontrado")

        previous_quantity = int(product.stock_quantity)

        # Calcular nova quantidade baseada no tipo de movimento
        if movement_data.movement_type == MovementType.ENTRADA:
            new_quantity = previous_quantity + movement_data.quantity
        elif movement_data.movement_type == MovementType.SAIDA:
            new_quantity = max(0, previous_quantity - movement_data.quantity)
        elif movement_data.movement_type == MovementType.AJUSTE:
            new_quantity = (
                movement_data.quantity
            )  # Quantity é o valor absoluto para ajuste
        else:  # PERDA, DEVOLUCAO, TRANSFERENCIA
            new_quantity = previous_quantity - movement_data.quantity

        # Calcular custo total
        total_cost = None
        if movement_data.unit_cost and movement_data.quantity:
            total_cost = movement_data.unit_cost * movement_data.quantity

        # Criar movimento
        movement = StockMovement(
            product_id=movement_data.product_id,
            movement_type=movement_data.movement_type,
            quantity=movement_data.quantity,
            previous_quantity=previous_quantity,
            new_quantity=new_quantity,
            unit_cost=movement_data.unit_cost,
            total_cost=total_cost,
            reason=movement_data.reason,
            notes=movement_data.notes,
            user_id=user_id,
            supplier_id=movement_data.supplier_id,
        )

        # Atualizar estoque do produto
        product.stock_quantity = new_quantity

        # Atualizar datas do produto
        if movement_data.movement_type == MovementType.ENTRADA:
            product.last_purchase_date = datetime.utcnow()
        elif movement_data.movement_type == MovementType.SAIDA:
            product.last_sale_date = datetime.utcnow()

        self.db.add(movement)
        self.db.commit()
        self.db.refresh(movement)
        return movement

    def adjust_stock(
        self, product_id: int, new_quantity: int, reason: str, user_id: int
    ) -> StockMovement:
        """Ajustar estoque de um produto"""
        movement_data = StockMovementCreate(
            product_id=product_id,
            movement_type=MovementType.AJUSTE,
            quantity=new_quantity,  # Para ajuste, quantity é o valor final
            reason=reason,
        )
        return self.create_stock_movement(movement_data, user_id)

    # =================== PURCHASE ORDER OPERATIONS ===================
    def get_purchase_orders(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        supplier_id: Optional[int] = None,
    ) -> List[PurchaseOrder]:
        """Buscar pedidos de compra"""
        query = self.db.query(PurchaseOrder).options(
            joinedload(PurchaseOrder.supplier),
            joinedload(PurchaseOrder.user),
            joinedload(PurchaseOrder.items).joinedload(PurchaseOrderItem.product),
        )

        if status:
            query = query.filter(PurchaseOrder.status == status)

        if supplier_id:
            query = query.filter(PurchaseOrder.supplier_id == supplier_id)

        return (
            query.order_by(desc(PurchaseOrder.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_purchase_order_by_id(self, order_id: int) -> Optional[PurchaseOrder]:
        """Buscar pedido por ID"""
        return (
            self.db.query(PurchaseOrder)
            .options(
                joinedload(PurchaseOrder.supplier),
                joinedload(PurchaseOrder.user),
                joinedload(PurchaseOrder.items).joinedload(PurchaseOrderItem.product),
            )
            .filter(PurchaseOrder.id == order_id)
            .first()
        )

    def create_purchase_order(
        self, order_data: PurchaseOrderCreate, user_id: int
    ) -> PurchaseOrder:
        """Criar pedido de compra"""
        # Criar pedido
        order = PurchaseOrder(
            supplier_id=order_data.supplier_id,
            order_number=order_data.order_number,
            notes=order_data.notes,
            user_id=user_id,
            expected_delivery=order_data.expected_delivery,
        )

        self.db.add(order)
        self.db.flush()  # Para obter o ID

        # Criar itens do pedido
        total_amount = Decimal("0")
        for item_data in order_data.items:
            total_cost = item_data.unit_cost * item_data.quantity_ordered
            item = PurchaseOrderItem(
                purchase_order_id=order.id,
                product_id=item_data.product_id,
                quantity_ordered=item_data.quantity_ordered,
                unit_cost=item_data.unit_cost,
                total_cost=total_cost,
            )
            total_amount += total_cost
            self.db.add(item)

        # Atualizar valor total
        order.total_amount = total_amount

        self.db.commit()
        self.db.refresh(order)
        return order

    def update_purchase_order(
        self, order_id: int, order_data: PurchaseOrderUpdate
    ) -> Optional[PurchaseOrder]:
        """Atualizar pedido de compra"""
        order = self.get_purchase_order_by_id(order_id)
        if not order:
            return None

        update_data = order_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(order, field, value)

        self.db.commit()
        self.db.refresh(order)
        return order

    # =================== STOCK REPORTS ===================
    def get_stock_report(
        self,
        category_id: Optional[int] = None,
        supplier_id: Optional[int] = None,
        low_stock_only: bool = False,
    ) -> tuple[StockSummary, List[StockReportItem]]:
        """Gerar relatório de estoque"""

        # Query base
        query = (
            self.db.query(
                Product.id.label("product_id"),
                Product.name.label("product_name"),
                Product.barcode,
                Category.name.label("category_name"),
                Supplier.name.label("supplier_name"),
                Product.stock_quantity.label("current_stock"),
                Product.min_stock_level.label("min_stock"),
                Product.max_stock.label("max_stock"),
                Product.reorder_point,
                Product.cost_price,
                Product.price.label("sale_price"),
                Product.location,
                Product.last_purchase_date,
                Product.last_sale_date,
            )
            .join(Category)
            .outerjoin(Supplier)
        )

        if category_id:
            query = query.filter(Product.category_id == category_id)

        if supplier_id:
            query = query.filter(Product.supplier_id == supplier_id)

        if low_stock_only:
            query = query.filter(Product.stock_quantity <= Product.min_stock_level)

        products = query.filter(Product.is_active == True).all()

        # Processar dados dos produtos
        items = []
        total_stock_value = Decimal("0")
        low_stock_count = 0
        out_of_stock_count = 0
        overstock_count = 0

        for product in products:
            # Contar movimentações
            movement_count = (
                self.db.query(StockMovement)
                .filter(StockMovement.product_id == product.product_id)
                .count()
            )

            # Determinar status
            if product.current_stock == 0:
                status = "out_of_stock"
                out_of_stock_count += 1
            elif product.current_stock <= product.min_stock:
                status = "low_stock"
                low_stock_count += 1
            elif product.max_stock and product.current_stock > product.max_stock:
                status = "overstock"
                overstock_count += 1
            else:
                status = "ok"

            # Calcular valor do estoque
            stock_value = Decimal("0")
            if product.cost_price and product.current_stock:
                stock_value = Decimal(str(product.cost_price)) * Decimal(
                    str(product.current_stock)
                )

            total_stock_value += stock_value

            # Última movimentação
            last_movement_date = product.last_purchase_date or product.last_sale_date

            item = StockReportItem(
                product_id=product.product_id,
                product_name=product.product_name,
                barcode=product.barcode,
                category_name=product.category_name,
                supplier_name=product.supplier_name,
                current_stock=int(product.current_stock),
                min_stock=int(product.min_stock),
                max_stock=int(product.max_stock) if product.max_stock else None,
                reorder_point=int(product.reorder_point)
                if product.reorder_point
                else None,
                cost_price=Decimal(str(product.cost_price))
                if product.cost_price
                else None,
                sale_price=Decimal(str(product.sale_price)),
                stock_value=stock_value,
                location=product.location,
                last_movement_date=last_movement_date,
                movement_count=movement_count,
                status=status,
            )
            items.append(item)

        # Contar movimentações recentes
        today = date.today()
        movements_today = (
            self.db.query(StockMovement)
            .filter(func.date(StockMovement.created_at) == today)
            .count()
        )

        # Última semana
        week_ago = date.today().replace(day=date.today().day - 7)
        movements_week = (
            self.db.query(StockMovement)
            .filter(func.date(StockMovement.created_at) >= week_ago)
            .count()
        )

        # Sumário
        summary = StockSummary(
            total_products=len(products),
            total_stock_value=total_stock_value,
            low_stock_items=low_stock_count,
            out_of_stock_items=out_of_stock_count,
            overstocked_items=overstock_count,
            total_movements_today=movements_today,
            total_movements_week=movements_week,
        )

        return summary, items
