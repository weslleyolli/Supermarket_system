"""
Interface de testes para Streamlit
"""

import json

import requests
import streamlit as st


class TestInterface:
    """Interface de testes do sistema"""

    def __init__(self):
        self.api_base = "http://localhost:8000/api/v1"

    def render(self):
        st.markdown(
            """
            <div style='position: absolute; top: 1.5rem; left: 1.5rem; z-index: 1000;'>
                <span style='font-size:1.3em; color:#1f77b4; font-weight:bold; cursor:default;'>
                    ← Voltar
                </span>
            </div>
        """,
            unsafe_allow_html=True,
        )
        st.markdown("### 🧪 Testes Rápidos do Sistema")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🔍 Testes de API")
            if st.button("🏥 Health Check"):
                self._test_health()
            if st.button("📦 Listar Produtos"):
                self._test_list_products()
            if st.button("🏷️ Listar Categorias"):
                self._test_list_categories()
        with col2:
            st.subheader("🛒 Testes de PDV")
            if st.button("🔍 Buscar por Código"):
                self._test_barcode_search()
            if st.button("📊 Status do Carrinho"):
                self._test_cart_status()
        st.subheader("🔧 Teste Personalizado")
        with st.form("custom_test"):
            endpoint = st.selectbox(
                "Endpoint",
                options=[
                    "/health",
                    "/api/v1/products",
                    "/api/v1/products/categories",
                    "/api/v1/products/search",
                    "/api/v1/pdv/cart",
                ],
            )
            method = st.selectbox("Método", ["GET", "POST"])
            if method == "POST":
                body = st.text_area("Body (JSON)", value="{}")
            if st.form_submit_button("🚀 Executar"):
                url = f"http://localhost:8000{endpoint}"
                try:
                    if method == "GET":
                        response = requests.get(url, timeout=5)
                    else:
                        data = json.loads(body) if body else {}
                        response = requests.post(url, json=data, timeout=5)
                    st.code(f"Status: {response.status_code}")
                    st.json(response.json())
                except requests.exceptions.RequestException as e:
                    st.error(f"Erro de conexão: {e}")
                except json.JSONDecodeError as e:
                    st.error(f"Erro no JSON: {e}")
        st.subheader("📋 Códigos para Teste")
        test_codes = {
            "Coca-Cola 2L (com promoção)": "7891000100103",
            "Queijo Mussarela (por peso)": "7891000500107",
            "Alcatra Bovina (por peso)": "7891000800",
            "Água Crystal (com promoção)": "7891000200104",
            "Detergente Ypê (com promoção)": "7891001600118",
        }
        for name, code in test_codes.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text(f"{name}")
            with col2:
                st.code(code)

    def _test_health(self):
        """Testa health check"""
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                st.success("✅ API funcionando!")
                st.json(data)
            else:
                st.error(f"❌ Erro: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Erro de conexão: {e}")

    def _test_list_products(self):
        """Testa listagem de produtos"""
        try:
            response = requests.get(f"{self.api_base}/products", timeout=5)
            if response.status_code == 200:
                products = response.json()
                st.success(f"✅ Encontrados {len(products)} produtos")
                if products:
                    for product in products[:3]:
                        st.write(
                            f"• {product['name']} - {product['barcode']} - R$ {product['price']:.2f}"
                        )
                else:
                    st.warning(
                        "Nenhum produto encontrado. Execute: `python scripts/create_sample_products.py`"
                    )
            else:
                st.error(f"❌ Erro: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Erro: {e}")

    def _test_list_categories(self):
        """Testa listagem de categorias"""
        try:
            response = requests.get(f"{self.api_base}/products/categories", timeout=5)
            if response.status_code == 200:
                categories = response.json()
                st.success(f"✅ Encontradas {len(categories)} categorias")
                for category in categories:
                    st.write(
                        f"• {category['name']} ({category.get('products_count', 0)} produtos)"
                    )
            else:
                st.error(f"❌ Erro: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Erro: {e}")

    def _test_barcode_search(self):
        """Testa busca por código de barras"""
        try:
            test_barcode = "7891000100103"
            payload = {"barcode": test_barcode}
            response = requests.post(
                f"{self.api_base}/products/barcode-search", json=payload, timeout=5
            )
            if response.status_code == 200:
                product = response.json()
                st.success(f"✅ Produto encontrado: {product['name']}")
                st.write(f"Preço: R$ {product['price']:.2f}")
                st.write(f"Estoque: {product['stock_quantity']}")
                if product.get("has_promotion"):
                    st.write(f"🎁 Promoção ativa!")
            else:
                st.error("❌ Produto não encontrado ou erro na API")
        except Exception as e:
            st.error(f"❌ Erro: {e}")

    def _test_cart_status(self):
        """Testa status do carrinho"""
        try:
            response = requests.get(f"{self.api_base}/pdv/cart", timeout=5)
            if response.status_code == 200:
                cart = response.json()
                st.success("✅ Carrinho acessível")
                st.write(f"Itens: {len(cart.get('items', []))}")
                st.write(f"Total: R$ {cart.get('final_total', 0):.2f}")
            else:
                st.error(f"❌ Erro: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Erro: {e}")
