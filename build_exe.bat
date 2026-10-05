@echo off
rem Gera dist\EcoCiente.exe (um arquivo, sem console, com a logo como icone).
cd /d "%~dp0"
if not exist .venv python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt pyinstaller || goto :erro
.venv\Scripts\pyinstaller --noconfirm --onefile --noconsole --name EcoCiente ^
    --icon assets\ecociente.ico --paths src --hidden-import psycopg2 ^
    --add-data "src\ui_static;src\ui_static" --add-data "assets;assets" ^
    src\ui.py || goto :erro
if not exist dist\.env copy .env.example dist\.env >nul
echo.
echo Pronto: dist\EcoCiente.exe. O .env fica na mesma pasta do executavel.
pause
exit /b
:erro
echo Falha ao gerar o executavel.
pause
