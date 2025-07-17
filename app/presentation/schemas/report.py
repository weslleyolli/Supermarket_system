from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel


class DashboardKPIs(BaseModel):
    """KPIs principais do dashboard"""

    today_sales: float
    today_transactions: int
    products_sold: int
    customers_served: int
    average_ticket: float
    # Comparações com período anterior
    sales_trend: float  # % mudança
    transactions_trend: float
    products_trend: float
    customers_trend: float
    ticket_trend: float


class TopProduct(BaseModel):
    """Produto mais vendido"""

    product_id: int
    product_name: str
    category_name: str
    quantity_sold: float
    revenue: float
    profit: float


class DailySales(BaseModel):
    """Vendas por dia"""

    date: date
    total_sales: float
    total_transactions: int
    total_products: int
    average_ticket: float


class StockAlert(BaseModel):
    """Alerta de estoque"""

    product_id: int
    product_name: str
    category_name: str
    current_stock: float
    min_stock: float
    stock_status: str  # "critical", "low", "ok"
    days_to_stockout: Optional[int]


class SalesGoal(BaseModel):
    """Meta de vendas"""

    period: str  # "daily", "weekly", "monthly"
    goal_amount: float
    current_amount: float
    achievement_percentage: float
    status: str  # "on_track", "behind", "exceeded"


class CategoryPerformance(BaseModel):
    """Performance por categoria"""

    category_id: int
    category_name: str
    total_sales: float
    total_products: int
    profit_margin: float
    growth_percentage: float


class HourlyAnalysis(BaseModel):
    """Análise por hora do dia"""

    hour: int
    sales_amount: float
    transactions_count: int
    average_ticket: float


class DashboardResponse(BaseModel):
    """Resposta completa do dashboard"""

    kpis: DashboardKPIs
    top_products: List[TopProduct]
    daily_sales: List[DailySales]
    stock_alerts: List[StockAlert]
    sales_goals: List[SalesGoal]
    category_performance: List[CategoryPerformance]
    hourly_analysis: List[HourlyAnalysis]
    # Metadados
    last_updated: datetime
    period_start: date
    period_end: date


class SalesReportFilters(BaseModel):
    """Filtros para relatório de vendas"""

    start_date: Optional[date] = None
    end_date: Optional[date] = None
    category_id: Optional[int] = None
    cashier_id: Optional[int] = None
    payment_method: Optional[str] = None
    group_by: str = "day"  # "hour", "day", "week", "month"


class SalesReportData(BaseModel):
    """Dados do relatório de vendas"""

    period: str
    total_sales: float
    total_transactions: int
    total_products: int
    total_profit: float
    average_ticket: float
    top_payment_method: str


class SalesReportResponse(BaseModel):
    """Resposta do relatório de vendas"""

    summary: SalesReportData
    data_points: List[DailySales]
    top_products: List[TopProduct]
    category_breakdown: List[CategoryPerformance]
