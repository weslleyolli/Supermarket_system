#!/usr/bin/env python3
"""
Script simples para popular dados de fornecedores usando SQL direto
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text

from app.core.config import settings


def populate_suppliers_simple():
    """Popular fornecedores usando SQL direto"""
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            print("🔄 Populando fornecedores com SQL direto...")

            # Dados dos fornecedores
            suppliers = [
                {
                    "name": "Distribuidora Central Ltda",
                    "company_name": "Central Distribuidora de Alimentos",
                    "document": "12.345.678/0001-90",
                    "email": "vendas@central.com.br",
                    "phone": "(11) 1234-5678",
                    "address": "Rua das Industrias, 123 - São Paulo, SP",
                    "contact_person": "João Silva",
                },
                {
                    "name": "FreshFruit Fornecedores",
                    "company_name": "FreshFruit Comércio de Frutas",
                    "document": "98.765.432/0001-10",
                    "email": "contato@freshfruit.com.br",
                    "phone": "(11) 9876-5432",
                    "address": "Av. dos Produtores, 456 - São Paulo, SP",
                    "contact_person": "Maria Santos",
                },
                {
                    "name": "Padaria & Cia",
                    "company_name": "Panificadora Moderna Ltda",
                    "document": "11.222.333/0001-44",
                    "email": "vendas@padariaecia.com.br",
                    "phone": "(11) 5555-1234",
                    "address": "Rua do Trigo, 789 - São Paulo, SP",
                    "contact_person": "Pedro Oliveira",
                },
                {
                    "name": "Bebidas Premium",
                    "company_name": "Premium Bebidas e Distribuição",
                    "document": "33.444.555/0001-77",
                    "email": "comercial@bebidaspremium.com.br",
                    "phone": "(11) 7777-8888",
                    "address": "Estrada das Bebidas, 321 - São Paulo, SP",
                    "contact_person": "Ana Costa",
                },
            ]

            inserted_count = 0
            for supplier in suppliers:
                # Verificar se já existe
                result = conn.execute(
                    text(
                        """
                    SELECT COUNT(*) FROM suppliers WHERE document = :document
                """
                    ),
                    {"document": supplier["document"]},
                )

                if result.fetchone()[0] == 0:
                    # Inserir novo fornecedor
                    conn.execute(
                        text(
                            """
                        INSERT INTO suppliers (name, company_name, document, email, phone, address, contact_person, is_active)
                        VALUES (:name, :company_name, :document, :email, :phone, :address, :contact_person, true)
                    """
                        ),
                        supplier,
                    )
                    inserted_count += 1
                    print(f"  ✅ Fornecedor '{supplier['name']}' inserido")
                else:
                    print(f"  ⚠️  Fornecedor '{supplier['name']}' já existe")

            conn.commit()
            print(f"\n🎉 {inserted_count} fornecedores inseridos com sucesso!")

            # Verificar quantos fornecedores existem no total
            result = conn.execute(text("SELECT COUNT(*) FROM suppliers"))
            total = result.fetchone()[0]
            print(f"📊 Total de fornecedores no banco: {total}")

    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = populate_suppliers_simple()
    if not success:
        sys.exit(1)
