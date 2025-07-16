"""
Interface Streamlit - Sistema de Supermercado
Aplicação principal com sistema de login
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import requests
import streamlit as st

# Adicionar path do projeto
sys.path.append(str(Path(__file__).parent.parent.parent))

# Configuração da página
st.set_page_config(
    page_title="Sistema de Supermercado",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
    .css-1d391kg { padding-top: 0rem; }
    .login-container { background: linear-gradient(135deg, #1f77b4 0%, #e74c3c 100%); padding: 3rem; border-radius: 20px; color: white; text-align: center; margin: 2rem 0; box-shadow: 0 15px 35px rgba(0,0,0,0.1); }
    .login-form { background: rgba(255, 255, 255, 0.1); padding: 2rem; border-radius: 15px; backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.2); }
    .main-header { background: linear-gradient(90deg, #1f77b4, #e74c3c); padding: 1.5rem; border-radius: 15px; color: white; text-align: center; margin-bottom: 2rem; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
    .metric-card { background: #f8f9fa; padding: 1.5rem; border-radius: 12px; border-left: 5px solid #1f77b4; margin: 1rem 0; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .success-box { background: #d1ecf1; color: #0c5460; padding: 1rem; border-radius: 8px; border-left: 4px solid #17a2b8; margin: 1rem 0; }
    .error-box { background: #f8d7da; color: #721c24; padding: 1rem; border-radius: 8px; border-left: 4px solid #dc3545; margin: 1rem 0; }
    .warning-box { background: #fff3cd; color: #856404; padding: 1rem; border-radius: 8px; border-left: 4px solid #ffc107; margin: 1rem 0; }
    .sidebar .sidebar-content { background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%); }
    .stButton > button { background: linear-gradient(90deg, #1f77b4, #e74c3c); color: white; border: none; border-radius: 8px; padding: 0.5rem 1rem; font-weight: bold; }
    .not-logged-in .css-1d391kg { padding: 0; }
</style>
""",
    unsafe_allow_html=True,
)


class AuthService:
    """Serviço de autenticação"""

    def __init__(self):
        self.api_base = "http://localhost:8000/api/v1"

    def login(self, username: str, password: str) -> Dict[str, Any]:
        try:
            payload = {"username": username, "password": password}
            response = requests.post(
                f"{self.api_base}/auth/login", json=payload, timeout=10
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                error_detail = response.json().get("detail", "Erro desconhecido")
                return {"success": False, "error": error_detail}
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Não foi possível conectar à API. Verifique se está rodando.",
            }
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Timeout na conexão. Tente novamente."}
        except Exception as e:
            return {"success": False, "error": f"Erro inesperado: {str(e)}"}

    def check_api_status(self) -> Dict[str, Any]:
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                return response.json()
            return {"status": "error", "message": "API retornou erro"}
        except:
            return {"status": "error", "message": "API indisponível"}


def show_login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
        <div style='position:fixed;top:0;left:0;right:0;z-index:1000;background:linear-gradient(90deg,#1f77b4,#e74c3c);padding:1.2rem 0 1.2rem 0;text-align:center;color:white;box-shadow:0 2px 10px rgba(0,0,0,0.08);'>
            <h1 style='margin:0;font-size:2rem;display:inline-block;vertical-align:middle;'>🛒 O Barateiro</h1><br>
            <span style='font-size:1.1em;opacity:0.9;'>Atacado e varejo</span>
        </div>
        <div style='height:90px;'></div>
        """,
            unsafe_allow_html=True,
        )
        auth_service = AuthService()
        api_status = auth_service.check_api_status()
        if api_status.get("status") != "healthy":
            st.markdown(
                """
            <div class="error-box">
                <h4>❌ API Indisponível</h4>
                <p>Para usar o sistema, execute:</p>
                <code>uvicorn app.main:app --reload</code>
            </div>
            """,
                unsafe_allow_html=True,
            )
            if st.button("🔄 Tentar Novamente"):
                st.rerun()
            return
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "👤 Usuário",
                placeholder="Digite seu usuário",
                help="Use 'admin' para teste",
            )
            password = st.text_input(
                "🔒 Senha",
                type="password",
                placeholder="Digite sua senha",
                help="Use 'admin123' para teste",
            )
            login_button = st.form_submit_button(
                "🔓 Entrar no Sistema", type="primary", use_container_width=True
            )
            if login_button and username and password:
                with st.spinner("Verificando credenciais..."):
                    result = auth_service.login(username, password)
                    if result["success"]:
                        user_data = result["data"]
                        st.session_state.logged_in = True
                        st.session_state.user = user_data["user"]
                        st.session_state.token = user_data["access_token"]
                        st.session_state.login_time = datetime.now()
                        st.success(f"✅ Bem-vindo, {user_data['user']['full_name']}!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ {result['error']}")
        st.markdown(
            """
        <div style="text-align: center; margin-top: 3rem; opacity: 0.7;">
            <p>Sistema de Gestão de Supermercado v1.0</p>
        </div>
        """,
            unsafe_allow_html=True,
        )


def show_main_app():
    user = st.session_state.user
    st.markdown(
        f"""
    <div class="main-header">
        <h1>🛒 O Barateiro</h1>
        <p>Bem-vindo, <strong>{user['full_name']}</strong> ({user['role'].upper()})</p>
    </div>
    """,
        unsafe_allow_html=True,
    )
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50/1f77b4/white?text=LOGO", width=150)
        st.markdown(
            f"""
        ### 👤 Usuário Logado
        **{user['full_name']}**
        📧 {user['email']}
        🎭 {user['role'].upper()}
        ⏰ Login: {st.session_state.login_time.strftime('%H:%M')}
        """
        )
        st.divider()
        if user["role"] in ["admin", "manager"]:
            page_options = [
                "🏠 Dashboard",
                "🛒 PDV - Ponto de Venda",
                "📦 Gestão de Produtos",
                "📊 Relatório de Vendas",
                "👥 Gestão de Usuários",
                "⚙️ Configurações",
                "🧪 Testes do Sistema",
            ]
        elif user["role"] == "supervisor":
            page_options = [
                "🏠 Dashboard",
                "🛒 PDV - Ponto de Venda",
                "📦 Consulta de Produtos",
                "📊 Relatório de Vendas",
                "🧪 Testes do Sistema",
            ]
        else:
            page_options = [
                "🛒 PDV - Ponto de Venda",
                "📦 Consulta de Produtos",
                "🧪 Testes do Sistema",
            ]
        # Controle de navegação centralizado via session_state
        if "selected_page" not in st.session_state:
            st.session_state["selected_page"] = page_options[0]
        selected_page = st.selectbox(
            "📋 Navegação",
            page_options,
            index=page_options.index(st.session_state["selected_page"])
            if st.session_state["selected_page"] in page_options
            else 0,
        )
        # Atualiza a página selecionada se o usuário mudar manualmente
        if selected_page != st.session_state["selected_page"]:
            st.session_state["selected_page"] = selected_page
            st.experimental_rerun()
        st.divider()
        show_system_status_sidebar()
        st.divider()
        if st.button("🚪 Sair do Sistema", use_container_width=True, type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("Logout realizado!")
            st.rerun()
    route_page(st.session_state["selected_page"])


def show_system_status_sidebar():
    try:
        response = requests.get("http://localhost:8000/health", timeout=3)
        if response.status_code == 200:
            api_status = response.json()
            st.markdown("### 📊 Status do Sistema")
            counts = api_status.get("counts", {})
            st.metric("👥 Usuários", counts.get("users", 0))
            st.metric("📦 Produtos", counts.get("products", 0))
            st.metric("🛒 Vendas", counts.get("sales", 0))
            alerts = api_status.get("alerts", {})
            low_stock = counts.get("low_stock_products", 0)
            if low_stock > 0:
                st.warning(f"⚠️ {low_stock} produtos com estoque baixo")
            else:
                st.success("✅ Estoque OK")
        else:
            st.error("❌ API com problemas")
    except:
        st.error("❌ API desconectada")


def route_page(page: str):
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "🛒 PDV - Ponto de Venda":
        show_pdv()
    elif "📦" in page:
        if st.session_state.user["role"] in ["admin", "manager"]:
            show_products_management()
        else:
            show_products_view()
    elif page == "📊 Relatório de Vendas":
        show_sales_report()
    elif page == "👥 Gestão de Usuários":
        show_users_management()
    elif page == "⚙️ Configurações":
        show_settings()
    elif page == "🧪 Testes do Sistema":
        show_tests()


def show_dashboard():
    st.header("🏠 Dashboard")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            st.error("Erro ao carregar dados do sistema")
            return
        api_status = response.json()
        counts = api_status.get("counts", {})
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                label="👥 Usuários Ativos",
                value=counts.get("users", 0),
                help="Total de usuários cadastrados no sistema",
            )
        with col2:
            st.metric(
                label="📦 Produtos",
                value=counts.get("products", 0),
                help="Produtos ativos disponíveis para venda",
            )
        with col3:
            st.metric(
                label="🛒 Vendas Hoje",
                value=counts.get("sales", 0),
                help="Total de vendas realizadas",
            )
        with col4:
            low_stock = counts.get("low_stock_products", 0)
            st.metric(
                label="⚠️ Estoque Baixo",
                value=low_stock,
                delta=f"-{low_stock}" if low_stock > 0 else "OK",
                delta_color="inverse",
                help="Produtos com estoque abaixo do mínimo",
            )
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🔋 Status dos Recursos")
            features = api_status.get("features", {})
            # Mapeamento dos nomes dos recursos para português
            feature_translation = {
                "api": "API",
                "banco_de_dados": "Banco de Dados",
                "database": "Banco de Dados",
                "impressora": "Impressora",
                "printer": "Impressora",
                "leitor_de_codigo_de_barras": "Leitor de Código de Barras",
                "barcode_reader": "Leitor de Código de Barras",
                "balanca": "Balança",
                "scale": "Balança",
                "hardware": "Hardware",
                "produtos": "Produtos",
                "products": "Produtos",
                "usuarios": "Usuários",
                "users": "Usuários",
                "vendas": "Vendas",
                "sales": "Vendas",
            }
            for feature, status in features.items():
                # Traduzir o nome do recurso se houver tradução, senão formatar para português
                feature_pt = feature_translation.get(
                    feature.lower(), feature.replace("_", " ").capitalize()
                )
                if "✅" in status:
                    st.success(f"{status} {feature_pt}")
                else:
                    st.warning(f"{status} {feature_pt}")
        with col2:
            st.subheader("📈 Ações Rápidas")
            if st.button("🛒 Abrir PDV", use_container_width=True, key="abrir_pdv_btn"):
                st.session_state["selected_page"] = "🛒 PDV - Ponto de Venda"
                st.experimental_rerun()
            if st.button(
                "📦 Ver Produtos", use_container_width=True, key="ver_produtos_btn"
            ):
                # Seleciona a página correta conforme o perfil
                if st.session_state.user["role"] in ["admin", "manager"]:
                    st.session_state["selected_page"] = "📦 Gestão de Produtos"
                else:
                    st.session_state["selected_page"] = "📦 Consulta de Produtos"
                st.experimental_rerun()
            if low_stock > 0:
                if st.button(
                    f"⚠️ Ver {low_stock} Produtos em Falta",
                    use_container_width=True,
                    key="ver_falta_btn",
                ):
                    if st.session_state.user["role"] in ["admin", "manager"]:
                        st.session_state["selected_page"] = "📦 Gestão de Produtos"
                    else:
                        st.session_state["selected_page"] = "📦 Consulta de Produtos"
                    st.experimental_rerun()
            if st.button(
                "📊 Relatórios", use_container_width=True, key="ver_relatorios_btn"
            ):
                st.session_state["selected_page"] = "📊 Relatório de Vendas"
                st.experimental_rerun()
        if low_stock > 0:
            st.warning(
                f"⚠️ **Atenção:** {low_stock} produto(s) com estoque baixo precisam de reposição!"
            )
    except Exception as e:
        st.error(f"Erro ao carregar dashboard: {e}")


def show_pdv():
    st.header("🛒 PDV - Ponto de Venda")
    from pages.pdv import PDVInterface

    pdv = PDVInterface()
    pdv.render_authenticated(st.session_state.user, st.session_state.token)


def show_products_management():
    st.header("📦 Gestão de Produtos")
    st.info("🚧 Interface em desenvolvimento - Use a API: http://localhost:8000/docs")


def show_products_view():
    st.header("📦 Consulta de Produtos")
    st.info("🚧 Interface em desenvolvimento - Use a API: http://localhost:8000/docs")


def show_sales_report():
    st.header("📊 Relatório de Vendas")
    st.info("🚧 Interface em desenvolvimento - Use a API: http://localhost:8000/docs")


def show_users_management():
    st.header("👥 Gestão de Usuários")
    st.info("🚧 Interface em desenvolvimento - Use a API: http://localhost:8000/docs")


def show_settings():
    st.header("⚙️ Configurações do Sistema")
    st.info("🚧 Interface em desenvolvimento")


def show_tests():
    st.header("🧪 Testes do Sistema")
    from pages.tests import TestInterface

    test_interface = TestInterface()
    test_interface.render()


def main():
    if not st.session_state.get("logged_in", False):
        show_login_page()
    else:
        show_main_app()


if __name__ == "__main__":
    main()
