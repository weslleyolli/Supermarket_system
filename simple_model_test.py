#!/usr/bin/env python3
"""
Teste simples para verificar se os modelos carregam sem erros
Execute no WSL: python3 simple_model_test.py
"""

import os
import sys

# Adicionar o diretório atual ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


def test_models():
    try:
        print("🧪 TESTE SIMPLES: Carregando modelos...")

        # Importar Base primeiro
        from app.infrastructure.database.connection import SessionLocal

        # Importar modelos na ordem correta
        print("📦 Importando Customer...")
        from app.infrastructure.database.models.customer import Customer

        print("📦 Importando User...")
        from app.infrastructure.database.models.user import User

        print("📦 Importando Category...")
        from app.infrastructure.database.models.product import Category

        print("📦 Importando Supplier...")
        from app.infrastructure.database.models.stock import Supplier

        print("📦 Importando Product...")
        from app.infrastructure.database.models.product import Product

        print("📦 Importando Sale...")
        from app.infrastructure.database.models.sale import Sale, SaleItem

        print("✅ Todos os modelos carregados com sucesso!")

        # Teste simples de query
        print("\n🔍 Testando queries básicas...")
        db = SessionLocal()

        # Contar produtos
        product_count = db.query(Product).count()
        print(f"📊 Produtos no banco: {product_count}")

        # Contar fornecedores
        supplier_count = db.query(Supplier).count()
        print(f"📊 Fornecedores no banco: {supplier_count}")

        # Query simples com supplier_id
        products_with_supplier = (
            db.query(Product).filter(Product.supplier_id.isnot(None)).count()
        )
        print(f"📊 Produtos com fornecedor: {products_with_supplier}")

        # Teste de relacionamento
        print("\n🔗 Testando relacionamento Product -> Supplier...")
        try:
            # Buscar um produto que tem supplier_id
            product = db.query(Product).filter(Product.supplier_id.isnot(None)).first()
            if product:
                print(f"📦 Produto encontrado: {product.name}")
                print(f"🔗 Supplier ID: {product.supplier_id}")

                # Tentar acessar o relacionamento
                supplier = product.supplier
                if supplier:
                    print(f"✅ Relacionamento funcionando! Fornecedor: {supplier.name}")
                else:
                    print(
                        "⚠️  Relacionamento configurado mas fornecedor não encontrado"
                    )
            else:
                print("⚠️  Nenhum produto com supplier_id encontrado")
        except Exception as e:
            print(f"❌ Erro no relacionamento: {e}")

        db.close()
        print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
        return True

    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_models()
    exit_code = 0 if success else 1
    sys.exit(exit_code)
