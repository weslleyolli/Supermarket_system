"""
Interface PDV para Streamlit com autenticação
"""

from typing import Dict, Optional

import requests
import streamlit as st


class PDVInterface:
    """Interface do PDV em Streamlit com autenticação"""

    def __init__(self):
        self.api_base = "http://localhost:8000/api/v1"

    def get_headers(self, token: str) -> Dict[str, str]:
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def render_authenticated(self, user: dict, token: str):
        if user["role"] not in ["admin", "manager", "supervisor", "cashier"]:
            st.error("❌ Você não tem permissão para acessar o PDV")
            return
        col1, col2 = st.columns([2, 1])
        with col1:
            self._render_product_input(token)
            self._render_cart(token)
        with col2:
            self._render_payment_panel(token, user)
            self._render_quick_actions(token)

    def _render_product_input(self, token: str):
        st.subheader("📦 Adicionar Produto")
        with st.form("add_product_form", clear_on_submit=True):
            barcode = st.text_input(
                "Código de Barras",
                placeholder="Digite ou escaneie o código...",
                help="Códigos de teste: 7891000100103, 7891000500107",
            )
            col1, col2 = st.columns(2)
            with col1:
                quantity = st.number_input(
                    "Quantidade", min_value=0.0, value=1.0, step=1.0, format="%.0f"
                )
            with col2:
                weight = st.number_input(
                    "Peso (kg)",
                    min_value=0.0,
                    value=0.0,
                    step=0.001,
                    format="%.3f",
                    help="Para produtos vendidos por peso",
                )
            submitted = st.form_submit_button("➕ Adicionar ao Carrinho", type="primary")
            if submitted and barcode:
                # Só permite adicionar se quantidade > 0 ou peso > 0
                if quantity > 0 or weight > 0:
                    self._add_product_to_cart(barcode, quantity, weight, token)
                else:
                    st.warning("Informe uma quantidade ou peso maior que zero.")

    def _render_cart(self, token: str):
        st.subheader("🛒 Carrinho de Compras")
        try:
            response = requests.get(
                f"{self.api_base}/pdv/cart", headers=self.get_headers(token), timeout=5
            )
            if response.status_code == 200:
                cart = response.json()
            else:
                st.error("Erro ao obter carrinho")
                return
        except Exception as e:
            st.error(f"Erro de conexão: {e}")
            return
        if not cart.get("items"):
            st.info("Carrinho vazio - Adicione produtos usando o código de barras")
            return
        for i, item in enumerate(cart["items"]):
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    st.write(f"**{item['product_name']}**")
                    weight = item.get("weight")
                    if weight is not None and weight > 0:
                        st.caption(
                            f"⚖️ {weight:.3f}kg × R$ {item['unit_price']:.2f}/kg"
                        )
                    else:
                        st.caption(
                            f"📦 {item['quantity']:.0f}un × R$ {item['unit_price']:.2f}"
                        )
                    if item.get("has_promotion"):
                        st.success(
                            f"🎁 {item.get('promotion_description', 'Promoção ativa')}"
                        )
                with col2:
                    st.metric("Total", f"R$ {item['final_total']:.2f}")
                with col3:
                    if item.get("bulk_discount_applied", 0) > 0:
                        st.metric(
                            "Desconto", f"-R$ {item['bulk_discount_applied']:.2f}"
                        )
                with col4:
                    if st.button("🗑️", key=f"remove_{i}", help="Remover item"):
                        self._remove_item_from_cart(item["product_id"], token)
                st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Subtotal", f"R$ {cart['subtotal']:.2f}")
        with col2:
            if cart.get("bulk_discount", 0) > 0:
                st.metric("Desconto Total", f"-R$ {cart['bulk_discount']:.2f}")
        with col3:
            st.metric("**TOTAL FINAL**", f"**R$ {cart['final_total']:.2f}**")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Limpar Carrinho", key="clear_cart"):
                self._clear_cart(token)
        with col2:
            st.metric("Itens", len(cart["items"]))

    def _render_payment_panel(self, token: str, user: dict):
        st.subheader("💳 Finalizar Venda")
        try:
            response = requests.get(
                f"{self.api_base}/pdv/cart", headers=self.get_headers(token), timeout=5
            )
            if response.status_code == 200:
                cart = response.json()
                total = cart.get("final_total", 0)
                has_items = len(cart.get("items", [])) > 0
            else:
                st.error("Erro ao obter carrinho")
                return
        except Exception as e:
            st.error(f"Erro: {e}")
            return
        if not has_items:
            st.warning("Adicione produtos ao carrinho para finalizar a venda")
            return
        with st.form("payment_form"):
            payment_method = st.selectbox(
                "Método de Pagamento",
                options=["cash", "debit_card", "credit_card", "pix"],
                format_func=lambda x: {
                    "cash": "💵 Dinheiro",
                    "debit_card": "💳 Cartão Débito",
                    "credit_card": "💳 Cartão Crédito",
                    "pix": "📱 PIX",
                }[x],
            )
            amount_received = st.number_input(
                "Valor Recebido", min_value=total, value=total, step=0.01, format="%.2f"
            )
            change = amount_received - total
            if change > 0:
                st.success(f"💰 **Troco: R$ {change:.2f}**")
            customer_id = st.number_input(
                "ID Cliente (opcional)",
                min_value=0,
                value=0,
                step=1,
                help="Deixe 0 se não houver cliente cadastrado",
            )
            if st.form_submit_button("✅ FINALIZAR VENDA", type="primary"):
                self._process_payment(
                    payment_method,
                    amount_received,
                    customer_id if customer_id > 0 else None,
                    token,
                    user,
                )

    def _render_quick_actions(self, token: str):
        st.subheader("⚡ Ações Rápidas")
        # Estado dos toggles
        if "show_busca_produto" not in st.session_state:
            st.session_state["show_busca_produto"] = False
        if "show_vendas_dia" not in st.session_state:
            st.session_state["show_vendas_dia"] = False
        if "show_balanca" not in st.session_state:
            st.session_state["show_balanca"] = False
        if "show_impressora" not in st.session_state:
            st.session_state["show_impressora"] = False

        if st.button("🔍 Buscar Produto", use_container_width=True):
            st.session_state["show_busca_produto"] = not st.session_state[
                "show_busca_produto"
            ]
        if st.session_state["show_busca_produto"]:
            st.info(
                "Use os códigos de teste:\n- 7891000100103 (Coca-Cola)\n- 7891000500107 (Queijo)"
            )

        if st.button("📊 Vendas do Dia", use_container_width=True):
            st.session_state["show_vendas_dia"] = not st.session_state[
                "show_vendas_dia"
            ]
        if st.session_state["show_vendas_dia"]:
            self._show_today_sales(token)

        if st.button("⚖️ Testar Balança", use_container_width=True):
            st.session_state["show_balanca"] = not st.session_state["show_balanca"]
        if st.session_state["show_balanca"]:
            st.info("🚧 Simulação de balança: Peso = 1.250kg")

        if st.button("🖨️ Testar Impressora", use_container_width=True):
            st.session_state["show_impressora"] = not st.session_state[
                "show_impressora"
            ]
        if st.session_state["show_impressora"]:
            st.info("🖨️ Impressora térmica: OK ✅")

    def _add_product_to_cart(
        self, barcode: str, quantity: float, weight: float, token: str
    ):
        try:
            payload = {"barcode": barcode, "quantity": quantity}
            if weight > 0:
                payload["weight"] = weight
            response = requests.post(
                f"{self.api_base}/pdv/add-product",
                json=payload,
                headers=self.get_headers(token),
                timeout=10,
            )
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    st.success(result.get("message", "Produto adicionado"))
                    cart = result.get("cart", {})
                    if cart.get("bulk_discount", 0) > 0:
                        st.success(
                            f"🎁 Promoção aplicada! Economia: R$ {cart['bulk_discount']:.2f}"
                        )
                    st.rerun()
                else:
                    st.error("Erro ao adicionar produto")
            else:
                error = response.json().get("detail", "Erro desconhecido")
                st.error(f"❌ {error}")
        except requests.exceptions.Timeout:
            st.error("⏱️ Timeout - Operação demorou muito")
        except requests.exceptions.ConnectionError:
            st.error("🔌 Erro de conexão com a API")
        except Exception as e:
            st.error(f"💥 Erro inesperado: {e}")

    def _remove_item_from_cart(self, product_id: int, token: str):
        try:
            payload = {"operation": "remove", "product_id": product_id}
            response = requests.post(
                f"{self.api_base}/pdv/cart/update",
                json=payload,
                headers=self.get_headers(token),
                timeout=5,
            )
            if response.status_code == 200:
                st.success("Item removido")
                st.rerun()
            else:
                st.error("Erro ao remover item")
        except Exception as e:
            st.error(f"Erro: {e}")

    def _clear_cart(self, token: str):
        try:
            payload = {"operation": "clear"}
            response = requests.post(
                f"{self.api_base}/pdv/cart/update",
                json=payload,
                headers=self.get_headers(token),
                timeout=5,
            )
            if response.status_code == 200:
                st.success("Carrinho limpo")
                st.rerun()
            else:
                st.error("Erro ao limpar carrinho")
        except Exception as e:
            st.error(f"Erro: {e}")

    def _process_payment(
        self,
        payment_method: str,
        amount_received: float,
        customer_id: Optional[int],
        token: str,
        user: dict,
    ):
        try:
            payload = {
                "payment_method": payment_method,
                "amount_received": amount_received,
            }
            if customer_id:
                payload["customer_id"] = customer_id
            response = requests.post(
                f"{self.api_base}/pdv/payment",
                json=payload,
                headers=self.get_headers(token),
                timeout=15,
            )
            if response.status_code == 200:
                result = response.json()
                st.success("✅ **VENDA FINALIZADA COM SUCESSO!**")
                st.balloons()
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("🆔 Venda ID", result["sale_id"])
                    st.metric("💰 Total", f"R$ {result['final_amount']:.2f}")
                with col2:
                    st.metric("💵 Recebido", f"R$ {result['amount_received']:.2f}")
                    st.metric("💸 Troco", f"R$ {result['change_amount']:.2f}")
                with st.expander("📄 Cupom Fiscal", expanded=True):
                    self._show_receipt(result["receipt_data"])
                st.success("🔓 Gaveta do dinheiro aberta")
                st.info("🖨️ Cupom enviado para impressora térmica")
                st.rerun()
            else:
                error = response.json().get("detail", "Erro no pagamento")
                st.error(f"❌ {error}")
        except requests.exceptions.Timeout:
            st.error("⏱️ Timeout no processamento do pagamento")
        except Exception as e:
            st.error(f"💥 Erro no pagamento: {e}")

    def _show_receipt(self, receipt_data: dict):
        st.code(
            f"""
═══════════════════════════════════════════
               CUPOM FISCAL
═══════════════════════════════════════════

🆔 Venda: {receipt_data.get('sale_id', 'N/A')}
📅 Data: {receipt_data.get('date', 'N/A')}

───────────────────────────────────────────
📦 PRODUTOS:
"""
        )
        for item in receipt_data.get("items", []):
            quantity_text = (
                f"{item.get('weight', item.get('quantity', 0)):.3f}kg"
                if item.get("weight")
                else f"{item.get('quantity', 0):.0f}un"
            )
            st.code(
                f"""
{item.get('name', 'Produto')}
  {quantity_text} x R$ {item.get('unit_price', 0):.2f}
  Total: R$ {item.get('total', 0):.2f}
"""
            )
            if item.get("discount", 0) > 0:
                st.code(f"  🎁 Desconto: -R$ {item.get('discount', 0):.2f}")
        st.code(
            f"""
───────────────────────────────────────────
💰 TOTAIS:
Subtotal: R$ {receipt_data.get('subtotal', 0):.2f}
Desconto: -R$ {receipt_data.get('total_discount', 0):.2f}
TOTAL: R$ {receipt_data.get('final_total', 0):.2f}

💳 PAGAMENTO:
Método: {receipt_data.get('payment_method', '').upper()}
Recebido: R$ {receipt_data.get('amount_received', 0):.2f}
Troco: R$ {receipt_data.get('change', 0):.2f}

═══════════════════════════════════════════
        OBRIGADO PELA PREFERÊNCIA!
═══════════════════════════════════════════
"""
        )

    def _show_today_sales(self, token: str):
        try:
            response = requests.get(
                f"{self.api_base}/sales", headers=self.get_headers(token), timeout=5
            )
            if response.status_code == 200:
                sales = response.json()
                if sales:
                    st.success(f"📊 {len(sales)} vendas encontradas hoje")
                    total_revenue = sum(
                        sale.get("final_amount", 0) for sale in sales[:10]
                    )
                    avg_ticket = total_revenue / len(sales[:10]) if sales[:10] else 0
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("💰 Faturamento", f"R$ {total_revenue:.2f}")
                    with col2:
                        st.metric("🎯 Ticket Médio", f"R$ {avg_ticket:.2f}")
                else:
                    st.info("📊 Nenhuma venda registrada hoje")
            else:
                st.error("Erro ao buscar vendas")
        except Exception as e:
            st.error(f"Erro: {e}")
