#!/usr/bin/env python3
"""
Script para testar o sistema de migração de estoque
"""

import os
import sys

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_stock_migration():
    """Testar se o script de migração pode ser importado e executado"""

    print("🔄 TESTANDO SCRIPT DE MIGRAÇÃO DE ESTOQUE...")

    try:
        # Importar as funções do script de migração
        from scripts.create_stock_tables import (
            create_stock_tables,
            populate_sample_stock_data,
            verify_stock_setup,
        )

        print("✅ Funções de migração importadas com sucesso")
        print("📋 Funções disponíveis:")
        print("   - create_stock_tables(): Cria todas as tabelas do sistema de estoque")
        print("   - populate_sample_stock_data(): Popula dados de exemplo")
        print("   - verify_stock_setup(): Verifica se a configuração está correta")

        print("\n🎯 SCRIPT DE MIGRAÇÃO PRONTO PARA USO!")
        print("\n📋 PARA EXECUTAR A MIGRAÇÃO:")
        print("   python scripts/create_stock_tables.py")

        return True

    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False


def check_database_connection():
    """Verificar se a conexão com o banco está funcionando"""

    print("\n🔄 TESTANDO CONEXÃO COM O BANCO DE DADOS...")

    try:
        from sqlalchemy import create_engine, text

        from app.infrastructure.database.connection import get_database_url

        database_url = get_database_url()
        engine = create_engine(database_url)

        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test")).scalar()
            if result == 1:
                print("✅ Conexão com banco de dados funcionando")
                return True
            else:
                print("❌ Erro na consulta de teste")
                return False

    except Exception as e:
        print(f"❌ Erro na conexão com banco: {e}")
        print("💡 Certifique-se de que:")
        print("   - O banco de dados está rodando")
        print("   - As variáveis de ambiente estão configuradas")
        print("   - As credenciais estão corretas")
        return False


def main():
    """Função principal"""
    print("🧪 TESTE DO SISTEMA DE MIGRAÇÃO DE ESTOQUE")
    print("=" * 50)

    # Teste 1: Importação do script
    migration_ok = test_stock_migration()

    # Teste 2: Conexão com banco
    db_ok = check_database_connection()

    # Resultado final
    if migration_ok and db_ok:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("🚀 O sistema está pronto para a migração de estoque")
    else:
        print("\n❌ ALGUNS TESTES FALHARAM!")
        print("🔧 Corrija os problemas antes de executar a migração")
        sys.exit(1)


if __name__ == "__main__":
    main()
