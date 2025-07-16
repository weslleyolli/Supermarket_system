#!/usr/bin/env python3
"""
Script atualizado para inicializar interface Streamlit
"""

import subprocess
import sys
from pathlib import Path


def main():
    print("🚀 Iniciando O Barateiro - Sistema de Supermercado")
    print("=" * 60)

    # Verificar se está no diretório correto
    if not Path("app/ui/main.py").exists():
        print("❌ Execute este script no diretório raiz do projeto")
        return

    # Verificar se Streamlit está instalado
    try:
        print("✅ Streamlit instalado")
    except ImportError:
        print("❌ Streamlit não encontrado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit"])

    # Criar diretório de configuração se não existir
    config_dir = Path("app/ui/.streamlit")
    config_dir.mkdir(parents=True, exist_ok=True)

    # Criar arquivo de configuração do Streamlit
    config_content = """[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
port = 8501
headless = false
runOnSave = true
maxUploadSize = 200

[browser]
gatherUsageStats = false
showErrorDetails = true
"""

    config_file = config_dir / "config.toml"
    with open(config_file, "w") as f:
        f.write(config_content)

    print("✅ Configurações criadas")

    # Verificar API
    try:
        import requests

        response = requests.get("http://localhost:8000/health", timeout=3)
        if response.status_code == 200:
            print("✅ API conectada e funcionando")
        else:
            print("⚠️  API respondeu mas com erro")
    except:
        print("⚠️  API não está rodando. Execute: uvicorn app.main:app --reload")

    print("🌐 Abrindo O Barateiro em: http://localhost:8501")
    print("⏹️  Para parar: Ctrl+C")
    print()

    # Executar Streamlit
    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                "app/ui/main.py",
                "--server.port=8501",
                "--server.address=0.0.0.0",
            ]
        )
    except KeyboardInterrupt:
        print("\n⏹️  O Barateiro encerrado pelo usuário")


if __name__ == "__main__":
    main()
