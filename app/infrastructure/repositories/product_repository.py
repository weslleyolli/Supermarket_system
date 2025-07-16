"""
Repositório de produtos
"""

from typing import Any, Dict, List, Optional

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.infrastructure.database.models.product import Category, Product
from app.presentation.schemas.product import (
    ProductCreate,
    ProductUpdate,
    StockAdjustment,
)


class ProductRepository:
    """Repositório para operações com produtos"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Busca produto por ID com categoria"""
        return (
            self.db.query(Product)
            .options(joinedload(Product.category))
            .filter(Product.id == product_id)
            .first()
        )

    def get_by_barcode(self, barcode: str) -> Optional[Product]:
        """Busca produto por código de barras"""
        return (
            self.db.query(Product)
            .options(joinedload(Product.category))
            .filter(Product.barcode == barcode)
            .first()
        )

    def search(
        self,
        query: str = None,
        category_id: int = None,
        active_only: bool = True,
        low_stock_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Product]:
        """Busca produtos com filtros"""
        db_query = self.db.query(Product).options(joinedload(Product.category))

        # Filtro por status
        if active_only:
            db_query = db_query.filter(Product.is_active)

        # Filtro por categoria
        if category_id:
            db_query = db_query.filter(Product.category_id == category_id)

        # Filtro por estoque baixo
        if low_stock_only:
            db_query = db_query.filter(
                Product.stock_quantity <= Product.min_stock_level
            )

        # Busca por texto
        if query:
            search_filter = or_(
                Product.name.ilike(f"%{query}%"),
                Product.barcode.ilike(f"%{query}%"),
                Product.description.ilike(f"%{query}%"),
            )
            db_query = db_query.filter(search_filter)

        return db_query.offset(skip).limit(limit).all()

    def get_all(
        self, skip: int = 0, limit: int = 100, active_only: bool = True
    ) -> List[Product]:
        """Lista todos os produtos"""
        query = self.db.query(Product).options(joinedload(Product.category))

        if active_only:
            query = query.filter(Product.is_active)

        return query.offset(skip).limit(limit).all()

    def create(self, product_data: ProductCreate) -> Product:
        """Cria novo produto"""
        # Verificar se código de barras já existe
        existing = self.get_by_barcode(product_data.barcode)
        if existing:
            raise ValueError("Código de barras já existe")

        # Verificar se categoria existe
        category = (
            self.db.query(Category)
            .filter(Category.id == product_data.category_id)
            .first()
        )
        if not category:
            raise ValueError("Categoria não encontrada")

        db_product = Product(**product_data.model_dump())

        try:
            self.db.add(db_product)
            self.db.commit()
            self.db.refresh(db_product)
            return db_product
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Erro ao criar produto")

    def update(self, product_id: int, product_data: ProductUpdate) -> Optional[Product]:
        """Atualiza produto"""
        db_product = self.get_by_id(product_id)
        if not db_product:
            return None

        update_data = product_data.model_dump(exclude_unset=True)

        # Verificar código de barras duplicado
        if "barcode" in update_data:
            existing = self.get_by_barcode(update_data["barcode"])
            if existing and existing.id != product_id:
                raise ValueError("Código de barras já existe")

        # Verificar categoria
        if "category_id" in update_data:
            category = (
                self.db.query(Category)
                .filter(Category.id == update_data["category_id"])
                .first()
            )
            if not category:
                raise ValueError("Categoria não encontrada")

        for field, value in update_data.items():
            setattr(db_product, field, value)

        try:
            self.db.commit()
            self.db.refresh(db_product)
            return db_product
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Erro ao atualizar produto")

    def delete(self, product_id: int) -> bool:
        """Remove produto (soft delete)"""
        db_product = self.get_by_id(product_id)
        if not db_product:
            return False

        db_product.is_active = False
        self.db.commit()
        return True

    def adjust_stock(self, adjustment: StockAdjustment, user_id: int) -> Product:
        """Ajusta estoque do produto"""
        db_product = self.get_by_id(adjustment.product_id)
        if not db_product:
            raise ValueError("Produto não encontrado")

        new_quantity = db_product.stock_quantity + adjustment.quantity_change

        if new_quantity < 0:
            raise ValueError("Estoque não pode ficar negativo")

        db_product.stock_quantity = new_quantity

        # Registrar movimentação de estoque (implementar depois)
        # self._create_stock_movement(adjustment, user_id)

        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def get_low_stock_products(self, limit: int = 50) -> List[Product]:
        """Produtos com estoque baixo"""
        return (
            self.db.query(Product)
            .options(joinedload(Product.category))
            .filter(
                and_(
                    Product.is_active, Product.stock_quantity <= Product.min_stock_level
                )
            )
            .limit(limit)
            .all()
        )

    def get_top_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Produtos mais vendidos (implementar com dados de vendas depois)"""
        # Por enquanto retorna produtos com maior estoque
        products = (
            self.db.query(Product)
            .options(joinedload(Product.category))
            .filter(Product.is_active)
            .order_by(desc(Product.stock_quantity))
            .limit(limit)
            .all()
        )

        return [
            {
                "product": product,
                "sales_count": 0,  # Implementar depois
                "revenue": 0.0,  # Implementar depois
            }
            for product in products
        ]

    def update_prices_bulk(
        self, category_id: Optional[int], percentage: float, apply_to_cost: bool = False
    ) -> int:
        """Atualiza preços em lote"""
        query = self.db.query(Product).filter(Product.is_active)

        if category_id:
            query = query.filter(Product.category_id == category_id)

        products = query.all()
        updated_count = 0

        for product in products:
            # Atualizar preço de venda
            product.price = product.price * (1 + percentage / 100)

            # Atualizar preço de custo se solicitado
            if apply_to_cost:
                product.cost_price = product.cost_price * (1 + percentage / 100)

            updated_count += 1

        self.db.commit()
        return updated_count
