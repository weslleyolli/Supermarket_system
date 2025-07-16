"""
Serviço de produtos
"""

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.infrastructure.repositories.category_repository import CategoryRepository
from app.infrastructure.repositories.product_repository import ProductRepository
from app.presentation.schemas.product import (
    BulkPriceUpdate,
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    ProductCreate,
    ProductResponse,
    ProductSummary,
    ProductUpdate,
    StockAdjustment,
)


class ProductService:
    """Serviço de produtos"""

    def __init__(self, db: Session):
        self.db = db
        self.product_repo = ProductRepository(db)
        self.category_repo = CategoryRepository(db)

    def _calculate_product_fields(self, product) -> Dict[str, Any]:
        """Calcula campos adicionais do produto"""
        profit_margin = 0
        if product.cost_price > 0:
            profit_margin = (
                (product.price - product.cost_price) / product.cost_price
            ) * 100

        # Status do estoque
        if product.stock_quantity <= 0:
            stock_status = "sem_estoque"
        elif product.stock_quantity <= product.min_stock_level:
            stock_status = "estoque_baixo"
        else:
            stock_status = "ok"

        # Verificar se tem promoção
        has_promotion = (
            product.bulk_discount_enabled and product.bulk_discount_percentage > 0
        )

        return {
            "profit_margin": round(profit_margin, 2),
            "stock_status": stock_status,
            "has_promotion": has_promotion,
        }

    # CATEGORIAS
    def create_category(self, category_data: CategoryCreate) -> CategoryResponse:
        """Cria nova categoria"""
        try:
            category = self.category_repo.create(category_data)
            response_data = CategoryResponse.model_validate(category)
            response_data.products_count = self.category_repo.get_products_count(
                category.id
            )
            return response_data
        except ValueError as e:
            raise ValueError(str(e))

    def get_category(self, category_id: int) -> Optional[CategoryResponse]:
        """Obtém categoria por ID"""
        category = self.category_repo.get_by_id(category_id)
        if not category:
            return None

        response_data = CategoryResponse.model_validate(category)
        response_data.products_count = self.category_repo.get_products_count(
            category.id
        )
        return response_data

    def list_categories(
        self, skip: int = 0, limit: int = 100, active_only: bool = True
    ) -> List[CategoryResponse]:
        """Lista categorias"""
        categories = self.category_repo.get_all(
            skip=skip, limit=limit, active_only=active_only
        )

        result = []
        for category in categories:
            response_data = CategoryResponse.model_validate(category)
            response_data.products_count = self.category_repo.get_products_count(
                category.id
            )
            result.append(response_data)

        return result

    def update_category(
        self, category_id: int, category_data: CategoryUpdate
    ) -> Optional[CategoryResponse]:
        """Atualiza categoria"""
        try:
            category = self.category_repo.update(category_id, category_data)
            if not category:
                return None

            response_data = CategoryResponse.model_validate(category)
            response_data.products_count = self.category_repo.get_products_count(
                category.id
            )
            return response_data
        except ValueError as e:
            raise ValueError(str(e))

    def delete_category(self, category_id: int) -> bool:
        """Remove categoria"""
        try:
            return self.category_repo.delete(category_id)
        except ValueError as e:
            raise ValueError(str(e))

    # PRODUTOS
    def create_product(self, product_data: ProductCreate) -> ProductResponse:
        """Cria novo produto"""
        try:
            product = self.product_repo.create(product_data)

            # Carregar categoria
            product = self.product_repo.get_by_id(product.id)

            # Preparar resposta
            response_data = ProductResponse.model_validate(product)

            # Adicionar campos calculados
            calculated_fields = self._calculate_product_fields(product)
            for field, value in calculated_fields.items():
                setattr(response_data, field, value)

            return response_data
        except ValueError as e:
            raise ValueError(str(e))

    def get_product(self, product_id: int) -> Optional[ProductResponse]:
        """Obtém produto por ID"""
        product = self.product_repo.get_by_id(product_id)
        if not product:
            return None

        response_data = ProductResponse.model_validate(product)

        # Adicionar campos calculados
        calculated_fields = self._calculate_product_fields(product)
        for field, value in calculated_fields.items():
            setattr(response_data, field, value)

        return response_data

    def get_product_by_barcode(self, barcode: str) -> Optional[ProductResponse]:
        """Obtém produto por código de barras"""
        product = self.product_repo.get_by_barcode(barcode)
        if not product:
            return None

        response_data = ProductResponse.model_validate(product)

        # Adicionar campos calculados
        calculated_fields = self._calculate_product_fields(product)
        for field, value in calculated_fields.items():
            setattr(response_data, field, value)

        return response_data

    def search_products(
        self,
        query: str = None,
        category_id: int = None,
        active_only: bool = True,
        low_stock_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ProductSummary]:
        """Busca produtos"""
        products = self.product_repo.search(
            query=query,
            category_id=category_id,
            active_only=active_only,
            low_stock_only=low_stock_only,
            skip=skip,
            limit=limit,
        )

        result = []
        for product in products:
            calculated_fields = self._calculate_product_fields(product)

            summary = ProductSummary(
                id=product.id,
                name=product.name,
                barcode=product.barcode,
                price=product.price,
                stock_quantity=product.stock_quantity,
                category_name=product.category.name,
                is_active=product.is_active,
                stock_status=calculated_fields["stock_status"],
            )
            result.append(summary)

        return result

    def list_products(
        self, skip: int = 0, limit: int = 100, active_only: bool = True
    ) -> List[ProductSummary]:
        """Lista produtos"""
        return self.search_products(skip=skip, limit=limit, active_only=active_only)

    def update_product(
        self, product_id: int, product_data: ProductUpdate
    ) -> Optional[ProductResponse]:
        """Atualiza produto"""
        try:
            product = self.product_repo.update(product_id, product_data)
            if not product:
                return None

            # Recarregar com categoria
            product = self.product_repo.get_by_id(product.id)

            response_data = ProductResponse.model_validate(product)

            # Adicionar campos calculados
            calculated_fields = self._calculate_product_fields(product)
            for field, value in calculated_fields.items():
                setattr(response_data, field, value)

            return response_data
        except ValueError as e:
            raise ValueError(str(e))

    def delete_product(self, product_id: int) -> bool:
        """Remove produto"""
        return self.product_repo.delete(product_id)

    def adjust_stock(
        self, adjustment: StockAdjustment, user_id: int
    ) -> ProductResponse:
        """Ajusta estoque"""
        try:
            product = self.product_repo.adjust_stock(adjustment, user_id)

            # Recarregar com categoria
            product = self.product_repo.get_by_id(product.id)

            response_data = ProductResponse.model_validate(product)

            # Adicionar campos calculados
            calculated_fields = self._calculate_product_fields(product)
            for field, value in calculated_fields.items():
                setattr(response_data, field, value)

            return response_data
        except ValueError as e:
            raise ValueError(str(e))

    def get_low_stock_products(self, limit: int = 50) -> List[ProductSummary]:
        """Produtos com estoque baixo"""
        products = self.product_repo.get_low_stock_products(limit)

        result = []
        for product in products:
            summary = ProductSummary(
                id=product.id,
                name=product.name,
                barcode=product.barcode,
                price=product.price,
                stock_quantity=product.stock_quantity,
                category_name=product.category.name,
                is_active=product.is_active,
                stock_status="estoque_baixo",
            )
            result.append(summary)

        return result

    def update_prices_bulk(self, bulk_update: BulkPriceUpdate) -> Dict[str, Any]:
        """Atualiza preços em lote"""
        try:
            updated_count = self.product_repo.update_prices_bulk(
                category_id=bulk_update.category_id,
                percentage=bulk_update.price_change_percentage,
                apply_to_cost=bulk_update.apply_to_cost_price,
            )

            return {
                "updated_count": updated_count,
                "percentage": bulk_update.price_change_percentage,
                "category_id": bulk_update.category_id,
            }
        except Exception as e:
            raise ValueError(f"Erro ao atualizar preços: {str(e)}")
