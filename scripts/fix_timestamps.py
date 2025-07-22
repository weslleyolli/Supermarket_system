#!/usr/bin/env python3
"""
Script para corrigir valores padrão das colunas de timestamp
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text

from app.core.config import settings


def fix_timestamp_defaults():
    """Corrigir valores padrão das colunas de timestamp"""
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            print("🔄 Corrigindo valores padrão das colunas de timestamp...")

            # Corrigir tabela suppliers
            conn.execute(
                text("ALTER TABLE suppliers ALTER COLUMN created_at SET DEFAULT NOW()")
            )
            conn.execute(
                text("ALTER TABLE suppliers ALTER COLUMN updated_at SET DEFAULT NOW()")
            )
            print("  ✅ Tabela suppliers corrigida")

            # Atualizar registros existentes que tenham valores nulos
            conn.execute(
                text("UPDATE suppliers SET created_at = NOW() WHERE created_at IS NULL")
            )
            conn.execute(
                text("UPDATE suppliers SET updated_at = NOW() WHERE updated_at IS NULL")
            )
            print("  ✅ Registros existentes atualizados")

            conn.commit()
            print("✅ Valores padrão adicionados às colunas de timestamp")

    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = fix_timestamp_defaults()
    if not success:
        sys.exit(1)
