from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db

print("DEBUG: reports.py - Arquivo simplificado de relatórios carregado")

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """
    Dashboard simplificado usando SQL direto
    """
    print(
        f"DEBUG: /dashboard - Iniciando para usuário {current_user.username if hasattr(current_user, 'username') else 'desconhecido'}"
    )

    try:
        # Total de vendas
        print("DEBUG: Executando query - total de vendas")
        print("DEBUG: Query: SELECT COUNT(*) FROM sales WHERE status = 'COMPLETED'")
        total_sales_result = db.execute(
            text("SELECT COUNT(*) FROM sales WHERE status = 'COMPLETED'")
        )
        total_sales = total_sales_result.scalar() or 0
        print(f"DEBUG: Total de vendas RESULTADO: {total_sales}")

        # Receita total
        print("DEBUG: Executando query - receita total")
        print(
            "DEBUG: Query: SELECT COALESCE(SUM(final_amount), 0) FROM sales WHERE status = 'COMPLETED'"
        )
        total_revenue_result = db.execute(
            text(
                "SELECT COALESCE(SUM(final_amount), 0) FROM sales WHERE status = 'COMPLETED'"
            )
        )
        total_revenue = float(total_revenue_result.scalar() or 0.0)
        print(f"DEBUG: Receita total RESULTADO: {total_revenue}")

        # Total de produtos
        print("DEBUG: Executando query - total de produtos")
        print("DEBUG: Query: SELECT COUNT(*) FROM products")
        total_products_result = db.execute(text("SELECT COUNT(*) FROM products"))
        total_products = total_products_result.scalar() or 0
        print(f"DEBUG: Total de produtos RESULTADO: {total_products}")

        # Alertas de estoque baixo (produtos com quantidade < 10)
        print("DEBUG: Executando query - alertas de estoque")
        print("DEBUG: Query: SELECT COUNT(*) FROM products WHERE stock_quantity < 10")
        low_stock_result = db.execute(
            text("SELECT COUNT(*) FROM products WHERE stock_quantity < 10")
        )
        low_stock_alerts = low_stock_result.scalar() or 0
        print(f"DEBUG: Alertas de estoque baixo RESULTADO: {low_stock_alerts}")

        # Vendas recentes (últimas 5)
        print("DEBUG: Executando query - vendas recentes")
        print(
            "DEBUG: Query: SELECT id, final_amount, created_at FROM sales WHERE status = 'COMPLETED' ORDER BY created_at DESC LIMIT 5"
        )
        recent_sales_result = db.execute(
            text(
                """
            SELECT id, final_amount, created_at
            FROM sales
            WHERE status = 'COMPLETED'
            ORDER BY created_at DESC
            LIMIT 5
        """
            )
        )
        recent_sales = []
        for row in recent_sales_result:
            recent_sales.append(
                {
                    "id": row[0],
                    "total": float(row[1]),
                    "created_at": row[2].isoformat() if row[2] else None,
                }
            )
        print(f"DEBUG: Vendas recentes encontradas RESULTADO: {len(recent_sales)}")

        dashboard_data = {
            "today_sales": total_sales,  # ✅ Corrigido: total_sales -> today_sales
            "total_revenue": total_revenue,
            "products_sold": total_products,  # ✅ Corrigido: total_products -> products_sold
            "customers_served": total_sales,  # ✅ Adicionado: aproximação baseada em vendas
            "average_ticket": round(total_revenue / total_sales, 2)
            if total_sales > 0
            else 0.0,  # ✅ Adicionado
            "low_stock_alerts": low_stock_alerts,
            "recent_sales": recent_sales,
            "top_products": [],  # Implementar depois se necessário
            "sales_by_period": {
                "daily": total_sales,  # Simplificado por enquanto
                "weekly": total_sales,
                "monthly": total_sales,
            },
        }

        print(f"DEBUG: /dashboard - Dados finais RESULTADO: {dashboard_data}")
        return dashboard_data

    except Exception as e:
        print(f"DEBUG: /dashboard - Erro: {e}")
        import traceback

        traceback.print_exc()

        return {
            "today_sales": 0,
            "total_revenue": 0.0,
            "products_sold": 0,
            "customers_served": 0,
            "average_ticket": 0.0,
            "low_stock_alerts": 0,
            "recent_sales": [],
            "top_products": [],
            "sales_by_period": {"daily": 0, "weekly": 0, "monthly": 0},
        }


@router.get("/kpis")
async def get_kpis(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """
    KPIs usando SQL direto
    """
    print("DEBUG: /kpis - Iniciando")

    try:
        total_sales_result = db.execute(
            text("SELECT COUNT(*) FROM sales WHERE status = 'COMPLETED'")
        )
        total_sales = total_sales_result.scalar() or 0

        total_revenue_result = db.execute(
            text(
                "SELECT COALESCE(SUM(final_amount), 0) FROM sales WHERE status = 'COMPLETED'"
            )
        )
        total_revenue = float(total_revenue_result.scalar() or 0.0)

        total_products_result = db.execute(text("SELECT COUNT(*) FROM products"))
        total_products = total_products_result.scalar() or 0

        low_stock_result = db.execute(
            text("SELECT COUNT(*) FROM products WHERE stock_quantity < 10")
        )
        low_stock_alerts = low_stock_result.scalar() or 0

        kpis = {
            "total_sales": total_sales,
            "total_revenue": total_revenue,
            "total_products": total_products,
            "low_stock_alerts": low_stock_alerts,
        }

        print(f"DEBUG: /kpis - Retornando: {kpis}")
        return kpis

    except Exception as e:
        print(f"DEBUG: /kpis - Erro: {e}")
        return {
            "total_sales": 0,
            "total_revenue": 0.0,
            "total_products": 0,
            "low_stock_alerts": 0,
        }


@router.get("/sales")
async def get_sales_report(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """
    Relatório de vendas simplificado
    """
    print("DEBUG: /sales - Iniciando")

    try:
        sales_result = db.execute(
            text(
                """
            SELECT id, final_amount, created_at, status
            FROM sales
            WHERE status = 'COMPLETED'
            ORDER BY created_at DESC
            LIMIT 20
        """
            )
        )

        sales = []
        for row in sales_result:
            sales.append(
                {
                    "id": row[0],
                    "total": float(row[1]),
                    "created_at": row[2].isoformat() if row[2] else None,
                    "status": row[3],
                }
            )

        print(f"DEBUG: /sales - Encontradas {len(sales)} vendas")
        return {"sales": sales}

    except Exception as e:
        print(f"DEBUG: /sales - Erro: {e}")
        return {"sales": []}


@router.get("/stock-alerts")
async def get_stock_alerts(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """
    Alertas de estoque usando SQL direto
    """
    print("DEBUG: /stock-alerts - Iniciando")

    try:
        # Produtos com estoque baixo
        alerts_result = db.execute(
            text(
                """
            SELECT name, stock_quantity, min_stock_level
            FROM products
            WHERE stock_quantity < 10
            ORDER BY stock_quantity ASC
        """
            )
        )

        alerts = []
        for row in alerts_result:
            alerts.append(
                {
                    "product_name": row[0],
                    "current_quantity": row[1],
                    "min_stock": row[2] if row[2] else 10,
                }
            )

        alerts_count = len(alerts)
        print(f"DEBUG: /stock-alerts - Encontrados {alerts_count} alertas")

        return {"alerts_count": alerts_count, "alerts": alerts}

    except Exception as e:
        print(f"DEBUG: /stock-alerts - Erro: {e}")
        return {"alerts_count": 0, "alerts": []}
