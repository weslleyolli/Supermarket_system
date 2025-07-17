from datetime import date, datetime
from typing import Optional

from app.infrastructure.repositories.report_repository import ReportRepository
from app.presentation.schemas.report import (
    CategoryPerformance,
    DailySales,
    DashboardKPIs,
    DashboardResponse,
    HourlyAnalysis,
    SalesGoal,
    SalesReportData,
    SalesReportFilters,
    SalesReportResponse,
    StockAlert,
    TopProduct,
)


class ReportService:
    """Serviço de relatórios e dashboard"""

    def __init__(self, db):
        self.db = db
        self.repo = ReportRepository(db)

    def get_dashboard_data(
        self, target_date: Optional[date] = None
    ) -> DashboardResponse:
        try:
            print(
                f"📊 ReportService: Iniciando geração do dashboard para data: {target_date}"
            )

            # KPIs do dia
            print("🔄 Buscando KPIs do dia...")
            kpis_dict = self.repo.get_today_kpis(target_date)
            print(f"✅ KPIs obtidos: {kpis_dict}")
            kpis = DashboardKPIs(**kpis_dict)

            # Tendências (mock ou real)
            print("🔄 Calculando tendências...")
            trends = self.repo.get_period_comparison(target_date or date.today())
            print(f"✅ Tendências calculadas: {trends}")
            for key, value in trends.items():
                setattr(kpis, key, value)

            # Top produtos
            print("🔄 Buscando top produtos...")
            top_products_data = self.repo.get_top_products()
            print(f"✅ Top produtos obtidos: {len(top_products_data)} produtos")
            top_products = [TopProduct(**p) for p in top_products_data]

            # Vendas diárias
            print("🔄 Buscando vendas diárias...")
            daily_sales_data = self.repo.get_daily_sales()
            print(f"✅ Vendas diárias obtidas: {len(daily_sales_data)} registros")
            daily_sales = [DailySales(**d) for d in daily_sales_data]

            # Alertas de estoque
            print("🔄 Buscando alertas de estoque...")
            stock_alerts_data = self.repo.get_stock_alerts()
            print(f"✅ Alertas de estoque obtidos: {len(stock_alerts_data)} alertas")
            stock_alerts = [StockAlert(**a) for a in stock_alerts_data]

            # Metas de vendas (mock)
            print("🔄 Gerando metas de vendas...")
            sales_goals = [
                SalesGoal(
                    period="monthly",
                    goal_amount=10000,
                    current_amount=kpis.today_sales,
                    achievement_percentage=50.0,
                    status="on_track",
                )
            ]

            # Performance por categoria
            print("🔄 Buscando performance por categoria...")
            category_performance_data = self.repo.get_category_performance()
            print(
                f"✅ Performance por categoria obtida: {len(category_performance_data)} categorias"
            )
            category_performance = [
                CategoryPerformance(**c) for c in category_performance_data
            ]

            # Análise por hora
            print("🔄 Buscando análise por hora...")
            hourly_analysis_data = self.repo.get_hourly_analysis(target_date)
            print(f"✅ Análise por hora obtida: {len(hourly_analysis_data)} registros")
            hourly_analysis = [HourlyAnalysis(**h) for h in hourly_analysis_data]

            print("✅ Dashboard completo gerado com sucesso!")
            return DashboardResponse(
                kpis=kpis,
                top_products=top_products,
                daily_sales=daily_sales,
                stock_alerts=stock_alerts,
                sales_goals=sales_goals,
                category_performance=category_performance,
                hourly_analysis=hourly_analysis,
            )

        except Exception as e:
            print(
                f"❌ Erro no ReportService.get_dashboard_data: {type(e).__name__}: {str(e)}"
            )
            import traceback

            traceback.print_exc()
            raise

    def get_sales_report(self, filters: SalesReportFilters) -> SalesReportResponse:
        # Dados agregados (mock ou real)
        summary = SalesReportData(
            period=filters.group_by,
            total_sales=1000.0,
            total_transactions=10,
            total_products=50,
            total_profit=200.0,
            average_ticket=100.0,
            top_payment_method="cash",
        )
        # Pontos diários
        data_points = [DailySales(**d) for d in self.repo.get_daily_sales()]
        # Top produtos
        top_products = [TopProduct(**p) for p in self.repo.get_top_products()]
        # Quebra por categoria
        category_breakdown = [
            CategoryPerformance(**c) for c in self.repo.get_category_performance()
        ]
        return SalesReportResponse(
            summary=summary,
            data_points=data_points,
            top_products=top_products,
            category_breakdown=category_breakdown,
        )
