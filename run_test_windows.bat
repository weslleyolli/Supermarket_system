@echo off
REM Script para testar o StockService no Windows

echo 🪟 EXECUTANDO TESTE NO WINDOWS...
echo ==================================

REM Navegar para o diretório do projeto
cd /d "%~dp0"

REM Verificar se Python está disponível
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado. Instale o Python primeiro.
    pause
    exit /b 1
)

REM Executar o teste
python test_stock_service_implementation.py

echo.
echo 💡 Para executar diretamente:
echo    python test_stock_service_implementation.py
pause
