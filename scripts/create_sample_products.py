#!/usr/bin/env python3
"""
Script para criar dados de exemplo
Sistema de Gestão de Supermercado
"""

import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session

from app.application.services.product_service import ProductService
from app.infrastructure.database.connection import SessionLocal
from app.presentation.schemas.product import CategoryCreate, ProductCreate


def create_sample_data():
    """Cria dados de exemplo para teste"""
    db: Session = SessionLocal()
    product_service = ProductService(db)

    try:
        print("🏪 CRIANDO DADOS DE EXEMPLO PARA TESTE")
        print("=" * 50)

        # =====================================================================
        # CRIAR CATEGORIAS
        # =====================================================================
        print("\n📁 Criando categorias...")

        categories_data = [
            CategoryCreate(
                name="Bebidas",
                description="Refrigerantes, sucos, água mineral, energéticos",
            ),
            CategoryCreate(
                name="Laticínios", description="Leite, queijos, iogurtes, manteigas"
            ),
            CategoryCreate(
                name="Carnes e Aves",
                description="Carnes bovinas, suínas, frango, peixes",
            ),
            CategoryCreate(name="Frutas", description="Frutas frescas da estação"),
            CategoryCreate(
                name="Verduras e Legumes", description="Verduras e legumes frescos"
            ),
            CategoryCreate(name="Limpeza", description="Produtos de limpeza doméstica"),
            CategoryCreate(
                name="Higiene Pessoal",
                description="Produtos de higiene e cuidados pessoais",
            ),
            CategoryCreate(name="Padaria", description="Pães, bolos, doces da padaria"),
            CategoryCreate(
                name="Mercearia", description="Produtos secos, conservas, temperos"
            ),
            CategoryCreate(
                name="Congelados", description="Produtos congelados e sorvetes"
            ),
        ]

        created_categories = []
        for cat_data in categories_data:
            try:
                category = product_service.create_category(cat_data)
                created_categories.append(category)
                print(f"✅ {category.name}")
            except ValueError:
                print(f"⚠️  Categoria '{cat_data.name}' já existe")
                # Buscar categoria existente
                existing_cats = product_service.list_categories()
                for existing in existing_cats:
                    if existing.name == cat_data.name:
                        created_categories.append(existing)
                        break

        print(f"\n📁 Total de categorias: {len(created_categories)}")

        # =====================================================================
        # CRIAR PRODUTOS
        # =====================================================================
        print("\n📦 Criando produtos...")

        produtos_data = [
            # BEBIDAS
            ProductCreate(
                name="Coca-Cola 2L",
                description="Refrigerante Coca-Cola 2 litros",
                barcode="7891000100103",
                category_id=created_categories[0].id,
                price=8.50,
                cost_price=6.00,
                stock_quantity=48,
                min_stock_level=12,
                unit_type="unidade",
                requires_weighing=False,
                bulk_discount_enabled=True,
                bulk_min_quantity=6,
                bulk_discount_percentage=5.0,
            ),
            ProductCreate(
                name="Guaraná Antarctica 2L",
                description="Refrigerante Guaraná Antarctica 2 litros",
                barcode="7891000100110",
                category_id=created_categories[0].id,
                price=7.90,
                cost_price=5.50,
                stock_quantity=36,
                min_stock_level=10,
                bulk_discount_enabled=True,
                bulk_min_quantity=6,
                bulk_discount_percentage=5.0,
            ),
            ProductCreate(
                name="Água Mineral Crystal 500ml",
                description="Água mineral natural Crystal 500ml",
                barcode="7891000200104",
                category_id=created_categories[0].id,
                price=2.50,
                cost_price=1.80,
                stock_quantity=120,
                min_stock_level=24,
                bulk_discount_enabled=True,
                bulk_min_quantity=12,
                bulk_discount_percentage=8.0,
            ),
            ProductCreate(
                name="Suco Del Valle Laranja 1L",
                description="Suco de laranja Del Valle 1 litro",
                barcode="7891000300105",
                category_id=created_categories[0].id,
                price=6.90,
                cost_price=4.80,
                stock_quantity=24,
                min_stock_level=8,
            ),
            # ... (demais produtos conforme seu código) ...
        ]
        # ... (continuação do código para criar produtos, contadores, resumo, exemplos, etc.) ...
        created_products = []
        products_with_promotion = 0
        products_by_weight = 0
        low_stock_products = 0

        for prod_data in produtos_data:
            try:
                product = product_service.create_product(prod_data)
                created_products.append(product)
                if product.has_promotion:
                    products_with_promotion += 1
                if product.requires_weighing:
                    products_by_weight += 1
                if product.stock_quantity <= product.min_stock_level:
                    low_stock_products += 1
                type_indicator = ""
                if product.requires_weighing:
                    type_indicator += "⚖️ "
                if product.has_promotion:
                    type_indicator += f"🎁{product.bulk_discount_percentage}% "
                if product.stock_quantity <= product.min_stock_level:
                    type_indicator += "⚠️ "
                print(f"✅ {type_indicator}{product.name} - {product.barcode}")
            except ValueError as e:
                print(f"⚠️  Erro no produto '{prod_data.name}': {e}")
        print(f"\n🎉 DADOS CRIADOS COM SUCESSO!")
        print("=" * 50)
        print(f"📁 Categorias criadas: {len(created_categories)}")
        print(f"📦 Produtos criados: {len(created_products)}")
        print(f"🎁 Produtos com promoção: {products_with_promotion}")
        print(f"⚖️  Produtos por peso: {products_by_weight}")
        print(f"⚠️  Produtos com estoque baixo: {low_stock_products}")
        total_cost_value = sum(
            p.stock_quantity * p.cost_price for p in created_products
        )
        total_sale_value = sum(p.stock_quantity * p.price for p in created_products)
        print(f"\n💰 VALOR DO ESTOQUE:")
        print(f"   Custo total: R$ {total_cost_value:,.2f}")
        print(f"   Valor de venda: R$ {total_sale_value:,.2f}")
        print(f"   Margem potencial: R$ {total_sale_value - total_cost_value:,.2f}")
        print(f"\n🔍 EXEMPLOS PARA TESTE:")
        print("=" * 30)
        print("📱 Códigos de barras para testar:")
        for i, product in enumerate(created_products[:5]):
            print(f"   {product.barcode} - {product.name}")
        print(f"\n⚖️  Produtos por peso para testar balança:")
        weight_products = [p for p in created_products if p.requires_weighing][:3]
        for product in weight_products:
            print(f"   {product.barcode} - {product.name}")
        print(f"\n🎁 Produtos com promoção para testar desconto:")
        promo_products = [p for p in created_products if p.has_promotion][:3]
        for product in promo_products:
            print(
                f"   {product.barcode} - {product.name} ({product.bulk_min_quantity}+ unidades = {product.bulk_discount_percentage}% desconto)"
            )
        print(f"\n🚀 PRÓXIMOS PASSOS:")
        print("   1. uvicorn app.main:app --reload")
        print("   2. Acesse: http://localhost:8000/docs")
        print("   3. Teste os endpoints de produtos")
        print("   4. Faça login para testar autenticação")
    except Exception as e:
        print(f"❌ Erro ao criar dados: {e}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    create_sample_data()
