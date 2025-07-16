"""
Serviço de vendas e PDV
"""

from datetime import date
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.infrastructure.repositories.product_repository import ProductRepository
from app.infrastructure.repositories.sale_repository import SaleRepository
from app.presentation.schemas.product import ProductResponse
from app.presentation.schemas.sale import (
    BarcodeInput,
    Cart,
    CartItem,
    CartOperation,
    PaymentRequest,
    PaymentResponse,
    SaleItemResponse,
    SaleResponse,
    SaleSummary,
)


class SaleService:
    """Serviço de vendas"""

    # Carrinhos em memória por usuário
    _user_carts: Dict[int, Cart] = {}

    def __init__(self, db: Session, user_id: Optional[int] = None):
        self.db = db
        self.product_repo = ProductRepository(db)
        self.sale_repo = SaleRepository(db)
        self.user_id = user_id
        if user_id is not None:
            if user_id not in self._user_carts:
                self._user_carts[user_id] = Cart()
            self._current_cart = self._user_carts[user_id]
        else:
            self._current_cart = Cart()

    def _calculate_item_total(
        self, product: ProductResponse, quantity: float, weight: Optional[float] = None
    ) -> Tuple[float, float, float]:
        if product.requires_weighing and weight:
            original_total = weight * product.price
        else:
            original_total = quantity * product.price
        bulk_discount = 0
        if product.bulk_discount_enabled:
            effective_quantity = weight if product.requires_weighing else quantity
            if effective_quantity >= product.bulk_min_quantity:
                bulk_discount = original_total * (
                    product.bulk_discount_percentage / 100
                )
        final_total = original_total - bulk_discount
        return original_total, bulk_discount, final_total

    def _create_cart_item(
        self, product: ProductResponse, quantity: float, weight: Optional[float] = None
    ) -> CartItem:
        original_total, bulk_discount, final_total = self._calculate_item_total(
            product, quantity, weight
        )
        promotion_description = ""
        if bulk_discount > 0:
            promotion_description = f"{product.bulk_min_quantity}+ unidades = {product.bulk_discount_percentage}% OFF"
        return CartItem(
            product_id=product.id,
            product_name=product.name,
            product_barcode=product.barcode,
            unit_price=product.price,
            quantity=quantity,
            weight=weight,
            requires_weighing=product.requires_weighing,
            original_total=original_total,
            discount_applied=0,
            bulk_discount_applied=bulk_discount,
            final_total=final_total,
            has_promotion=bulk_discount > 0,
            promotion_description=promotion_description,
        )

    def _recalculate_cart(self, cart: Cart) -> Cart:
        cart.subtotal = sum(item.original_total for item in cart.items)
        cart.total_discount = sum(item.discount_applied for item in cart.items)
        cart.bulk_discount = sum(item.bulk_discount_applied for item in cart.items)
        cart.final_total = sum(item.final_total for item in cart.items)
        cart.total_items = len(cart.items)
        cart.total_quantity = sum(item.quantity for item in cart.items)
        return cart

    def add_product_by_barcode(self, barcode_input: BarcodeInput) -> Dict[str, Any]:
        product = self.product_repo.get_by_barcode(barcode_input.barcode)
        if not product:
            raise ValueError(
                f"Produto com código {barcode_input.barcode} não encontrado"
            )
        if not product.is_active:
            raise ValueError("Produto inativo")
        required_quantity = (
            barcode_input.weight
            if product.requires_weighing
            else barcode_input.quantity
        )
        if product.stock_quantity < required_quantity:
            raise ValueError(
                f"Estoque insuficiente. Disponível: {product.stock_quantity}"
            )
        from app.application.services.product_service import ProductService

        product_service = ProductService(self.db)
        product_response = product_service.get_product(product.id)
        existing_item = None
        for item in self._current_cart.items:
            if item.product_id == product.id:
                existing_item = item
                break
        if existing_item:
            new_quantity = existing_item.quantity + barcode_input.quantity
            new_weight = None
            if product_response.requires_weighing:
                new_weight = (existing_item.weight or 0) + (barcode_input.weight or 0)
            original_total, bulk_discount, final_total = self._calculate_item_total(
                product_response, new_quantity, new_weight
            )
            existing_item.quantity = new_quantity
            existing_item.weight = new_weight
            existing_item.original_total = original_total
            existing_item.bulk_discount_applied = bulk_discount
            existing_item.final_total = final_total
            existing_item.has_promotion = bulk_discount > 0
            if bulk_discount > 0:
                existing_item.promotion_description = f"{product_response.bulk_min_quantity}+ unidades = {product_response.bulk_discount_percentage}% OFF"
        else:
            cart_item = self._create_cart_item(
                product_response, barcode_input.quantity, barcode_input.weight
            )
            self._current_cart.items.append(cart_item)
        self._current_cart = self._recalculate_cart(self._current_cart)
        # Atualiza o carrinho global do usuário, se aplicável
        if self.user_id is not None:
            self._user_carts[self.user_id] = self._current_cart
        return {
            "success": True,
            "message": f"Produto {product_response.name} adicionado",
            "product": {
                "id": product_response.id,
                "name": product_response.name,
                "price": product_response.price,
                "requires_weighing": product_response.requires_weighing,
            },
            "cart": self._current_cart,
        }

    def get_current_cart(self) -> Cart:
        if self.user_id is not None and self.user_id in self._user_carts:
            return self._user_carts[self.user_id]
        return self._current_cart

    def update_cart_item(self, operation: CartOperation) -> Cart:
        if operation.operation == "clear":
            self._current_cart = Cart()
            return self._current_cart
        if operation.operation == "remove" and operation.product_id:
            self._current_cart.items = [
                item
                for item in self._current_cart.items
                if item.product_id != operation.product_id
            ]
        elif operation.operation == "update" and operation.product_id:
            for item in self._current_cart.items:
                if item.product_id == operation.product_id:
                    product = self.product_repo.get_by_id(operation.product_id)
                    if product:
                        from app.application.services.product_service import (
                            ProductService,
                        )

                        product_service = ProductService(self.db)
                        product_response = product_service.get_product(product.id)
                        if operation.quantity is not None:
                            item.quantity = operation.quantity
                        if operation.weight is not None:
                            item.weight = operation.weight
                        (
                            original_total,
                            bulk_discount,
                            final_total,
                        ) = self._calculate_item_total(
                            product_response, item.quantity, item.weight
                        )
                        item.original_total = original_total
                        item.bulk_discount_applied = bulk_discount
                        item.final_total = final_total
                        item.has_promotion = bulk_discount > 0
                    break
        self._current_cart = self._recalculate_cart(self._current_cart)
        return self._current_cart

    def process_payment(
        self, payment_request: PaymentRequest, user_id: int
    ) -> PaymentResponse:
        if not self._current_cart.items:
            raise ValueError("Carrinho vazio")
        if payment_request.amount_received < self._current_cart.final_total:
            raise ValueError("Valor recebido insuficiente")
        sale_items = []
        for cart_item in self._current_cart.items:
            sale_items.append(
                {
                    "product_id": cart_item.product_id,
                    "quantity": cart_item.quantity,
                    "weight": cart_item.weight,
                    "unit_price": cart_item.unit_price,
                    "original_total_price": cart_item.original_total,
                    "discount_applied": cart_item.discount_applied,
                    "bulk_discount_applied": cart_item.bulk_discount_applied,
                    "final_total_price": cart_item.final_total,
                }
            )
        sale_data = {
            "customer_id": payment_request.customer_id,
            "user_id": user_id,
            "subtotal_amount": self._current_cart.subtotal,
            "discount_amount": self._current_cart.total_discount,
            "bulk_discount_amount": self._current_cart.bulk_discount,
            "final_amount": self._current_cart.final_total,
            "payment_method": payment_request.payment_method,
            "items": sale_items,
        }
        # Salva a venda no banco e retorna o objeto sale
        sale = self.sale_repo.create_sale(sale_data)
        for cart_item in self._current_cart.items:
            product = self.product_repo.get_by_id(cart_item.product_id)
            if product:
                quantity_to_remove = (
                    cart_item.weight
                    if cart_item.requires_weighing
                    else cart_item.quantity
                )
                product.stock_quantity -= quantity_to_remove
                self.db.commit()
        change_amount = payment_request.amount_received - self._current_cart.final_total
        receipt_data = {
            "sale_id": sale.id,
            "date": sale.created_at.strftime("%d/%m/%Y %H:%M:%S"),
            "items": [
                {
                    "name": item.product_name,
                    "quantity": item.quantity,
                    "weight": item.weight,
                    "unit_price": item.unit_price,
                    "total": item.final_total,
                    "discount": item.bulk_discount_applied,
                }
                for item in self._current_cart.items
            ],
            "subtotal": self._current_cart.subtotal,
            "total_discount": self._current_cart.bulk_discount,
            "final_total": self._current_cart.final_total,
            "payment_method": payment_request.payment_method.value,
            "amount_received": payment_request.amount_received,
            "change": change_amount,
        }
        self._current_cart = Cart()
        if self.user_id is not None:
            self._user_carts[self.user_id] = self._current_cart
        return PaymentResponse(
            sale_id=sale.id,
            final_amount=sale.final_amount,
            amount_received=payment_request.amount_received,
            change_amount=change_amount,
            payment_method=payment_request.payment_method,
            receipt_data=receipt_data,
        )

    def get_sale(self, sale_id: int) -> Optional[SaleResponse]:
        sale = self.sale_repo.get_by_id(sale_id)
        if not sale:
            return None
        return self._convert_to_sale_response(sale)

    def list_sales(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        user_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[SaleSummary]:
        sales = self.sale_repo.get_sales_by_filters(
            start_date=start_date,
            end_date=end_date,
            user_id=user_id,
            status=status,
            skip=skip,
            limit=limit,
        )
        result = []
        for sale in sales:
            summary = SaleSummary(
                id=sale.id,
                final_amount=sale.final_amount,
                payment_method=sale.payment_method,
                status=sale.status,
                total_items=len(sale.items),
                created_at=sale.created_at,
                cashier_name=sale.user.full_name,
            )
            result.append(summary)
        return result

    def cancel_sale(self, sale_id: int, user_id: int) -> bool:
        return self.sale_repo.cancel_sale(sale_id, user_id)

    def _convert_to_sale_response(self, sale) -> SaleResponse:
        items = []
        for item in sale.items:
            item_response = SaleItemResponse(
                id=item.id,
                product_id=item.product_id,
                quantity=item.quantity,
                weight=item.weight,
                unit_price=item.unit_price,
                original_total_price=item.original_total_price,
                discount_applied=item.discount_applied,
                bulk_discount_applied=item.bulk_discount_applied,
                final_total_price=item.final_total_price,
                product_name=item.product.name,
                product_barcode=item.product.barcode,
            )
            items.append(item_response)
        response = SaleResponse(
            id=sale.id,
            customer_id=sale.customer_id,
            user_id=sale.user_id,
            subtotal_amount=sale.subtotal_amount,
            discount_amount=sale.discount_amount,
            bulk_discount_amount=sale.bulk_discount_amount,
            final_amount=sale.final_amount,
            payment_method=sale.payment_method,
            status=sale.status,
            created_at=sale.created_at,
            items=items,
        )
        response.total_items = len(items)
        response.total_quantity = sum(item.quantity for item in items)
        response.total_savings = sale.discount_amount + sale.bulk_discount_amount
        return response
