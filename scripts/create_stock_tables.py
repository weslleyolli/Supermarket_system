"""
Script para criar as tabelas do sistema de estoque
Execute este script após configurar o banco de dados principal
"""

import os
import sys

from sqlalchemy import create_engine, text

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.connection import get_database_url


def create_stock_tables():
    """Criar tabelas do sistema de estoque"""

    print("🚀 CRIANDO TABELAS DO SISTEMA DE ESTOQUE...")

    # Conectar ao banco
    database_url = get_database_url()
    engine = create_engine(database_url)

    # SQL para criar as tabelas
    sql_commands = [
        # 1. Tabela de fornecedores
        """
        CREATE TABLE IF NOT EXISTS suppliers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            company_name VARCHAR(255),
            document VARCHAR(20) UNIQUE,
            email VARCHAR(255),
            phone VARCHAR(20),
            address TEXT,
            contact_person VARCHAR(255),
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """,
        # 2. Tabela de movimentações de estoque
        """
        CREATE TABLE IF NOT EXISTS stock_movements (
            id SERIAL PRIMARY KEY,
            product_id INTEGER NOT NULL REFERENCES products(id),
            movement_type VARCHAR(20) NOT NULL CHECK (movement_type IN ('entrada', 'saida', 'ajuste', 'perda', 'devolucao', 'transferencia')),
            quantity INTEGER NOT NULL,
            previous_quantity INTEGER NOT NULL,
            new_quantity INTEGER NOT NULL,
            unit_cost DECIMAL(10, 2),
            total_cost DECIMAL(10, 2),
            reason VARCHAR(255),
            notes TEXT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            sale_id INTEGER REFERENCES sales(id),
            supplier_id INTEGER REFERENCES suppliers(id),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """,
        # 3. Tabela de pedidos de compra
        """
        CREATE TABLE IF NOT EXISTS purchase_orders (
            id SERIAL PRIMARY KEY,
            supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
            order_number VARCHAR(50) UNIQUE NOT NULL,
            status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'delivered', 'cancelled')),
            total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
            notes TEXT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            order_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            expected_delivery TIMESTAMP WITH TIME ZONE,
            delivery_date TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """,
        # 4. Tabela de itens do pedido de compra
        """
        CREATE TABLE IF NOT EXISTS purchase_order_items (
            id SERIAL PRIMARY KEY,
            purchase_order_id INTEGER NOT NULL REFERENCES purchase_orders(id) ON DELETE CASCADE,
            product_id INTEGER NOT NULL REFERENCES products(id),
            quantity_ordered INTEGER NOT NULL,
            quantity_received INTEGER DEFAULT 0,
            unit_cost DECIMAL(10, 2) NOT NULL,
            total_cost DECIMAL(10, 2) NOT NULL
        );
        """,
        # 5. Alterar tabela de produtos para adicionar campos de estoque
        """
        ALTER TABLE products
        ADD COLUMN IF NOT EXISTS supplier_id INTEGER REFERENCES suppliers(id),
        ADD COLUMN IF NOT EXISTS cost_price DECIMAL(10, 2),
        ADD COLUMN IF NOT EXISTS profit_margin DECIMAL(5, 2),
        ADD COLUMN IF NOT EXISTS weight DECIMAL(8, 3),
        ADD COLUMN IF NOT EXISTS dimensions VARCHAR(100),
        ADD COLUMN IF NOT EXISTS location VARCHAR(100),
        ADD COLUMN IF NOT EXISTS reorder_point INTEGER,
        ADD COLUMN IF NOT EXISTS max_stock INTEGER,
        ADD COLUMN IF NOT EXISTS last_purchase_date TIMESTAMP WITH TIME ZONE,
        ADD COLUMN IF NOT EXISTS last_sale_date TIMESTAMP WITH TIME ZONE;
        """,
        # 6. Índices para performance
        """
        CREATE INDEX IF NOT EXISTS idx_stock_movements_product_id ON stock_movements(product_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_stock_movements_created_at ON stock_movements(created_at);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_stock_movements_type ON stock_movements(movement_type);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_products_supplier_id ON products(supplier_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_products_stock_quantity ON products(stock_quantity);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_products_min_stock_level ON products(min_stock_level);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_purchase_orders_supplier_id ON purchase_orders(supplier_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_purchase_orders_status ON purchase_orders(status);
        """,
        # 7. Triggers para atualizar updated_at
        """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        """,
        """
        DROP TRIGGER IF EXISTS update_suppliers_updated_at ON suppliers;
        CREATE TRIGGER update_suppliers_updated_at
            BEFORE UPDATE ON suppliers
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """,
        """
        DROP TRIGGER IF EXISTS update_purchase_orders_updated_at ON purchase_orders;
        CREATE TRIGGER update_purchase_orders_updated_at
            BEFORE UPDATE ON purchase_orders
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """,
    ]

    # Executar comandos SQL
    with engine.connect() as conn:
        for i, sql in enumerate(sql_commands, 1):
            try:
                print(f"📋 Executando comando {i}/{len(sql_commands)}...")
                # Iniciar uma nova transação para cada comando
                with conn.begin():
                    conn.execute(text(sql))
                print(f"✅ Comando {i} executado com sucesso")
            except Exception as e:
                print(f"❌ Erro no comando {i}: {e}")
                # Continuar com o próximo comando mesmo em caso de erro
                continue

    print("🎉 TABELAS DE ESTOQUE CRIADAS COM SUCESSO!")


def populate_sample_stock_data():
    """Popular dados de exemplo para o sistema de estoque"""

    print("\n📊 POPULANDO DADOS DE EXEMPLO...")

    database_url = get_database_url()
    engine = create_engine(database_url)

    # Dados de exemplo
    sample_data = [
        # Fornecedores
        """
        INSERT INTO suppliers (name, company_name, email, phone, contact_person) VALUES
        ('Distribuidora ABC', 'ABC Distribuidora Ltda', 'contato@abc.com', '(11) 1234-5678', 'João Silva'),
        ('Química Industrial', 'Química Industrial S.A.', 'vendas@quimica.com', '(11) 9876-5432', 'Maria Santos'),
        ('Cosméticos XYZ', 'XYZ Cosméticos', 'comercial@xyz.com', '(11) 5555-1234', 'Pedro Costa'),
        ('Laticínios Norte', 'Norte Laticínios Ltda', 'pedidos@norte.com', '(11) 3333-7777', 'Ana Oliveira'),
        ('Grãos do Sul', 'Sul Grãos e Cereais', 'estoque@graos.com', '(11) 2222-8888', 'Carlos Lima');
        """,
        # Atualizar produtos existentes com informações de estoque
        """
        UPDATE products SET
            supplier_id = (SELECT id FROM suppliers WHERE name = 'Distribuidora ABC' LIMIT 1),
            cost_price = 18.50,
            profit_margin = 40.00,
            weight = 5.0,
            location = 'A-01-03',
            reorder_point = 20,
            max_stock = 100,
            last_purchase_date = CURRENT_TIMESTAMP - INTERVAL '5 days'
        WHERE name LIKE '%Arroz%';
        """,
        """
        UPDATE products SET
            supplier_id = (SELECT id FROM suppliers WHERE name = 'Química Industrial' LIMIT 1),
            cost_price = 2.80,
            profit_margin = 60.00,
            weight = 0.5,
            location = 'B-02-01',
            reorder_point = 30,
            max_stock = 80,
            last_purchase_date = CURRENT_TIMESTAMP - INTERVAL '3 days'
        WHERE name LIKE '%Detergente%';
        """,
        """
        UPDATE products SET
            supplier_id = (SELECT id FROM suppliers WHERE name = 'Cosméticos XYZ' LIMIT 1),
            cost_price = 12.00,
            profit_margin = 57.50,
            weight = 0.4,
            location = 'C-01-02',
            reorder_point = 25,
            max_stock = 60,
            last_purchase_date = CURRENT_TIMESTAMP - INTERVAL '7 days'
        WHERE name LIKE '%Shampoo%';
        """,
        """
        UPDATE products SET
            supplier_id = (SELECT id FROM suppliers WHERE name = 'Laticínios Norte' LIMIT 1),
            cost_price = 4.20,
            profit_margin = 38.00,
            weight = 1.0,
            location = 'D-01-01',
            reorder_point = 40,
            max_stock = 120,
            last_purchase_date = CURRENT_TIMESTAMP - INTERVAL '1 day'
        WHERE name LIKE '%Leite%';
        """,
        # Movimentações de estoque de exemplo
        """
        INSERT INTO stock_movements (product_id, movement_type, quantity, previous_quantity, new_quantity, unit_cost, total_cost, reason, user_id, supplier_id)
        SELECT
            p.id,
            'entrada',
            50,
            p.stock_quantity - 50,
            p.stock_quantity,
            p.cost_price,
            50 * p.cost_price,
            'Entrada inicial de estoque',
            1,
            p.supplier_id
        FROM products p
        WHERE p.cost_price IS NOT NULL
        AND NOT EXISTS (
            SELECT 1 FROM stock_movements sm
            WHERE sm.product_id = p.id
            AND sm.movement_type = 'entrada'
        )
        LIMIT 5;
        """,
        # Algumas saídas de estoque (vendas)
        """
        INSERT INTO stock_movements (product_id, movement_type, quantity, previous_quantity, new_quantity, reason, user_id)
        SELECT
            p.id,
            'saida',
            CASE
                WHEN p.stock_quantity > 30 THEN 15
                WHEN p.stock_quantity > 10 THEN 5
                ELSE 2
            END,
            p.stock_quantity + CASE
                WHEN p.stock_quantity > 30 THEN 15
                WHEN p.stock_quantity > 10 THEN 5
                ELSE 2
            END,
            p.stock_quantity,
            'Venda no PDV',
            1
        FROM products p
        WHERE p.stock_quantity > 0
        AND NOT EXISTS (
            SELECT 1 FROM stock_movements sm
            WHERE sm.product_id = p.id
            AND sm.movement_type = 'saida'
        )
        LIMIT 3;
        """,
    ]

    # Executar inserções
    with engine.connect() as conn:
        for i, sql in enumerate(sample_data, 1):
            try:
                print(f"📋 Inserindo dados {i}/{len(sample_data)}...")
                # Usar transação separada para cada comando
                with conn.begin():
                    conn.execute(text(sql))
                print(f"✅ Dados {i} inseridos com sucesso")
            except Exception as e:
                print(f"❌ Erro ao inserir dados {i}: {e}")
                continue

    print("🎉 DADOS DE EXEMPLO INSERIDOS COM SUCESSO!")


def verify_stock_setup():
    """Verificar se o sistema de estoque foi configurado corretamente"""

    print("\n🔍 VERIFICANDO CONFIGURAÇÃO DO SISTEMA DE ESTOQUE...")

    database_url = get_database_url()
    engine = create_engine(database_url)

    verification_queries = [
        ("Fornecedores", "SELECT COUNT(*) FROM suppliers"),
        ("Movimentações", "SELECT COUNT(*) FROM stock_movements"),
        (
            "Produtos com fornecedor",
            "SELECT COUNT(*) FROM products WHERE supplier_id IS NOT NULL",
        ),
        (
            "Produtos com preço de custo",
            "SELECT COUNT(*) FROM products WHERE cost_price IS NOT NULL",
        ),
        (
            "Produtos com localização",
            "SELECT COUNT(*) FROM products WHERE location IS NOT NULL",
        ),
    ]

    with engine.connect() as conn:
        for name, query in verification_queries:
            try:
                result = conn.execute(text(query)).scalar()
                print(f"✅ {name}: {result}")
            except Exception as e:
                print(f"❌ Erro ao verificar {name}: {e}")

    print("\n🎯 VERIFICAÇÃO CONCLUÍDA!")


def main():
    """Função principal"""
    print("🏗️ CONFIGURAÇÃO DO SISTEMA DE ESTOQUE")
    print("=" * 50)

    try:
        # 1. Criar tabelas
        create_stock_tables()

        # 2. Popular dados de exemplo
        populate_sample_stock_data()

        # 3. Verificar configuração
        verify_stock_setup()

        print("\n🎉 SISTEMA DE ESTOQUE CONFIGURADO COM SUCESSO!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Reiniciar o servidor backend")
        print("2. Testar os endpoints de estoque")
        print("3. Verificar a interface do frontend")
        print("4. Configurar alertas de estoque")

    except Exception as e:
        print(f"\n❌ ERRO NA CONFIGURAÇÃO: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
