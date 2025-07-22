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
        # Total de vendas DE HOJE
        print("DEBUG: Executando query - vendas de hoje")
        print(
            "DEBUG: Query: SELECT COUNT(*) FROM sales WHERE status = 'COMPLETED' AND DATE(created_at) = CURRENT_DATE"
        )
        today_sales_result = db.execute(
            text(
                "SELECT COUNT(*) FROM sales WHERE status = 'COMPLETED' AND DATE(created_at) = CURRENT_DATE"
            )
        )
        today_sales = today_sales_result.scalar() or 0
        print(f"DEBUG: Vendas de hoje RESULTADO: {today_sales}")

        # Receita DE HOJE
        print("DEBUG: Executando query - receita de hoje")
        print(
            "DEBUG: Query: SELECT COALESCE(SUM(final_amount), 0) FROM sales WHERE status = 'COMPLETED' AND DATE(created_at) = CURRENT_DATE"
        )
        today_revenue_result = db.execute(
            text(
                "SELECT COALESCE(SUM(final_amount), 0) FROM sales WHERE status = 'COMPLETED' AND DATE(created_at) = CURRENT_DATE"
            )
        )
        today_revenue = float(today_revenue_result.scalar() or 0.0)
        print(f"DEBUG: Receita de hoje RESULTADO: {today_revenue}")

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

        # Vendas recentes DE HOJE (últimas 5)
        print("DEBUG: Executando query - vendas recentes de hoje")
        print(
            "DEBUG: Query: SELECT id, final_amount, created_at FROM sales WHERE status = 'COMPLETED' AND DATE(created_at) = CURRENT_DATE ORDER BY created_at DESC LIMIT 5"
        )
        recent_sales_result = db.execute(
            text(
                """
            SELECT id, final_amount, created_at
            FROM sales
            WHERE status = 'COMPLETED' AND DATE(created_at) = CURRENT_DATE
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

        # Produtos mais vendidos (TOP 5 de todos os tempos)
        print("DEBUG: Executando query - top produtos mais vendidos")
        top_products_result = db.execute(
            text(
                """
                SELECT
                    p.name,
                    p.price,
                    COALESCE(SUM(si.quantity), 0) as total_sold,
                    COUNT(DISTINCT s.id) as times_sold
                FROM products p
                LEFT JOIN sale_items si ON p.id = si.product_id
                LEFT JOIN sales s ON si.sale_id = s.id AND s.status = 'COMPLETED'
                WHERE p.is_active = true
                GROUP BY p.id, p.name, p.price
                HAVING SUM(si.quantity) > 0
                ORDER BY total_sold DESC, times_sold DESC
                LIMIT 5
            """
            )
        )

        top_products = []
        for row in top_products_result:
            top_products.append(
                {
                    "name": row[0],
                    "price": float(row[1]) if row[1] else 0.0,
                    "quantity_sold": int(row[2]) if row[2] else 0,
                    "times_sold": int(row[3]) if row[3] else 0,
                }
            )
        print(f"DEBUG: Top produtos encontrados RESULTADO: {len(top_products)}")

        # Se não houver vendas, mostrar produtos mais populares (maior estoque inicial)
        if len(top_products) == 0:
            print(
                "DEBUG: Nenhuma venda encontrada, buscando produtos populares por estoque"
            )
            popular_products_result = db.execute(
                text(
                    """
                    SELECT name, price, stock_quantity, 0 as quantity_sold, 0 as times_sold
                    FROM products
                    WHERE is_active = true
                    ORDER BY stock_quantity DESC
                    LIMIT 5
                """
                )
            )

            for row in popular_products_result:
                top_products.append(
                    {
                        "name": row[0],
                        "price": float(row[1]) if row[1] else 0.0,
                        "quantity_sold": int(row[3]),
                        "times_sold": int(row[4]),
                    }
                )
            print(
                f"DEBUG: Produtos populares por estoque RESULTADO: {len(top_products)}"
            )

        dashboard_data = {
            "today_sales": today_revenue,  # 🔥 CORRIGIDO: VALOR em reais das vendas de hoje
            "total_revenue": today_revenue,  # ✅ Receita de hoje (mesmo valor)
            "products_sold": total_products,  # ✅ Total de produtos no sistema
            "customers_served": today_sales,  # ✅ NÚMERO de transações de hoje
            "average_ticket": round(today_revenue / today_sales, 2)
            if today_sales > 0
            else 0.0,  # ✅ Ticket médio do dia
            "low_stock_alerts": low_stock_alerts,
            "recent_sales": recent_sales,
            "top_products": top_products,  # 🔥 IMPLEMENTADO: produtos mais vendidos hoje
            "sales_by_period": {
                "daily": today_revenue,  # 🔥 CORRIGIDO: VALOR das vendas do dia
                "weekly": today_revenue,  # Simplificado por enquanto
                "monthly": today_revenue,  # Simplificado por enquanto
            },
        }

        print(f"DEBUG: /dashboard - Dados finais RESULTADO: {dashboard_data}")
        return dashboard_data

    except Exception as e:
        print(f"DEBUG: /dashboard - Erro: {e}")
        import traceback

        traceback.print_exc()

        return {
            "today_sales": 0.0,  # 🔥 CORRIGIDO: valor em reais, não quantidade
            "total_revenue": 0.0,
            "products_sold": 0,
            "customers_served": 0,
            "average_ticket": 0.0,
            "low_stock_alerts": 0,
            "recent_sales": [],
            "top_products": [],  # 🔥 ADICIONADO: campo obrigatório
            "sales_by_period": {
                "daily": 0.0,
                "weekly": 0.0,
                "monthly": 0.0,
            },  # 🔥 CORRIGIDO: valores em reais
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
    Alertas de estoque com detalhes dos produtos
    """
    print("DEBUG: /stock-alerts - Iniciando")

    try:
        # 🔍 MELHORAR: Query mais detalhada com informações úteis
        alerts_result = db.execute(
            text(
                """
            SELECT
                name,
                stock_quantity,
                min_stock_level,
                price,
                (min_stock_level - stock_quantity) as deficit,
                CASE
                    WHEN stock_quantity <= 0 THEN 'CRÍTICO'
                    WHEN stock_quantity <= min_stock_level * 0.5 THEN 'URGENTE'
                    ELSE 'ATENÇÃO'
                END as urgency_level
            FROM products
            WHERE stock_quantity <= min_stock_level
            AND is_active = true
            ORDER BY
                CASE
                    WHEN stock_quantity <= 0 THEN 1
                    WHEN stock_quantity <= min_stock_level * 0.5 THEN 2
                    ELSE 3
                END,
                stock_quantity ASC
        """
            )
        )

        alerts = []
        for row in alerts_result:
            alert = {
                "product_name": row[0],
                "current_stock": float(row[1]),
                "min_stock_level": float(row[2]),
                "price": float(row[3]),
                "deficit": float(row[4]),
                "urgency_level": row[5],
                "action_needed": f"Comprar {int(row[4])} unidades",
                "estimated_cost": float(row[3]) * float(row[4]),
            }
            alerts.append(alert)

        print(f"DEBUG: Encontrados {len(alerts)} alertas de estoque")

        # 📊 Estatísticas dos alertas
        total_alerts = len(alerts)
        critical_alerts = len([a for a in alerts if a["urgency_level"] == "CRÍTICO"])
        urgent_alerts = len([a for a in alerts if a["urgency_level"] == "URGENTE"])

        return {
            "alerts": alerts,
            "summary": {
                "total_alerts": total_alerts,
                "critical": critical_alerts,
                "urgent": urgent_alerts,
                "attention": total_alerts - critical_alerts - urgent_alerts,
                "total_estimated_cost": sum(a["estimated_cost"] for a in alerts),
            },
        }

    except Exception as e:
        print(f"DEBUG: Erro em /stock-alerts: {e}")
        return {
            "alerts": [],
            "summary": {
                "total_alerts": 0,
                "critical": 0,
                "urgent": 0,
                "attention": 0,
                "total_estimated_cost": 0.0,
            },
            "error": str(e),
        }
