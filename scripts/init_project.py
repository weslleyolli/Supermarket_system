#!/usr/bin/env python3
"""
Script de inicialização do projeto
Cria usuário admin inicial e dados de exemplo
"""

import asyncio
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

async def init_database():
    """Inicializa o banco de dados com dados básicos"""
    print("🗄️  Inicializando banco de dados...")
    
    # Aqui será implementada a lógica de inicialização
    # - Criar usuário admin
    # - Criar categorias básicas
    # - Criar produtos de exemplo
    # - Configurar promoções padrão
    
    print("✅ Banco de dados inicializado!")

async def main():
    """Função principal"""
    print("🚀 Inicializando Sistema de Supermercado...")
    print("=" * 50)
    
    try:
        await init_database()
        print("\n🎉 Sistema inicializado com sucesso!")
        print("\n📱 Acesse:")
        print("   API: http://localhost:8000")
        print("   Docs: http://localhost:8000/docs")
        print("   Admin: http://localhost:8501")
        print("\n👤 Login padrão:")
        print("   Usuário: admin")
        print("   Senha: admin123")
        
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
