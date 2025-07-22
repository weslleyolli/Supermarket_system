#!/usr/bin/env python3
"""
Teste para verificar se o erro de Foreign Key foi resolvido
Execute no WSL: python3 test_foreign_key_fix.py
"""

import os
import sys

# Adicionar o diretório atual ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


def test_foreign_key():
    try:
        print("🧪 TESTE: Verificando se Foreign Key foi resolvido...")

        # Importar configurações e modelos
        from app.core.config import settings
        from app.infrastructure.database.connection import SessionLocal, engine
        from app.infrastructure.database.models import Product, Supplier

        print("✅ Importações dos modelos: OK")

        # Criar sessão
        db = SessionLocal()

        # Testar query que usava FK
        print("🔍 Testando query com JOIN entre Product e Supplier...")

        # Query simples que usa a FK
        products_with_suppliers = (
            db.query(Product).join(Supplier, Product.supplier_id == Supplier.id).all()
        )

        print(f"✅ Query executada com sucesso!")
        print(f"📊 Encontrados {len(products_with_suppliers)} produtos com fornecedores")

        # Listar alguns produtos
        for i, product in enumerate(products_with_suppliers[:3]):
            # Buscar fornecedor manualmente por enquanto
            supplier = (
                db.query(Supplier).filter(Supplier.id == product.supplier_id).first()
            )
            supplier_name = supplier.name if supplier else "Sem fornecedor"
            print(f"  📦 {product.name} - Fornecedor: {supplier_name}")

        # Testar criação de produto com supplier_id
        print("\n🧪 Testando criação de produto com supplier_id...")

        # Buscar um fornecedor existente
        supplier = db.query(Supplier).first()
        if supplier:
            print(f"✅ Fornecedor encontrado: {supplier.name}")

            # Tentar criar um produto (só para testar, não vamos commitar)
            test_product = Product(
                name="Produto de Teste FK",
                barcode="TEST123456",
                category_id=1,
                price=10.0,
                cost_price=5.0,
                stock_quantity=100.0,
                min_stock_level=10.0,
                unit_type="un",
                requires_weighing=False,
                bulk_discount_enabled=False,
                is_active=True,
                supplier_id=supplier.id,  # Esta linha causava o erro antes
            )

            # Não vamos commitar, só testar se SQLAlchemy aceita
            db.add(test_product)
            db.flush()  # Só flush, sem commit

            print("✅ Produto de teste criado com supplier_id: OK")
            print("✅ Foreign Key funcionando corretamente!")

            # Rollback para não salvar o produto de teste
            db.rollback()
        else:
            print("⚠️  Nenhum fornecedor encontrado para teste")

        db.close()

        print("\n🎉 TESTE CONCLUÍDO: Foreign Key resolvido!")
        return True

    except Exception as e:
        print(f"❌ ERRO no teste: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_foreign_key()
    exit_code = 0 if success else 1
    sys.exit(exit_code)
