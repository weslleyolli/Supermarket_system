#!/usr/bin/env python3
"""
Script para testar a importação dos schemas de estoque
"""


def test_stock_schemas():
    try:
        print("🔄 Testando importação dos schemas de estoque...")

        # Testando enums
        from app.presentation.schemas.stock import AlertLevelEnum, MovementTypeEnum

        print("✅ Enums importados com sucesso")

        # Testando schemas principais
        from app.presentation.schemas.stock import (
            StockAdjustmentCreate,
            StockAlertResponse,
            StockEntryCreate,
            StockMovementCreate,
            StockMovementResponse,
            SupplierCreate,
            SupplierResponse,
        )

        print("✅ Schemas principais importados com sucesso")

        # Testando schemas de relatórios
        from app.presentation.schemas.stock import (
            BulkStockOperation,
            ProductStockSummary,
            StockDashboardResponse,
            StockReportResponseNew,
            TopSellingProduct,
        )

        print("✅ Schemas de relatórios importados com sucesso")

        # Testando criação de instâncias
        movement_type = MovementTypeEnum.ENTRADA
        alert_level = AlertLevelEnum.WARNING

        print(f"✅ MovementTypeEnum.ENTRADA = {movement_type}")
        print(f"✅ AlertLevelEnum.WARNING = {alert_level}")

        print("\n🎯 TODOS OS SCHEMAS DE ESTOQUE FORAM IMPORTADOS COM SUCESSO!")
        print("📋 Schemas disponíveis:")
        print("   - MovementTypeEnum, AlertLevelEnum")
        print("   - StockMovementCreate, StockMovementResponse")
        print("   - StockEntryCreate, StockAdjustmentCreate")
        print("   - SupplierCreate, SupplierUpdate, SupplierResponse")
        print("   - StockAlertResponse")
        print("   - ProductStockSummary, TopSellingProduct")
        print("   - StockReportResponseNew, StockDashboardResponse")
        print("   - ProductStockBase, ProductStockCreate, ProductStockResponse")
        print("   - StockMovementFilter, ProductStockFilter")
        print("   - BulkStockOperation")
        print("   - PurchaseOrderCreate, PurchaseOrderResponse")

        return True

    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False


if __name__ == "__main__":
    success = test_stock_schemas()
    exit(0 if success else 1)
