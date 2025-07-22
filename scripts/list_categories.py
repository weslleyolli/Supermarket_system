#!/usr/bin/env python3
"""
Script para listar todas as categorias cadastradas
"""

import os
import sys

# Adicionar o diretório atual ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


def list_categories():
    try:
        from sqlalchemy import text

        from app.infrastructure.database.connection import SessionLocal

        db = SessionLocal()
        print("📋 CATEGORIAS CADASTRADAS:")
        print("=" * 40)
        result = db.execute(
            text(
                """
            SELECT id, name, description, is_active
            FROM categories
            ORDER BY id
        """
            )
        )
        rows = list(result)
        if not rows:
            print("Nenhuma categoria encontrada.")
        else:
            for row in rows:
                print(f"ID: {row[0]} | Nome: {row[1]} | Ativa: {row[3]}")
                if row[2]:
                    print(f"   Descrição: {row[2]}")
        db.close()
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    list_categories()
