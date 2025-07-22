#!/usr/bin/env python3
"""
Script para atualizar valores padrão das colunas updated_at
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text

from app.core.config import settings


def update_updated_at_defaults():
    """Atualizar valores padrão da coluna updated_at"""
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            print("🔄 Atualizando valores padrão da coluna updated_at...")

            # Verificar se a coluna tem valor padrão
            result = conn.execute(
                text(
                    """
                SELECT column_default
                FROM information_schema.columns
                WHERE table_name = 'suppliers' AND column_name = 'updated_at'
            """
                )
            )
            current_default = result.fetchone()[0]
            print(f"Valor padrão atual para updated_at: {current_default}")

            if current_default != "now()":
                # Adicionar valor padrão para updated_at
                conn.execute(
                    text(
                        "ALTER TABLE suppliers ALTER COLUMN updated_at SET DEFAULT NOW()"
                    )
                )
                print("  ✅ Valor padrão NOW() adicionado para updated_at")
            else:
                print("  ✅ Valor padrão já está correto")

            conn.commit()
            print("✅ Atualização concluída")

    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = update_updated_at_defaults()
    if not success:
        sys.exit(1)
