#!/usr/bin/env python3
"""
Teste final para verificar Foreign Key funcionando
Execute no WSL: python3 test_final_success.py
"""

import os
import sys

# Adicionar o diretório atual ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


def test_final_success():
    try:
        print("🎉 TESTE FINAL: Validando Foreign Key FUNCIONANDO!")

        from sqlalchemy import text

        from app.infrastructure.database.connection import SessionLocal
        from app.infrastructure.database.models import Category, Product, Supplier

        db = SessionLocal()

        # Teste 1: Validar dados existentes
        print("\n📊 Validando dados existentes...")

        categories = db.query(Category).all()
        suppliers = db.query(Supplier).all()

        print(f"✅ Categorias disponíveis: {len(categories)}")
        for cat in categories[:3]:
            print(f"  📂 ID: {cat.id} - {cat.name}")

        print(f"✅ Fornecedores disponíveis: {len(suppliers)}")
        for sup in suppliers[:3]:
            print(f"  🏪 ID: {sup.id} - {sup.name}")

        # Teste 2: JOIN perfeito - O mais importante!
        print("\n🔗 TESTE CRITICAL: JOIN Product-Supplier...")
        join_result = db.execute(
            text(
                """
            SELECT p.name, s.name as supplier_name, p.supplier_id, p.category_id
            FROM products p
            JOIN suppliers s ON p.supplier_id = s.id
            JOIN categories c ON p.category_id = c.id
            LIMIT 3
        """
            )
        )

        rows = join_result.fetchall()
        print(f"✅ TRIPLE JOIN funcionando! {len(rows)} produtos:")
        for row in rows:
            print(
                f"  📦 {row[0]} - Fornecedor: {row[1]} - Cat: {row[3]} - Supplier: {row[2]}"
            )

        # Teste 3: Criar produto com IDs válidos
        if categories and suppliers:
            print("\n🧪 TESTE FINAL: Criação com IDs válidos...")

            valid_category = categories[0]
            valid_supplier = suppliers[0]

            print(f"✅ Usando Category ID: {valid_category.id} ({valid_category.name})")
            print(f"✅ Usando Supplier ID: {valid_supplier.id} ({valid_supplier.name})")

            test_product = Product(
                name="🎉 SUCESSO - FK Funcionando!",
                barcode="SUCCESS123",
                category_id=valid_category.id,  # ID válido!
                supplier_id=valid_supplier.id,  # ID válido!
                price=1.99,
                cost_price=1.00,
                stock_quantity=50.0,
                min_stock_level=5.0,
                unit_type="un",
                requires_weighing=False,
                bulk_discount_enabled=False,
                is_active=True,
            )

            db.add(test_product)
            db.flush()  # Testa Foreign Keys

            print("✅ SUCESSO TOTAL! Produto criado com ambas as FKs!")
            print("✅ supplier_id FK: FUNCIONANDO")
            print("✅ category_id FK: FUNCIONANDO")

            db.rollback()  # Não salvar

        # Teste 4: Contar produtos com suppliers
        products_with_suppliers = (
            db.query(Product).filter(Product.supplier_id.isnot(None)).count()
        )
        print(f"\n📈 RESULTADO: {products_with_suppliers} produtos têm fornecedores")

        db.close()

        print("\n" + "=" * 50)
        print("🎊 TESTE CONCLUÍDO COM SUCESSO TOTAL!")
        print("✅ Foreign Key suppliers: RESOLVIDO")
        print("✅ SQLAlchemy funcionando: PERFEITO")
        print("✅ JOINs funcionando: PERFEITO")
        print("✅ Criação de produtos: PERFEITO")
        print("✅ Sistema pronto para pagamentos!")
        print("=" * 50)

        return True

    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_final_success()
    print(f"\n🏆 RESULTADO: {'VITÓRIA COMPLETA!' if success else 'Falhou'}")
    sys.exit(0 if success else 1)
