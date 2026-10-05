@echo off
rem Abre a interface do EcoCiente. Na primeira vez cria o ambiente e o .env.
cd /d "%~dp0"
if not exist .venv (
    python -m venv .venv || goto :erro
    .venv\Scripts\python -m pip install -r requirements.txt || goto :erro
)
if not exist .env copy .env.example .env >nul
.venv\Scripts\python src\ui.py
exit /b
:erro
echo Nao foi possivel preparar o ambiente. Confira se o Python 3.12+ esta instalado e no PATH.
pause
