"""
Endpoints de produtos
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.application.services.product_service import ProductService
from app.infrastructure.database.connection import get_db
from app.presentation.api.dependencies import get_current_active_user, require_admin
from app.presentation.schemas.auth import UserResponse
from app.presentation.schemas.product import (
    BarcodeSearch,
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

router = APIRouter(prefix="/products", tags=["Produtos"])


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    """Dependency para obter serviço de produtos"""
    return ProductService(db)


# ENDPOINTS DE CATEGORIAS
@router.post(
    "/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED
)
async def create_category(
    category_data: CategoryCreate,
    product_service: ProductService = Depends(get_product_service),
    _: UserResponse = Depends(require_admin),
):
    """
    Cria nova categoria (Manager+ apenas)
    """
    try:
        return product_service.create_category(category_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/categories", response_model=List[CategoryResponse])
async def list_categories(
    skip: int = Query(0, ge=0, description="Pular registros"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    active_only: bool = Query(True, description="Apenas categorias ativas"),
    product_service: ProductService = Depends(get_product_service),
    _: UserResponse = Depends(get_current_active_user),
):
    """
    Lista categorias
    """
    return product_service.list_categories(
        skip=skip, limit=limit, active_only=active_only
    )


@router.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    product_service: ProductService = Depends(get_product_service),
    _: UserResponse = Depends(get_current_active_user),
):
    """
    Obtém categoria por ID
    """
    category = product_service.get_category(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada"
        )
    return category


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    product_service: ProductService = Depends(get_product_service),
    _: UserResponse = Depends(require_admin),
):
    """
    Atualiza categoria (Manager+ apenas)
    """
    try:
        category = product_service.update_category(category_id, category_data)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada"
            )
        return category
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    product_service: ProductService = Depends(get_product_service),
    _: UserResponse = Depends(require_admin),
):
    """
    Remove categoria (Manager+ apenas)
    """
    try:
        success = product_service.delete_category(category_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada"
            )
        return {"message": "Categoria removida com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ENDPOINTS DE PRODUTOS
@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    product_service: ProductService = Depends(get_product_service),
    _: UserResponse = Depends(require_admin),
):
    """
    Cria novo produto (Manager+ apenas)

    - **name**: Nome do produto
    - **barcode**: Código de barras (8-14 dígitos)
    - **category_id**: ID da categoria
    - **price**: Preço de venda
    - **cost_price**: Preço de custo
    - **stock_quantity**: Quantidade em estoque
    - **unit_type**: Tipo de unidade (unidade/peso/volume)
    - **requires_weighing**: Se requer pesagem
    - **bulk_discount_enabled**: Se tem desconto por quantidade
    """
    try:
        return product_service.create_product(product_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[ProductSummary])
async def list_products(
    skip: int = Query(0, ge=0, description="Pular registros"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    active_only: bool = Query(True, description="Apenas produtos ativos"),
    product_service: ProductService = Depends(get_product_service),
    _: UserResponse = Depends(get_current_active_user),
):
    """
    Lista produtos (resumo)
    """
    return product_service.list_products(
        skip=skip, limit=limit, active_only=active_only
    )


@router.get("/search", response_model=List[ProductSummary])
async def search_products(
    q: Optional[str] = Query(None, description="Buscar por nome, código ou descrição"),
    category_id: Optional[int] = Query(None, description="Filtrar por categoria"),
    low_stock: bool = Query(False, description="Apenas produtos com estoque baixo"),
    skip: int = Query(0, ge=0, description="Pular registros"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    product_service: ProductService = Depends(get_product_service),
    _: UserResponse = Depends(get_current_active_user),
):
    """
    Busca produtos com filtros

    - **q**: Texto para buscar (nome, código, descrição)
    - **category_id**: Filtrar por categoria
    - **low_stock**: Apenas produtos com estoque baixo
    """
    return product_service.search_products(
        query=q,
        category_id=category_id,
        low_stock_only=low_stock,
        skip=skip,
        limit=limit,
    )


@router.post("/barcode-search", response_model=ProductResponse)
async def search_by_barcode(
    barcode_data: BarcodeSearch,
    product_service: ProductService = Depends(get_product_service),
    _: UserResponse = Depends(get_current_active_user),
):
    """
    Busca produto por código de barras

    Endpoint específico para leitores de código de barras
    """
    product = product_service.get_product_by_barcode(barcode_data.barcode)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto com código {barcode_data.barcode} não encontrado",
        )
    return product


@router.get("/low-stock", response_model=List[ProductSummary])
async def get_low_stock_products(
    limit: int = Query(50, ge=1, le=500, description="Limite de produtos"),
    product_service: ProductService = Depends(get_product_service),
    _: UserResponse = Depends(get_current_active_user),
):
    """
    Lista produtos com estoque baixo

    Produtos onde quantidade <= estoque mínimo
    """
    return product_service.get_low_stock_products(limit=limit)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    product_service: ProductService = Depends(get_product_service),
    _: UserResponse = Depends(get_current_active_user),
):
    """
    Obtém produto por ID (detalhes completos)
    """
    product = product_service.get_product(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado"
        )
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    product_service: ProductService = Depends(get_product_service),
    _: UserResponse = Depends(require_admin),
):
    """
    Atualiza produto (Manager+ apenas)
    """
    try:
        product = product_service.update_product(product_id, product_data)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado"
            )
        return product
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    product_service: ProductService = Depends(get_product_service),
    _: UserResponse = Depends(require_admin),
):
    """
    Remove produto (Manager+ apenas)
    """
    success = product_service.delete_product(product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado"
        )
    return {"message": "Produto removido com sucesso"}


@router.post("/stock/adjust", response_model=ProductResponse)
async def adjust_stock(
    adjustment: StockAdjustment,
    current_user: UserResponse = Depends(get_current_active_user),
    product_service: ProductService = Depends(get_product_service),
):
    """
    Ajusta estoque do produto

    - **product_id**: ID do produto
    - **quantity_change**: Quantidade a adicionar (+) ou remover (-)
    - **reason**: Motivo do ajuste
    """
    try:
        return product_service.adjust_stock(adjustment, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/prices/bulk-update")
async def bulk_update_prices(
    bulk_update: BulkPriceUpdate,
    product_service: ProductService = Depends(get_product_service),
    _: UserResponse = Depends(require_admin),
):
    """
    Atualiza preços em lote (Manager+ apenas)

    - **category_id**: ID da categoria (opcional - aplica a todos se não informado)
    - **price_change_percentage**: Percentual de mudança (-50% a +100%)
    - **apply_to_cost_price**: Aplicar também ao preço de custo
    """
    try:
        result = product_service.update_prices_bulk(bulk_update)
        return {"message": "Preços atualizados com sucesso", "details": result}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
